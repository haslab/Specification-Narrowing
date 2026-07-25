"""Run the batch comparison, scope study, and always-online comparison.

Each synthesis request runs in a separate, persistent worker process.  The
driver can therefore enforce a safety timeout on every request and kill the
worker without leaving a Python/JVM process behind. Each request constructs one
complete batch, so the timeout bounds total batch synthesis. Main-scope results
are reused by the scope and online studies, and results are written
incrementally so a long evaluation can be resumed safely.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from contextlib import redirect_stdout
from datetime import datetime, timezone
import io
import json
import math
import os
from pathlib import Path
import selectors
import statistics
import subprocess
import sys
from timeit import default_timer as timer
from typing import Optional


ALGORITHMS = ("balanced", "recursive", "exact", "enumerate")
SCOPE_STUDY_ALGORITHMS = ("balanced", "recursive", "exact")
METHOD_METADATA = {
    "balanced": {
        "display_name": "Balanced MaxSAT",
        "family": "tree-guided",
    },
    "recursive": {
        "display_name": "Recursive SAT",
        "family": "tree-guided",
    },
    "exact": {
        "display_name": "Exact MaxSAT",
        "family": "cover-based",
    },
    "enumerate": {
        "display_name": "Separation-pattern enumeration",
        "family": "cover-based",
    },
}
CURRENT_FORMAT_VERSION = 7
ALLOYMAX_VERSION = "1.0.2"
DEFAULT_ONLINE_TIMEOUT_SECONDS = 180.0
RESULT_PREFIX = "__SPEC_NARROWING_RESULT__"
ONLINE_RESULT_PREFIX = "__SPEC_NARROWING_ONLINE_RESULT__"


def method_metadata(algorithms):
    """Return JSON-friendly display metadata for the selected method IDs."""

    return {
        algorithm: dict(METHOD_METADATA[algorithm])
        for algorithm in algorithms
    }


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = fraction * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def number_stats(values) -> Optional[dict[str, float]]:
    """Return descriptive statistics in a JSON-friendly dictionary."""

    numbers = [float(value) for value in values if value is not None]
    if not numbers:
        return None
    return {
        "count": len(numbers),
        "mean": round(statistics.mean(numbers), 2),
        "median": round(statistics.median(numbers), 2),
        "stdev": round(statistics.pstdev(numbers), 2),
        "min": round(min(numbers), 2),
        "p25": round(_percentile(numbers, 0.25), 2),
        "p75": round(_percentile(numbers, 0.75), 2),
        "p95": round(_percentile(numbers, 0.95), 2),
        "max": round(max(numbers), 2),
    }


def _worker_server(algorithm: str, filename: str, scope: int) -> int:
    """Serve newline-delimited synthesis requests on stdin/stdout."""

    from balanced import balanced_test_set
    from enumeration import enumerated_test_set
    from exact import exact_test_set
    from recursive import recursive_test_set

    content = Path(filename).read_text()
    strategy = {
        "balanced": balanced_test_set,
        "exact": exact_test_set,
        "recursive": recursive_test_set,
        "enumerate": enumerated_test_set,
    }[algorithm]

    for line in sys.stdin:
        request = json.loads(line)
        if request.get("stop"):
            return 0
        messages = io.StringIO()
        algorithm_statistics = None
        try:
            start = timer()
            with redirect_stdout(messages):
                if algorithm in {"balanced", "enumerate"}:
                    algorithm_statistics = {}
                    strategy_arguments = (
                        content,
                        scope,
                        None,
                        algorithm_statistics,
                    )
                else:
                    strategy_arguments = (content, scope, None)
                instances = [
                    instance.alloy5 for instance in strategy(*strategy_arguments)
                ]
            response = {
                "status": "completed",
                "synthesis_seconds": timer() - start,
                "instances": instances,
            }
            if messages.getvalue().strip():
                response["messages"] = messages.getvalue().strip()
            if algorithm_statistics is not None:
                response[algorithm] = algorithm_statistics
        except BaseException as error:
            response = {
                "status": "error",
                "error": f"{type(error).__name__}: {error}",
            }
        print(RESULT_PREFIX + json.dumps(response), flush=True)
    return 0


def _online_worker(filename: str, scope: int) -> int:
    """Measure all oracle paths for one always-online balanced tree."""

    from balanced import online_balanced_path_costs

    try:
        result = online_balanced_path_costs(Path(filename).read_text(), scope)
        result["status"] = "completed"
    except BaseException as error:
        result = {
            "status": "error",
            "error": f"{type(error).__name__}: {error}",
        }
    print(ONLINE_RESULT_PREFIX + json.dumps(result), flush=True)
    return 0


def _run_online_problem(filename: Path, scope: int, timeout_seconds: float):
    """Run one online comparison in an isolated, time-bounded process."""

    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "_online_worker",
                str(filename),
                str(scope),
            ],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "synthesis_timeout_seconds": timeout_seconds,
        }
    for line in completed.stdout.splitlines():
        if line.startswith(ONLINE_RESULT_PREFIX):
            return json.loads(line[len(ONLINE_RESULT_PREFIX) :])
    return {
        "status": "error",
        "error": completed.stderr.strip() or "online worker returned no result",
    }


class SynthesisServer:
    """A restartable synthesis worker with a timeout for each request."""

    def __init__(self, algorithm, filename, scope, timeout_seconds):
        self.algorithm = algorithm
        self.filename = str(filename)
        self.scope = scope
        self.timeout_seconds = timeout_seconds
        self.process = None

    def start(self):
        if self.process is not None and self.process.poll() is None:
            return
        self.process = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "_worker",
                self.algorithm,
                self.filename,
                str(self.scope),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )

    def request(self, candidates=None):
        self.start()
        request = {} if candidates is None else {"candidates": candidates}
        try:
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            self.stop()
            return {"status": "error", "error": str(error)}

        deadline = timer() + self.timeout_seconds
        selector = selectors.DefaultSelector()
        selector.register(self.process.stdout, selectors.EVENT_READ)
        try:
            while True:
                remaining = deadline - timer()
                if remaining <= 0 or not selector.select(remaining):
                    self.stop()
                    return {
                        "status": "timeout",
                        "timeout_seconds": self.timeout_seconds,
                    }
                line = self.process.stdout.readline()
                if not line:
                    result = {
                        "status": "error",
                        "error": f"synthesis worker exited with {self.process.poll()}",
                    }
                    self.stop()
                    return result
                if line.startswith(RESULT_PREFIX):
                    return json.loads(line[len(RESULT_PREFIX) :])
        finally:
            selector.close()

    def stop(self):
        process = self.process
        self.process = None
        if process is None:
            return
        if process.poll() is None:
            try:
                process.stdin.write(json.dumps({"stop": True}) + "\n")
                process.stdin.flush()
                process.wait(timeout=1)
            except (BrokenPipeError, OSError, subprocess.TimeoutExpired):
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        if process.stdin is not None:
            process.stdin.close()
        if process.stdout is not None:
            process.stdout.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, _type, _value, _traceback):
        self.stop()


def fixed_classification_counts(predicates, truth_table):
    """Adaptively order a fixed suite for every possible ground truth."""

    counts = {}
    errors = {}
    for oracle in predicates:
        remaining = list(predicates)
        answered = set()
        classifications = 0
        while len(remaining) > 1:
            ranked = []
            for index, truths in enumerate(truth_table):
                if index in answered:
                    continue
                desirable = [p for p in remaining if truths[p]]
                undesirable = [p for p in remaining if not truths[p]]
                if not desirable or not undesirable:
                    continue
                ranked.append(
                    (
                        max(len(desirable), len(undesirable)),
                        -len(desirable) * len(undesirable),
                        index,
                    )
                )
            if not ranked:
                errors[oracle] = "fixed suite does not distinguish remaining candidates"
                break
            index = min(ranked)[2]
            answered.add(index)
            answer = truth_table[index][oracle]
            remaining = [p for p in remaining if truth_table[index][p] == answer]
            classifications += 1
        counts[oracle] = classifications if remaining == [oracle] else None
    return counts, errors


def evaluate_batch(
    collector,
    filename,
    algorithm,
    scope,
    timeout_seconds,
    predicate_holds,
):
    predicates = list(collector.predicates)
    with SynthesisServer(algorithm, filename, scope, timeout_seconds) as server:
        synthesis = server.request()
    result = {
        "algorithm": algorithm,
        "status": synthesis["status"],
        "synthesis_timeout_seconds": timeout_seconds,
    }
    if synthesis["status"] != "completed":
        result.update(
            {
                key: value
                for key, value in synthesis.items()
                if key not in {"status", "timeout_seconds"}
            }
        )
        result["classifications"] = {predicate: None for predicate in predicates}
        result["classification_stats"] = None
        result["completed_oracles"] = 0
        result["total_oracles"] = len(predicates)
        return result

    instances = synthesis["instances"]
    evaluation_start = timer()
    truth_table = [
        {
            predicate: predicate_holds(collector, instance, predicate, scope)
            for predicate in predicates
        }
        for instance in instances
    ]
    evaluation_before = timer() - evaluation_start
    classification_start = timer()
    counts, errors = fixed_classification_counts(predicates, truth_table)
    evaluation_during = timer() - classification_start
    result.update(
        {
            "test_suite_size": len(instances),
            "synthesis_seconds": round(synthesis["synthesis_seconds"], 2),
            "evaluation_before_classification_seconds": round(
                evaluation_before, 2
            ),
            "evaluation_during_classification_seconds": round(
                evaluation_during, 2
            ),
            "classifications": counts,
            "classification_stats": number_stats(counts.values()),
            "completed_oracles": sum(value is not None for value in counts.values()),
            "total_oracles": len(predicates),
        }
    )
    if errors:
        result["oracle_errors"] = errors
        result["status"] = "partial"
    if synthesis.get("messages"):
        result["messages"] = synthesis["messages"]
    if synthesis.get("enumeration") is not None:
        enumeration = dict(synthesis["enumeration"])
        for key in ("enumeration_seconds", "cover_seconds"):
            if enumeration.get(key) is not None:
                enumeration[key] = round(enumeration[key], 2)
        result["enumeration"] = enumeration
    if synthesis.get("balanced") is not None:
        result["balanced"] = dict(synthesis["balanced"])
    return result


def _problem_key(path: Path):
    parts = path.stem.rsplit("_", 2)
    try:
        size = int(parts[-1])
    except (ValueError, IndexError):
        size = 0
    return size, path.name


def _problem_metadata(path: Path, predicates):
    parts = path.stem.rsplit("_", 2)
    return {
        "file": path.name,
        "model": parts[0] if len(parts) == 3 else None,
        "requirement": parts[1] if len(parts) == 3 else None,
        "declared_size": int(parts[2]) if len(parts) == 3 else len(predicates),
        "candidate_count": len(predicates),
        "candidates": list(predicates),
    }


def _format_stats(stats):
    if stats is None:
        return "no completed oracles"
    return (
        f"mean {stats['mean']:.2f}, median {stats['median']:.2f}, "
        f"min {stats['min']:.2f}, p95 {stats['p95']:.2f}, "
        f"max {stats['max']:.2f}"
    )


def print_algorithm_result(key, result):
    suffix = _format_stats(result.get("classification_stats"))
    extra = ""
    if "test_suite_size" in result:
        extra = (
            f"; suite {result['test_suite_size']}; "
            f"synthesis {result['synthesis_seconds']:.2f} seconds; "
            "evaluation before/during "
            f"{result['evaluation_before_classification_seconds']:.2f}/"
            f"{result['evaluation_during_classification_seconds']:.2f} seconds"
        )
        if result.get("enumeration"):
            enumeration = result["enumeration"]
            extra += (
                f"; enumerated {enumeration['separation_patterns']} "
                "separation patterns in "
                f"{enumeration.get('enumeration_solver_calls', 'unknown')} "
                "SAT calls; "
                "enumeration/cover "
                f"{enumeration['enumeration_seconds']:.2f}/"
                f"{enumeration['cover_seconds']:.2f} seconds"
            )
        if result.get("balanced"):
            balanced = result["balanced"]
            extra += (
                f"; MaxSAT calls {balanced['maxsat_calls']}; "
                f"reuses {balanced['ideal_reuses'] + balanced['matched_reuses']}"
            )
    print(
        f"  {key:24} {result['status']:9} "
        f"{result.get('completed_oracles', 0)}/{result.get('total_oracles', 0)} "
        f"oracles; classifications {suffix}{extra}",
        flush=True,
    )


def grouped_summary(problems):
    summary = {}
    for key in ALGORITHMS:
        by_size = {}
        for problem in problems:
            size = str(problem["candidate_count"])
            result = problem["algorithms"].get(key)
            if result is None:
                continue
            bucket = by_size.setdefault(
                size,
                {
                    "problems": 0,
                    "completed_problems": 0,
                    "completed_oracles": 0,
                    "total_oracles": 0,
                    "classifications": [],
                    "test_suite_sizes": [],
                    "synthesis_seconds": [],
                    "evaluation_before_seconds": [],
                    "evaluation_during_seconds": [],
                    "enumerated_instances": [],
                    "separation_patterns": [],
                    "enumeration_solver_calls": [],
                    "enumeration_seconds": [],
                    "cover_seconds": [],
                },
            )
            bucket["problems"] += 1
            bucket["completed_problems"] += result["status"] == "completed"
            bucket["completed_oracles"] += result.get("completed_oracles", 0)
            bucket["total_oracles"] += result.get("total_oracles", 0)
            bucket["classifications"].extend(
                value
                for value in result.get("classifications", {}).values()
                if value is not None
            )
            if result.get("test_suite_size") is not None:
                bucket["test_suite_sizes"].append(result["test_suite_size"])
            if result.get("enumeration"):
                enumeration = result["enumeration"]
                bucket["enumerated_instances"].append(
                    enumeration["enumerated_instances"]
                )
                bucket["separation_patterns"].append(
                    enumeration["separation_patterns"]
                )
                if enumeration.get("enumeration_solver_calls") is not None:
                    bucket["enumeration_solver_calls"].append(
                        enumeration["enumeration_solver_calls"]
                    )
                bucket["enumeration_seconds"].append(
                    enumeration["enumeration_seconds"]
                )
                bucket["cover_seconds"].append(enumeration["cover_seconds"])
            if result.get("synthesis_seconds") is not None:
                bucket["synthesis_seconds"].append(result["synthesis_seconds"])
                bucket["evaluation_before_seconds"].append(
                    result["evaluation_before_classification_seconds"]
                )
                bucket["evaluation_during_seconds"].append(
                    result["evaluation_during_classification_seconds"]
                )
        summary[key] = {}
        for size, bucket in by_size.items():
            summary[key][size] = {
                key: value
                for key, value in bucket.items()
                if key
                not in {
                    "classifications",
                    "test_suite_sizes",
                    "synthesis_seconds",
                    "evaluation_before_seconds",
                    "evaluation_during_seconds",
                    "enumerated_instances",
                    "separation_patterns",
                    "enumeration_solver_calls",
                    "enumeration_seconds",
                    "cover_seconds",
                }
            }
            summary[key][size]["classification_stats"] = number_stats(
                bucket["classifications"]
            )
            if bucket["test_suite_sizes"]:
                summary[key][size]["test_suite_size_stats"] = number_stats(
                    bucket["test_suite_sizes"]
                )
            for values_key, stats_key in (
                ("synthesis_seconds", "synthesis_seconds_stats"),
                ("evaluation_before_seconds", "evaluation_before_seconds_stats"),
                ("evaluation_during_seconds", "evaluation_during_seconds_stats"),
                ("enumerated_instances", "enumerated_instances_stats"),
                ("separation_patterns", "separation_patterns_stats"),
                (
                    "enumeration_solver_calls",
                    "enumeration_solver_calls_stats",
                ),
                ("enumeration_seconds", "enumeration_seconds_stats"),
                ("cover_seconds", "cover_seconds_stats"),
            ):
                if bucket[values_key]:
                    summary[key][size][stats_key] = number_stats(bucket[values_key])
    return summary


def _scope_study_problem(main_problem):
    """Copy stable problem metadata without duplicating main-study results."""

    return {
        key: deepcopy(main_problem[key])
        for key in (
            "file",
            "model",
            "requirement",
            "declared_size",
            "candidate_count",
            "candidates",
        )
        if key in main_problem
    } | {"scopes": {}}


def scope_study_summary(study):
    """Summarize the scope experiment, including its paired RQ2 subset."""

    scopes = [str(scope) for scope in study["configuration"]["scopes"]]
    algorithm_keys = study["configuration"]["algorithms"]
    by_scope = {key: {} for key in algorithm_keys}
    for key in algorithm_keys:
        for scope in scopes:
            results = [
                problem.get("scopes", {}).get(scope, {}).get(key)
                for problem in study.get("problems", [])
            ]
            results = [result for result in results if result is not None]
            completed = [
                result for result in results if result.get("status") == "completed"
            ]
            by_scope[key][scope] = {
                "problems": len(results),
                "completed_problems": len(completed),
                "completed_oracles": sum(
                    result.get("completed_oracles", 0) for result in results
                ),
                "total_oracles": sum(
                    result.get("total_oracles", 0) for result in results
                ),
                "test_suite_size_stats": number_stats(
                    result.get("test_suite_size") for result in completed
                ),
                "classification_stats": number_stats(
                    classification
                    for result in completed
                    for classification in result.get("classifications", {}).values()
                    if classification is not None
                ),
                "synthesis_seconds_stats": number_stats(
                    result.get("synthesis_seconds") for result in completed
                ),
            }

    exact_key = "exact"
    paired_problems = [
        problem
        for problem in study.get("problems", [])
        if all(
            problem.get("scopes", {})
            .get(scope, {})
            .get(exact_key, {})
            .get("status")
            == "completed"
            for scope in scopes
        )
    ]
    paired_algorithms = {key: {} for key in algorithm_keys}
    for key in algorithm_keys:
        for scope in scopes:
            results = [
                problem["scopes"][scope].get(key) for problem in paired_problems
            ]
            results = [
                result
                for result in results
                if result is not None and result.get("status") == "completed"
            ]
            paired_algorithms[key][scope] = {
                "completed_problems": len(results),
                "test_suite_size_stats": number_stats(
                    result.get("test_suite_size") for result in results
                ),
                "classification_stats": number_stats(
                    classification
                    for result in results
                    for classification in result.get("classifications", {}).values()
                    if classification is not None
                ),
            }
    return {
        "by_scope": by_scope,
        "paired_exact_completed_all_scopes": {
            "problem_count": len(paired_problems),
            "files": [problem["file"] for problem in paired_problems],
            "algorithms": paired_algorithms,
        },
    }


def online_comparison_summary(document):
    """Summarize paired batch and always-online balanced synthesis costs."""

    study = document.get("online_comparison", {})
    batch_by_file = {
        problem["file"]: problem["algorithms"]["balanced"]
        for problem in document.get("problems", [])
        if problem.get("algorithms", {}).get("balanced", {}).get("status")
        == "completed"
    }
    completed = [
        result
        for result in study.get("problems", [])
        if result.get("status") == "completed" and result["file"] in batch_by_file
    ]
    if not completed:
        return {"completed_configurations": 0}

    batch_seconds = [
        batch_by_file[result["file"]]["synthesis_seconds"] for result in completed
    ]
    online_configuration_means = [
        statistics.mean(result["path_synthesis_seconds"].values())
        for result in completed
    ]
    online_paths = [
        seconds
        for result in completed
        for seconds in result["path_synthesis_seconds"].values()
    ]
    ratios = [
        online / batch
        for online, batch in zip(online_configuration_means, batch_seconds)
        if batch > 0
    ]
    paired_differences = [
        batch - online
        for batch, online in zip(batch_seconds, online_configuration_means)
    ]
    return {
        "completed_configurations": len(completed),
        "completed_oracle_paths": len(online_paths),
        "batch_synthesis_seconds": {
            "mean": statistics.mean(batch_seconds),
            "median": statistics.median(batch_seconds),
        },
        "online_mean_path_synthesis_seconds": {
            "mean_across_configurations": statistics.mean(
                online_configuration_means
            ),
            "median_across_configurations": statistics.median(
                online_configuration_means
            ),
            "path_weighted_mean": statistics.mean(online_paths),
            "path_weighted_median": statistics.median(online_paths),
        },
        "online_to_batch_ratio": {
            "mean": statistics.mean(ratios),
            "median": statistics.median(ratios),
        },
        "paired_batch_minus_online_seconds": {
            "mean": statistics.mean(paired_differences),
            "median": statistics.median(paired_differences),
            "min": min(paired_differences),
            "max": max(paired_differences),
            "batch_slower_configurations": sum(
                difference > 0 for difference in paired_differences
            ),
        },
    }


def ensure_online_comparison(document, timeout_seconds):
    """Initialize and normalize the paired always-online balanced study."""

    expected = {
        "method": "balanced",
        "scope": document["configuration"]["scope"],
        "synthesis_timeout_seconds": timeout_seconds,
        "eligible_batch_status": "completed",
        "aggregation": "mean oracle-path cost per configuration",
    }
    changed = False
    study = document.get("online_comparison")
    if study is None:
        study = {
            "configuration": expected,
            "problems": [],
        }
        document["online_comparison"] = study
        changed = True
    else:
        configuration = study.setdefault("configuration", {})
        old_timeout = configuration.pop("timeout_seconds", None)
        if old_timeout is not None:
            changed = True
        if old_timeout is not None and "synthesis_timeout_seconds" not in configuration:
            configuration["synthesis_timeout_seconds"] = old_timeout
        for key, value in expected.items():
            if configuration.get(key) != value:
                if (
                    key in {"scope", "synthesis_timeout_seconds"}
                    and configuration.get(key) is not None
                ):
                    raise ValueError(
                        "cannot resume: existing online-comparison scope or "
                        "timeout does not match the requested configuration"
                    )
                configuration[key] = value
                changed = True
        if configuration.pop("batch_results", None) is not None:
            changed = True
        if configuration.pop("problems_directory", None) is not None:
            changed = True

    summary = online_comparison_summary(document)
    if study.get("summary") != summary:
        study["summary"] = summary
        changed = True
    return changed


def ensure_scope_study(
    document,
    candidate_count,
    scopes,
    timeout_seconds,
):
    """Initialize the RQ2 scope study and reuse matching main-study results."""

    scopes = sorted(set(scopes))
    algorithms = list(SCOPE_STUDY_ALGORITHMS)
    expected = {
        "candidate_count": candidate_count,
        "scopes": scopes,
        "algorithms": algorithms,
        "method_metadata": method_metadata(algorithms),
        "synthesis_timeout_seconds": timeout_seconds,
        "alloymax_version": ALLOYMAX_VERSION,
    }
    changed = False
    study = document.get("scope_study")
    if study is None:
        study = {
            "configuration": expected,
            "problems": [],
        }
        document["scope_study"] = study
        changed = True
    else:
        study_configuration = study.setdefault("configuration", {})
        if "alloymax_version" not in study_configuration:
            study_configuration["alloymax_version"] = ALLOYMAX_VERSION
            changed = True
        if "method_metadata" not in study_configuration:
            study_configuration["method_metadata"] = method_metadata(algorithms)
            changed = True
        if study_configuration != expected:
            raise ValueError(
                "cannot resume: existing scope-study configuration does not "
                "match the requested candidate count, scopes, algorithms, "
                "timeout, or AlloyMax version"
            )

    study_by_file = {
        problem["file"]: problem for problem in study.get("problems", [])
    }
    main_scope = document.get("configuration", {}).get("scope")
    for main_problem in document.get("problems", []):
        if main_problem.get("candidate_count") != candidate_count:
            continue
        problem = study_by_file.get(main_problem["file"])
        if problem is None:
            problem = _scope_study_problem(main_problem)
            study["problems"].append(problem)
            study_by_file[main_problem["file"]] = problem
            changed = True
        if main_scope not in scopes:
            continue
        scope_results = problem["scopes"].setdefault(str(main_scope), {})
        for key in algorithms:
            main_result = main_problem.get("algorithms", {}).get(key)
            if main_result is not None and key not in scope_results:
                scope_results[key] = deepcopy(main_result)
                changed = True

    summary = scope_study_summary(study)
    if study.get("summary") != summary:
        study["summary"] = summary
        changed = True
    if document.get("format_version") != CURRENT_FORMAT_VERSION:
        document["format_version"] = CURRENT_FORMAT_VERSION
        changed = True
    return changed


def save_results(output: Path, document):
    document["updated_at"] = datetime.now(timezone.utc).isoformat()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, output)


def argument_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate balanced, recursive, exact, and enumeration-based "
            "batch construction, the scope study, and always-online balanced "
            "synthesis."
        )
    )
    parser.add_argument("--problems", type=Path, default=Path("problems"))
    parser.add_argument("--output", type=Path, default=Path("evaluation-results.json"))
    parser.add_argument("--scope", type=int, default=3)
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help=(
            "total synthesis budget for constructing one complete batch "
            "(default: 60 seconds)"
        ),
    )
    parser.add_argument("--min-size", type=int)
    parser.add_argument("--max-size", type=int)
    parser.add_argument("--limit", type=int, help="process only the first N problems")
    parser.add_argument(
        "--study",
        choices=("all", "main", "scope", "online"),
        default="all",
        help=(
            "run every study, or only the main, scope, or online comparison "
            "(default: all)"
        ),
    )
    parser.add_argument(
        "--online-timeout",
        type=float,
        default=DEFAULT_ONLINE_TIMEOUT_SECONDS,
        help=(
            "safety timeout for traversing one online balanced tree "
            f"(default: {DEFAULT_ONLINE_TIMEOUT_SECONDS:g} seconds)"
        ),
    )
    parser.add_argument("--scope-study-size", type=int, default=16)
    parser.add_argument("--scope-study-min", type=int, default=3)
    parser.add_argument("--scope-study-max", type=int, default=7)
    output_mode = parser.add_mutually_exclusive_group()
    output_mode.add_argument(
        "--resume",
        action="store_true",
        help="resume an existing output file (the default when it exists)",
    )
    output_mode.add_argument(
        "--overwrite",
        action="store_true",
        help="discard an existing output file and start a new evaluation",
    )
    return parser


def _main_paths(args):
    paths = sorted(args.problems.glob("*.als"), key=_problem_key)
    if args.min_size is not None:
        paths = [path for path in paths if _problem_key(path)[0] >= args.min_size]
    if args.max_size is not None:
        paths = [path for path in paths if _problem_key(path)[0] <= args.max_size]
    if args.limit is not None:
        paths = paths[: args.limit]
    return paths


def _scope_study_paths(args):
    paths = sorted(args.problems.glob("*.als"), key=_problem_key)
    paths = [
        path for path in paths if _problem_key(path)[0] == args.scope_study_size
    ]
    if args.limit is not None:
        paths = paths[: args.limit]
    return paths


def _new_document(args):
    return {
        "format_version": CURRENT_FORMAT_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "configuration": {
            "scope": args.scope,
            "synthesis_timeout_seconds": args.timeout,
            "problems_directory": str(args.problems),
            "algorithms": list(ALGORITHMS),
            "method_metadata": method_metadata(ALGORITHMS),
            "alloymax_version": ALLOYMAX_VERSION,
        },
        "problems": [],
    }


def _load_document(args):
    changed = False
    if args.output.exists() and not args.overwrite:
        document = json.loads(args.output.read_text())
        if document.get("format_version") != CURRENT_FORMAT_VERSION:
            raise SystemExit(
                "cannot resume: unsupported result format; use a format-"
                f"{CURRENT_FORMAT_VERSION} file or --overwrite"
            )
        configuration = document.get("configuration", {})
        if configuration.get("scope") != args.scope:
            raise SystemExit("cannot resume: output scope does not match --scope")
        if configuration.get("synthesis_timeout_seconds") != args.timeout:
            raise SystemExit("cannot resume: output timeout does not match --timeout")
        if not args.resume:
            print(f"Resuming existing results in {args.output}.", flush=True)
    else:
        document = _new_document(args)
        changed = True

    if args.study in {"all", "scope"}:
        scopes = range(args.scope_study_min, args.scope_study_max + 1)
        try:
            changed |= ensure_scope_study(
                document,
                args.scope_study_size,
                scopes,
                args.timeout,
            )
        except ValueError as error:
            raise SystemExit(str(error)) from error
    if args.study in {"all", "online"}:
        try:
            changed |= ensure_online_comparison(document, args.online_timeout)
        except ValueError as error:
            raise SystemExit(str(error)) from error

    if changed:
        document["format_version"] = CURRENT_FORMAT_VERSION
        save_results(args.output, document)
    return document


def _failed_result(algorithm, predicates, error, synthesis_timeout_seconds):
    return {
        "algorithm": algorithm,
        "status": "error",
        "error": f"{type(error).__name__}: {error}",
        "synthesis_timeout_seconds": synthesis_timeout_seconds,
        "classifications": {predicate: None for predicate in predicates},
        "classification_stats": None,
        "completed_oracles": 0,
        "total_oracles": len(predicates),
    }


def run_main_study(args, document, parse, predicate_holds):
    paths = _main_paths(args)
    existing_by_file = {
        problem["file"]: problem for problem in document["problems"]
    }
    required_keys = set(ALGORITHMS)
    pending = [
        path
        for path in paths
        if path.name not in existing_by_file
        or not required_keys.issubset(
            existing_by_file[path.name].get("algorithms", {})
        )
    ]
    print(
        f"Main comparison at scope {args.scope}: {len(pending)} problems "
        f"pending; {args.timeout:g}s synthesis timeout.",
        flush=True,
    )
    for index, path in enumerate(pending, 1):
        problem_start = timer()
        collector = parse(path.read_text())
        predicates = list(collector.predicates)
        problem = existing_by_file.get(path.name)
        if problem is None:
            problem = _problem_metadata(path, predicates)
            problem["algorithms"] = {}
            document["problems"].append(problem)
            existing_by_file[path.name] = problem
        missing_count = sum(
            algorithm not in problem["algorithms"] for algorithm in ALGORITHMS
        )
        print(
            f"[main {index}/{len(pending)}] {path.name} "
            f"({len(predicates)} candidates; {missing_count} methods pending)",
            flush=True,
        )
        for algorithm in ALGORITHMS:
            if algorithm in problem["algorithms"]:
                continue
            try:
                result = evaluate_batch(
                    collector,
                    path,
                    algorithm,
                    args.scope,
                    args.timeout,
                    predicate_holds,
                )
            except Exception as error:
                result = _failed_result(
                    algorithm, predicates, error, args.timeout
                )
            problem["algorithms"][algorithm] = result
            print_algorithm_result(algorithm, result)
        document["summary_by_candidate_count"] = grouped_summary(
            document["problems"]
        )
        save_results(args.output, document)
        print(
            f"  finished in {timer() - problem_start:.2f} seconds; "
            f"saved {args.output}",
            flush=True,
        )


def run_scope_study(args, document, parse, predicate_holds):
    ensure_scope_study(
        document,
        args.scope_study_size,
        range(args.scope_study_min, args.scope_study_max + 1),
        args.timeout,
    )
    study = document["scope_study"]
    study_by_file = {
        problem["file"]: problem for problem in study.get("problems", [])
    }
    paths = _scope_study_paths(args)
    scopes = study["configuration"]["scopes"]
    required_keys = set(study["configuration"]["algorithms"])
    pending_tasks = [
        (path, scope)
        for path in paths
        for scope in scopes
        if path.name not in study_by_file
        or not required_keys.issubset(
            study_by_file[path.name]
            .get("scopes", {})
            .get(str(scope), {})
        )
    ]
    print(
        f"RQ2 scope study for n={args.scope_study_size}, scopes "
        f"{scopes[0]}--{scopes[-1]}: {len(pending_tasks)} problem/scope "
        f"combinations pending; scope-{args.scope} main results are reused.",
        flush=True,
    )
    for index, (path, scope) in enumerate(pending_tasks, 1):
        task_start = timer()
        collector = parse(path.read_text())
        predicates = list(collector.predicates)
        problem = study_by_file.get(path.name)
        if problem is None:
            metadata = _problem_metadata(path, predicates)
            problem = _scope_study_problem(metadata)
            study["problems"].append(problem)
            study_by_file[path.name] = problem
        scope_results = problem["scopes"].setdefault(str(scope), {})
        missing = [key for key in required_keys if key not in scope_results]
        print(
            f"[scope {index}/{len(pending_tasks)}] {path.name}, scope {scope} "
            f"({len(missing)} methods pending)",
            flush=True,
        )
        for algorithm in SCOPE_STUDY_ALGORITHMS:
            if algorithm in scope_results:
                continue
            try:
                result = evaluate_batch(
                    collector,
                    path,
                    algorithm,
                    scope,
                    args.timeout,
                    predicate_holds,
                )
            except Exception as error:
                result = _failed_result(
                    algorithm, predicates, error, args.timeout
                )
            scope_results[algorithm] = result
            print_algorithm_result(algorithm, result)
        study["summary"] = scope_study_summary(study)
        save_results(args.output, document)
        print(
            f"  finished in {timer() - task_start:.2f} seconds; "
            f"saved {args.output}",
            flush=True,
        )


def run_online_study(args, document):
    """Evaluate online balanced path costs for batch-completed configurations."""

    ensure_online_comparison(document, args.online_timeout)
    study = document["online_comparison"]
    selected_paths = {path.name: path for path in _main_paths(args)}
    eligible = [
        problem
        for problem in document.get("problems", [])
        if problem["file"] in selected_paths
        and problem.get("algorithms", {}).get("balanced", {}).get("status")
        == "completed"
    ]
    existing = {
        result["file"]: result for result in study.get("problems", [])
    }
    pending = [
        problem for problem in eligible if problem["file"] not in existing
    ]
    print(
        "Always-online balanced comparison: "
        f"{len(pending)} pending of {len(eligible)} eligible; "
        f"{args.online_timeout:g}s safety timeout.",
        flush=True,
    )
    for index, problem in enumerate(pending, 1):
        result = _run_online_problem(
            selected_paths[problem["file"]],
            document["configuration"]["scope"],
            args.online_timeout,
        )
        result["file"] = problem["file"]
        result["candidate_count"] = problem["candidate_count"]
        study["problems"].append(result)
        study["summary"] = online_comparison_summary(document)
        save_results(args.output, document)
        detail = ""
        if result["status"] == "completed":
            detail = (
                "; mean path "
                f"{statistics.mean(result['path_synthesis_seconds'].values()):.2f}s"
            )
        print(
            f"[online {index}/{len(pending)}] {problem['file']}: "
            f"{result['status']}{detail}",
            flush=True,
        )
    summary = online_comparison_summary(document)
    if study.get("summary") != summary:
        study["summary"] = summary
        save_results(args.output, document)


def print_main_summary(document):
    print("\nMain summary by candidate count", flush=True)
    for key, sizes in document.get("summary_by_candidate_count", {}).items():
        print(key, flush=True)
        for size in sorted(sizes, key=int):
            row = sizes[size]
            suite = ""
            if row.get("test_suite_size_stats"):
                suite = f"; suite mean {row['test_suite_size_stats']['mean']:.2f}"
            timing = ""
            if row.get("synthesis_path_seconds_stats"):
                timing = (
                    "; mean oracle-path synthesis/evaluation "
                    f"{row['synthesis_path_seconds_stats']['mean']:.2f}/"
                    f"{row['evaluation_path_seconds_stats']['mean']:.2f} seconds"
                )
            elif row.get("synthesis_seconds_stats"):
                timing = (
                    "; mean synthesis/evaluation-before/evaluation-during "
                    f"{row['synthesis_seconds_stats']['mean']:.2f}/"
                    f"{row['evaluation_before_seconds_stats']['mean']:.2f}/"
                    f"{row['evaluation_during_seconds_stats']['mean']:.2f} seconds"
                )
            if row.get("separation_patterns_stats"):
                timing += (
                    "; separation patterns/SAT calls mean "
                    f"{row['separation_patterns_stats']['mean']:.2f}/"
                    f"{row.get('enumeration_solver_calls_stats', {}).get('mean', float('nan')):.2f}; "
                    "enumeration/cover mean "
                    f"{row['enumeration_seconds_stats']['mean']:.2f}/"
                    f"{row['cover_seconds_stats']['mean']:.2f} seconds"
                )
            print(
                f"  n={size}: {row['completed_oracles']}/{row['total_oracles']} "
                f"oracles; classifications {_format_stats(row['classification_stats'])}"
                f"{suite}{timing}",
                flush=True,
            )


def print_scope_summary(document):
    study = document.get("scope_study")
    if not study:
        return
    print("\nRQ2 scope-study summary", flush=True)
    for key, scopes in study.get("summary", {}).get("by_scope", {}).items():
        print(key, flush=True)
        for scope in sorted(scopes, key=int):
            row = scopes[scope]
            suite_stats = row.get("test_suite_size_stats")
            suite = "NA" if suite_stats is None else f"{suite_stats['mean']:.2f}"
            print(
                f"  scope={scope}: {row['completed_problems']}/{row['problems']} "
                f"problems; suite mean {suite}; classifications "
                f"{_format_stats(row.get('classification_stats'))}",
                flush=True,
            )
    paired = study.get("summary", {}).get(
        "paired_exact_completed_all_scopes", {}
    )
    print(
        "  exact paired subset completed at every scope: "
        f"{paired.get('problem_count', 0)} problems",
        flush=True,
    )


def print_online_summary(document):
    study = document.get("online_comparison")
    if not study:
        return
    summary = study.get("summary", {})
    completed = summary.get("completed_configurations", 0)
    print("\nAlways-online balanced comparison", flush=True)
    if not completed:
        print("  no completed configurations", flush=True)
        return
    batch = summary["batch_synthesis_seconds"]["median"]
    online = summary["online_mean_path_synthesis_seconds"][
        "median_across_configurations"
    ]
    print(
        f"  {completed} configurations; paired median batch/online "
        f"{batch:.2f}/{online:.2f} seconds",
        flush=True,
    )


def main(argv=None):
    args = argument_parser().parse_args(argv)
    if args.scope_study_min > args.scope_study_max:
        raise SystemExit("--scope-study-min cannot exceed --scope-study-max")
    document = _load_document(args)

    from alloy import parse
    from classification import predicate_holds

    try:
        if args.study in {"all", "main"}:
            run_main_study(args, document, parse, predicate_holds)
        if args.study in {"all", "scope"}:
            # Main scope results may have been added immediately above. Seed
            # them into the scope study before looking for missing work.
            if ensure_scope_study(
                document,
                args.scope_study_size,
                range(args.scope_study_min, args.scope_study_max + 1),
                args.timeout,
            ):
                save_results(args.output, document)
            run_scope_study(args, document, parse, predicate_holds)
        if args.study in {"all", "online"}:
            run_online_study(args, document)
    except KeyboardInterrupt:
        print("\nInterrupted; completed work has already been saved.", flush=True)
        return 130

    if args.study in {"all", "main"}:
        print_main_summary(document)
    if args.study in {"all", "scope"}:
        print_scope_summary(document)
    if args.study in {"all", "online"}:
        print_online_summary(document)
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "_worker":
        raise SystemExit(
            _worker_server(sys.argv[2], sys.argv[3], int(sys.argv[4]))
        )
    if len(sys.argv) == 4 and sys.argv[1] == "_online_worker":
        raise SystemExit(_online_worker(sys.argv[2], int(sys.argv[3])))
    raise SystemExit(main())
