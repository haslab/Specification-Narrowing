"""Recompute the paper's reported statistics from evaluation-results.json.

This module deliberately derives every value from per-problem results instead
of trusting the cached summaries in the result document.  It is imported by
``evaluation.py --paper-report`` and ``--full-report``; neither mode runs Alloy
or modifies the document. Both use the same calculations, with different
levels of presentation detail.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import math
from pathlib import Path
import statistics


METHODS = ("arbitrary-split", "balanced-split", "joint-cover", "enumerated-cover")
TREE_METHODS = METHODS[:2]
COVER_METHODS = METHODS[2:]
METHOD_ABBREVIATIONS = dict(zip(METHODS, ("AS", "BS", "JC", "EC")))
METHOD_LABELS = {
    "balanced-split": "Balanced Split",
    "arbitrary-split": "Arbitrary Split",
    "joint-cover": "Joint Cover",
    "enumerated-cover": "Enumerated Cover",
}


def binary_tree_lower_bound(candidate_count: int) -> float:
    """Minimum mean depth of a binary tree with equally weighted leaves."""

    if candidate_count <= 1:
        return 0.0
    depth = math.floor(math.log2(candidate_count))
    return depth + 2 - 2 ** (depth + 1) / candidate_count


def _mean(values):
    values = [value for value in values if value is not None]
    return statistics.mean(values) if values else None


def _median(values):
    values = [value for value in values if value is not None]
    return statistics.median(values) if values else None


def _result(problem, method):
    return problem.get("algorithms", {}).get(method, {})


def _status(result, synthesis=False):
    if synthesis:
        return result.get("synthesis_status", result.get("status", "missing"))
    return result.get("status", "missing")


def _completed(problem, method, synthesis=False):
    return _status(_result(problem, method), synthesis) == "completed"


def _joint(problems, methods, synthesis=False):
    return [
        problem
        for problem in problems
        if all(_completed(problem, method, synthesis) for method in methods)
    ]


def _classifications(result):
    return [
        value
        for value in result.get("classifications", {}).values()
        if value is not None
    ]


def _classification_mean(problems, method):
    return _mean(
        value
        for problem in problems
        for value in _classifications(_result(problem, method))
    )


def _suite_mean(problems, method):
    return _mean(_result(problem, method).get("test_suite_size") for problem in problems)


def _time_median(problems, method):
    return _median(_result(problem, method).get("synthesis_seconds") for problem in problems)


def batch_preparation_seconds(result):
    """Upfront batch synthesis time, preserving the cost of historical records.

    Current synthesis returns all candidate predictions within its measured
    runtime. Older records charged their computation separately; include that
    recorded cost when reading them, without exposing separate report columns.
    """

    synthesis = result.get("synthesis_seconds")
    if result.get("truth_vector_source") == "synthesis":
        return synthesis
    evaluation = result.get("evaluation_before_classification_seconds")
    if synthesis is None or evaluation is None:
        return None
    return synthesis + evaluation


def _path_count(problems, method):
    return sum(len(_classifications(_result(problem, method))) for problem in problems)


def _compare(left, right):
    if left < right:
        return "left"
    if left > right:
        return "right"
    return "tie"


def _paired_main(problems, left, right):
    paired = _joint(problems, (left, right))
    path_outcomes = Counter()
    configuration_outcomes = Counter()
    suite_outcomes = Counter()
    time_outcomes = Counter()
    for problem in paired:
        left_result = _result(problem, left)
        right_result = _result(problem, right)
        shared_oracles = set(left_result.get("classifications", {})) & set(
            right_result.get("classifications", {})
        )
        for oracle in shared_oracles:
            left_value = left_result["classifications"][oracle]
            right_value = right_result["classifications"][oracle]
            if left_value is not None and right_value is not None:
                path_outcomes[_compare(left_value, right_value)] += 1
        configuration_outcomes[
            _compare(
                statistics.mean(_classifications(left_result)),
                statistics.mean(_classifications(right_result)),
            )
        ] += 1
        suite_outcomes[
            _compare(left_result["test_suite_size"], right_result["test_suite_size"])
        ] += 1
        time_outcomes[
            _compare(left_result["synthesis_seconds"], right_result["synthesis_seconds"])
        ] += 1
    by_candidate_count = {}
    for candidate_count in sorted(
        {problem["candidate_count"] for problem in paired}
    ):
        subset = [
            problem
            for problem in paired
            if problem["candidate_count"] == candidate_count
        ]
        by_candidate_count[candidate_count] = {
            "configurations": len(subset),
            "oracle_paths": _path_count(subset, left),
            "classification_mean": {
                left: _classification_mean(subset, left),
                right: _classification_mean(subset, right),
            },
            "suite_mean": {
                left: _suite_mean(subset, left),
                right: _suite_mean(subset, right),
            },
            "synthesis_median": {
                left: _time_median(subset, left),
                right: _time_median(subset, right),
            },
        }
    return {
        "configurations": len(paired),
        "oracle_paths": _path_count(paired, left),
        "classification_mean": {
            left: _classification_mean(paired, left),
            right: _classification_mean(paired, right),
        },
        "suite_mean": {
            left: _suite_mean(paired, left),
            right: _suite_mean(paired, right),
        },
        "synthesis_median": {
            left: _time_median(paired, left),
            right: _time_median(paired, right),
        },
        "path_outcomes": dict(path_outcomes),
        "configuration_outcomes": dict(configuration_outcomes),
        "suite_outcomes": dict(suite_outcomes),
        "time_outcomes": dict(time_outcomes),
        "by_candidate_count": by_candidate_count,
        "files": [problem["file"] for problem in paired],
    }


def _by_candidate_count(problems, summarize):
    rows = [
        summarize(
            [problem for problem in problems if problem["candidate_count"] == size],
            size,
        )
        for size in sorted({problem["candidate_count"] for problem in problems})
    ]
    return rows + [summarize(problems, "All")]


def _minimum_cardinality(problem):
    """Use either completed cover method, checking agreement when both finish."""

    sizes = {
        _result(problem, method)["test_suite_size"]
        for method in COVER_METHODS
        if _completed(problem, method, synthesis=True)
    }
    if len(sizes) > 1:
        raise ValueError(
            f"cover methods disagree on minimum cardinality for {problem['file']}"
        )
    return next(iter(sizes), None)


def _reduction(original, reduced):
    if original in (None, 0) or reduced is None:
        return None
    return 100 * (original - reduced) / original


def _cardinality_report(problems):
    certified = {problem["file"]: _minimum_cardinality(problem) for problem in problems}

    def summarize(subset, size):
        paired = [
            problem for problem in _joint(subset, TREE_METHODS, synthesis=True)
            if certified[problem["file"]] is not None
        ]
        unreused = _mean(problem["candidate_count"] - 1 for problem in paired)
        suites = {method: _suite_mean(paired, method) for method in TREE_METHODS}
        suites["minimum"] = _mean(certified[problem["file"]] for problem in paired)
        return {
            "candidate_count": size,
            "configurations": len(paired),
            "unreused_tree_mean": unreused,
            "suite_mean": suites,
            "reduction_from_unreused_percent": {
                method: _reduction(unreused, value) for method, value in suites.items()
            },
            "minimum_reduction_from_balanced_percent": _reduction(
                suites["balanced-split"], suites["minimum"]
            ),
            "minimum_sources": dict(Counter(
                "both" if all(_completed(problem, method, synthesis=True) for method in COVER_METHODS)
                else next(method for method in COVER_METHODS if _completed(problem, method, synthesis=True))
                for problem in paired
            )),
            "files": [problem["file"] for problem in paired],
        }

    rows = _by_candidate_count(problems, summarize)
    return {"rows": rows, "summary": rows[-1]}


def _completion(problems, result_for=_result, synthesis=False):
    return {
        method: {
            "completed": sum(
                _status(result_for(problem, method), synthesis) == "completed"
                for problem in problems
            ),
            "total": len(problems),
            "statuses": dict(Counter(
                _status(result_for(problem, method), synthesis)
                for problem in problems
            )),
            "post_synthesis_errors": sum(
                _status(result_for(problem, method), True) == "completed"
                and result_for(problem, method).get("status") != "completed"
                for problem in problems
            ),
        }
        for method in METHODS
    }


def _synthesis_report(problems):
    def summarize(subset, size):
        paired = _joint(subset, METHODS, synthesis=True)
        return {
            "candidate_count": size,
            "configurations": len(subset),
            "completion": _completion(subset, synthesis=True),
            "paired_configurations": len(paired),
            "synthesis_median": {
                method: _time_median(paired, method) for method in METHODS
            },
            "synthesis_median_completed": {
                method: _time_median(_joint(subset, (method,), synthesis=True), method)
                for method in METHODS
            },
            "synthesis_maximum_completed": {
                method: max(
                    (_result(problem, method)["synthesis_seconds"]
                     for problem in _joint(subset, (method,), synthesis=True)),
                    default=None,
                )
                for method in METHODS
            },
            "paired_files": [problem["file"] for problem in paired],
        }

    rows = _by_candidate_count(problems, summarize)
    return {"rows": rows, "summary": rows[-1]}


def _sensitivity_report(
    document, temporal, trace=False, cardinality=False, methods=METHODS
):
    """Keep a fixed cohort: either minimum certificate for RQ1, all methods for RQ2."""
    study = document.get("trace_study" if trace else "scope_study", {})
    configuration = study.get("configuration", {})
    field = "trace_lengths" if trace else "scopes"
    bounds = configuration.get(field, [])
    problems = [
        problem for problem in study.get("problems", [])
        if bool(problem.get("temporal")) == temporal
    ]
    methods = (*TREE_METHODS, "minimum") if cardinality else methods

    def result_for(problem, bound, method):
        results = problem.get(field, {}).get(str(bound), {})
        if method == "minimum":
            minimum = _minimum_cardinality({
                "file": f"{problem['file']} ({field}={bound})",
                "algorithms": results,
            })
            return {} if minimum is None else {
                "status": "completed", "test_suite_size": minimum,
            }
        return results.get(method, {})

    paired = [
        problem for problem in problems
        if bounds and methods and all(
            _status(result_for(problem, bound, method), synthesis=True) == "completed"
            for bound in bounds for method in methods
        )
    ]
    rows = []
    for bound in bounds:
        row = {
            "bound": bound,
            "paired_configurations": len(paired),
            "completion": _completion(
                problems, lambda problem, method: result_for(problem, bound, method),
                synthesis=True,
            ),
            "suite_mean": {},
            "classification_mean": {},
            "synthesis_median": {},
            "suite_mean_completed": {},
            "synthesis_median_completed": {},
        }
        for method in methods:
            paired_results = [result_for(problem, bound, method) for problem in paired]
            completed = [
                result_for(problem, bound, method) for problem in problems
                if _status(result_for(problem, bound, method), synthesis=True) == "completed"
            ]
            row["suite_mean"][method] = _mean(
                result.get("test_suite_size") for result in paired_results
            )
            row["classification_mean"][method] = _mean(
                count for result in paired_results for count in _classifications(result)
            )
            row["synthesis_median"][method] = _median(
                result.get("synthesis_seconds") for result in paired_results
            )
            row["suite_mean_completed"][method] = _mean(
                result.get("test_suite_size") for result in completed
            )
            row["synthesis_median_completed"][method] = _median(
                result.get("synthesis_seconds") for result in completed
            )
        rows.append(row)
    return {
        "candidate_count": configuration.get(
            "temporal_candidate_count" if temporal and not trace else "candidate_count"
        ),
        "bound_label": "Trace length" if trace else "Scope",
        "fixed_scope": configuration.get("fixed_scope") if trace else None,
        "fixed_trace_length": configuration.get("temporal_trace_length") if temporal and not trace else None,
        "methods": methods,
        "configurations": len(problems),
        "paired_all_bounds": len(paired),
        "paired_files": [problem["file"] for problem in paired],
        "rows": rows,
    }


def _iterative_report(document, temporal, methods):
    """Pair actual iterative paths with batches; weight classifications by path."""

    problems = [
        problem for problem in document.get("problems", [])
        if bool(problem.get("temporal")) == temporal
    ]
    online_by_file = {
        result["file"]: result
        for result in document.get("online_comparison", {}).get("problems", [])
        if result.get("status") == "completed" and result.get("path_synthesis_seconds")
    }

    def summarize(subset, size):
        paired = [
            (problem, online_by_file[problem["file"]])
            for problem in _joint(subset, methods)
            if problem["file"] in online_by_file
        ]
        counts = {method: [] for method in (*methods, "iterative")}
        bounds = []
        for problem, online in paired:
            shared = set(online.get("classifications", {}))
            for method in methods:
                shared &= set(_result(problem, method).get("classifications", {}))
            for oracle in sorted(shared):
                values = {
                    method: _result(problem, method)["classifications"][oracle]
                    for method in methods
                } | {"iterative": online["classifications"][oracle]}
                if any(value is None for value in values.values()):
                    continue
                for method, value in values.items():
                    counts[method].append(value)
                bounds.append(binary_tree_lower_bound(problem["candidate_count"]))
        means = {method: _mean(values) for method, values in counts.items()}
        bound = _mean(bounds)
        timed = [
            (problem, online) for problem, online in paired
            if all(batch_preparation_seconds(_result(problem, method)) is not None
                   for method in methods)
        ]
        online_means = [
            statistics.mean(online["path_synthesis_seconds"].values())
            for _, online in timed
        ]
        batch_seconds = {
            method: [batch_preparation_seconds(_result(problem, method)) for problem, _ in timed]
            for method in methods
        }
        return {
            "candidate_count": size,
            "configurations": len(paired),
            "runtime_configurations": len(timed),
            "oracle_paths": len(bounds),
            "classification_mean": means,
            "bound": bound,
            "excess_over_bound": {
                method: None if value is None or bound is None else value - bound
                for method, value in means.items()
            },
            "difference_from_iterative": {
                method: None if means[method] is None or means["iterative"] is None
                else means[method] - means["iterative"]
                for method in methods
            },
            "batch_preparation_median": {
                method: _median(values) for method, values in batch_seconds.items()
            },
            "iterative_synthesis_median": _median(online_means),
            "paired_difference_median": {
                method: _median(batch - online for batch, online in zip(values, online_means))
                for method, values in batch_seconds.items()
            },
            "iterative_cheaper": {
                method: sum(batch > online for batch, online in zip(values, online_means))
                for method, values in batch_seconds.items()
            },
            "maximum_full_tree_seconds": max(
                (online["tree_synthesis_seconds"] for _, online in paired
                 if online.get("tree_synthesis_seconds") is not None),
                default=None,
            ),
            "files": [problem["file"] for problem, _ in paired],
        }

    rows = _by_candidate_count(problems, summarize)
    return {"methods": list(methods), "rows": rows, "summary": rows[-1]}


def _construction_details(problems):
    balanced = _joint(problems, ("balanced-split",), synthesis=True)
    details = [_result(problem, "balanced-split").get("balanced-split", {}) for problem in balanced]
    joint = {problem["file"] for problem in _joint(problems, ("joint-cover",), synthesis=True)}
    enumerated = {problem["file"] for problem in _joint(problems, ("enumerated-cover",), synthesis=True)}
    patterns = [
        _result(problem, "enumerated-cover").get("enumerated-cover", {}).get("separation_patterns")
        for problem in _joint(problems, ("enumerated-cover",), synthesis=True)
    ]
    return {
        "balanced_tree_nodes_mean": _mean(detail.get("tree_nodes") for detail in details),
        "balanced_maxsat_calls_mean": _mean(detail.get("maxsat_calls") for detail in details),
        "balanced_stored_tests_mean": _suite_mean(balanced, "balanced-split"),
        "balanced_reuses_mean": _mean(
            detail.get("ideal_reuses", 0) + detail.get("matched_reuses", 0)
            for detail in details
        ),
        "both_covers_completed": len(joint & enumerated),
        "joint_cover_only": len(joint - enumerated),
        "enumerated_cover_only": len(enumerated - joint),
        "neither_cover_completed": len(problems) - len(joint | enumerated),
        "separation_patterns_median": _median(patterns),
        "separation_patterns_maximum": max((value for value in patterns if value is not None), default=None),
    }


def build_paper_report(document):
    """Recompute paper tables and supplementary analyses under the three RQs."""

    main = document.get("problems", [])
    static = [problem for problem in main if not problem.get("temporal")]
    temporal = [problem for problem in main if problem.get("temporal")]
    scope = _sensitivity_report(document, temporal=False)
    scope["reduced_comparison"] = _sensitivity_report(
        document, temporal=False, methods=METHODS[:3]
    )
    temporal_scope = _sensitivity_report(document, temporal=True)
    trace = _sensitivity_report(document, temporal=True, trace=True)
    return {
        "format_version": document.get("format_version"),
        "updated_at": document.get("updated_at"),
        "configuration": document.get("configuration", {}),
        "legacy_runtime_measurements": any(
            result.get("synthesis_seconds") is not None
            and result.get("truth_vector_source") != "synthesis"
            for problem in main for result in problem.get("algorithms", {}).values()
        ),
        "benchmark": {
            kind: {
                "configurations": len(problems),
                "oracle_paths": sum(problem["candidate_count"] for problem in problems),
                "requirements": len({(problem.get("model"), problem.get("requirement")) for problem in problems}),
            }
            for kind, problems in (("static", static), ("temporal", temporal))
        },
        "rq1": {
            "static": _cardinality_report(static),
            "temporal": _cardinality_report(temporal),
            "static_scope": _sensitivity_report(document, temporal=False, cardinality=True),
            "temporal_trace": _sensitivity_report(document, temporal=True, trace=True, cardinality=True),
        },
        "rq2": {
            "static": _synthesis_report(static),
            "temporal": _synthesis_report(temporal),
            "static_scope": scope,
            "temporal_scope": temporal_scope,
            "temporal_trace": trace,
            "construction_details": {
                "static": _construction_details(static),
                "temporal": _construction_details(temporal),
            },
        },
        "rq3": {
            f"{kind}{suffix}": _iterative_report(document, is_temporal, methods)
            for kind, is_temporal in (("static", False), ("temporal", True))
            for suffix, methods in (("", ("balanced-split",)), ("_all_methods", METHODS))
        },
        "supplementary_pairs": {
            kind: {
                f"{left}_{right}": _paired_main(problems, left, right)
                for left, right in combinations(METHODS, 2)
            }
            for kind, problems in (("static", static), ("temporal", temporal))
        },
    }


def _fmt(value, digits=2):
    if value is None:
        return "NA"
    rounded = round(value, digits)
    return f"{0.0 if rounded == 0 else rounded:.{digits}f}"


def _table(title, headers, rows):
    print(f"\n{title}")
    strings = [[str(value) for value in row] for row in rows]
    widths = [
        max([len(header), *(len(row[index]) for row in strings)])
        for index, header in enumerate(headers)
    ]
    print(("  " + " | ".join(header.ljust(width) for header, width in zip(headers, widths))).rstrip())
    print("  " + "-+-".join("-" * width for width in widths))
    for row in strings:
        print(("  " + " | ".join(value.ljust(width) for value, width in zip(row, widths))).rstrip())


def _print_cardinality(title, report):
    _table(title, ["N", "Configs", "N-1", "Arbitrary Split", "Balanced Split", "Minimum"], [
        [row["candidate_count"], row["configurations"],
         _fmt(row["unreused_tree_mean"]) if row["candidate_count"] == "All"
         else row["candidate_count"] - 1,
         *(_fmt(row["suite_mean"][method]) for method in TREE_METHODS),
         _fmt(row["suite_mean"]["minimum"])]
        for row in report["rows"]
    ])
    summary = report["summary"]
    print(
        "  Paired subset: both tree methods and either completed cover method. "
        f"Cover certificates: both methods {summary['minimum_sources'].get('both', 0)}; "
        f"Joint Cover only {summary['minimum_sources'].get('joint-cover', 0)}; "
        f"Enumerated Cover only {summary['minimum_sources'].get('enumerated-cover', 0)}."
    )
    reductions = summary["reduction_from_unreused_percent"]
    print(
        f"  Reduction from N-1: AS {_fmt(reductions['arbitrary-split'], 1)}%, "
        f"BS {_fmt(reductions['balanced-split'], 1)}%; minimum vs BS "
        f"{_fmt(summary['minimum_reduction_from_balanced_percent'], 1)}%."
    )


def _print_sensitivity_sizes(title, study):
    methods = study["methods"]
    _table(title, [study["bound_label"], "Paired configs", *(METHOD_LABELS.get(m, "Minimum") for m in methods)], [
        [row["bound"], row["paired_configurations"], *(_fmt(row["suite_mean"].get(m)) for m in methods)]
        for row in study["rows"]
    ])
    print(
        f"  N={study['candidate_count']}; same {study['paired_all_bounds']} configurations "
        "completed by both tree methods and either cover method at every bound. "
        "Minimum uses either cover certificate, checking agreement when both finish."
    )
    if study["fixed_scope"] is not None:
        print(f"  Structural scope fixed at {study['fixed_scope']}.")
    if study["fixed_trace_length"] is not None:
        print(f"  Maximum trace length fixed at {study['fixed_trace_length']}.")


def _print_synthesis_medians(title, report):
    _table(title, ["N", "All-four paired configs", *(METHOD_LABELS[m] for m in METHODS)], [
        [row["candidate_count"], row["paired_configurations"], *(_fmt(row["synthesis_median"][m]) for m in METHODS)]
        for row in report["rows"]
    ])
    print("  Median seconds on configurations completed by all four methods at each N.")


def _print_success_medians(title, report):
    _table(title, ["N", "Configs", *(METHOD_LABELS[m] for m in METHODS)], [
        [row["candidate_count"], row["configurations"], *(
            f"{_fmt(row['synthesis_median_completed'][m])} "
            f"({row['completion'][m]['completed']}/{row['completion'][m]['total']})"
            for m in METHODS
        )]
        for row in report["rows"]
    ])
    print(
        "  Cells show median seconds (completed/total); "
        "each method uses its own successful runs."
    )


def _explain_empty_sensitivity(title, study):
    if study["paired_all_bounds"] or not study["rows"]:
        return
    empty = [
        f"{METHOD_ABBREVIATIONS[m]} at {study['bound_label'].lower()} {row['bound']}"
        for row in study["rows"] for m in study["methods"]
        if row["completion"][m]["completed"] == 0
        and not row["completion"][m]["statuses"].get("missing")
    ]
    reason = "; zero completions for " + ", ".join(empty) if empty else ""
    print(f"\n{title.title()}: no common completed subset for all four methods across all bounds{reason}.")
    missing = [
        f"{METHOD_ABBREVIATIONS[m]} at {study['bound_label'].lower()} {row['bound']} "
        f"({row['completion'][m]['statuses']['missing']}/{study['configurations']})"
        for row in study["rows"] for m in study["methods"]
        if row["completion"][m]["statuses"].get("missing")
    ]
    if missing:
        print("  Missing measurements: " + ", ".join(missing) + ".")


def _print_reduced_sensitivity(title, study):
    reduced = study.get("reduced_comparison")
    if study["paired_all_bounds"] or not reduced or not reduced["paired_all_bounds"]:
        return
    print(
        "  For a paired scope comparison, the following additional table excludes EC. "
        "Its medians use the same configurations completed by AS, BS, and JC at every bound."
    )
    _table(f"Additional table: {title}, paired synthesis medians excluding EC (s)",
           [study["bound_label"], "Paired configs", *(METHOD_ABBREVIATIONS[m] for m in reduced["methods"])], [
        [row["bound"], row["paired_configurations"], *(_fmt(row["synthesis_median"][m]) for m in reduced["methods"])]
        for row in reduced["rows"]
    ])


def _print_sensitivity_costs(title, study):
    methods = study["methods"]
    _explain_empty_sensitivity(title, study)
    _table(f"Additional table: {title}, paired synthesis medians (s)",
           [study["bound_label"], "Paired configs", *(METHOD_LABELS[m] for m in methods)], [
        [row["bound"], row["paired_configurations"], *(_fmt(row["synthesis_median"].get(m)) for m in methods)]
        for row in study["rows"]
    ])
    print(
        f"  N={study['candidate_count']}; same completed subset at every bound."
    )
    if study["fixed_scope"] is not None:
        print(f"  Structural scope fixed at {study['fixed_scope']}.")
    if study["fixed_trace_length"] is not None:
        print(f"  Maximum trace length fixed at {study['fixed_trace_length']}.")
    if study["rows"] and not study["paired_all_bounds"]:
        print("  No common completed subset across all bounds; paired sizes and times are NA.")
    _table(f"Additional table: {title}, completion and success-only diagnostics",
           [study["bound_label"], "Method", "Synthesized/total", "Timeout", "Error", "Partial", "Missing", "Mean size", "Median s"], [
        [row["bound"], METHOD_LABELS[m],
         f"{row['completion'][m]['completed']}/{row['completion'][m]['total']}",
         *(row["completion"][m]["statuses"].get(status, 0) for status in ("timeout", "error", "partial", "missing")),
         _fmt(row["suite_mean_completed"].get(m)), _fmt(row["synthesis_median_completed"].get(m))]
        for row in study["rows"] for m in methods
    ])
    print("  Diagnostic sizes and times use each method's own completed subset at each bound.")
    _print_reduced_sensitivity(title, study)


def _print_iterative(title, report):
    methods = report["methods"]
    _table(f"Additional table: {title}, classifications", [
        "N", "Configs", "Paths", "Bound", *(METHOD_ABBREVIATIONS[m] for m in methods), "Iterative"
    ], [
        [row["candidate_count"], row["configurations"], row["oracle_paths"], _fmt(row["bound"], 6),
         *(_fmt(row["classification_mean"][m], 6) for m in methods),
         _fmt(row["classification_mean"]["iterative"], 6)]
        for row in report["rows"]
    ])
    _table(f"Additional table: {title}, synthesis time (s)", [
        "N", "Configs", *(METHOD_ABBREVIATIONS[m] for m in methods), "Iterative",
        *(f"Delta {METHOD_ABBREVIATIONS[m]}" for m in methods)
    ], [
        [row["candidate_count"], row["runtime_configurations"],
         *(_fmt(row["batch_preparation_median"][m]) for m in methods),
         _fmt(row["iterative_synthesis_median"]),
         *(_fmt(row["paired_difference_median"][m]) for m in methods)]
        for row in report["rows"]
    ])
    summary = report["summary"]
    _table(f"Additional table: {title}, aggregate differences", [
        "Method", "Classifications minus iterative", "Classifications minus bound", "Iterative cheaper configs"
    ], [
        [METHOD_LABELS[m], _fmt(summary["difference_from_iterative"][m], 6),
         _fmt(summary["excess_over_bound"][m], 6),
         f"{summary['iterative_cheaper'][m]}/{summary['runtime_configurations']}"]
        for m in methods
    ])
    print(
        "  Classification means and bounds weight shared oracle paths equally. "
        "Batch times cover upfront synthesis of the complete suite; iterative times "
        "are cumulative synthesis along oracle paths, averaged within each configuration before taking medians; "
        "Delta columns are medians of paired batch-minus-iterative differences."
    )
    print("  Runtime comparisons require recorded batch synthesis time for every method shown; review simulation is excluded.")


def _print_header(report, source, title):
    print(f"{title} (recomputed from raw per-problem entries)")
    print("Display rounding: Python round-to-nearest; NA means an unavailable statistic or an empty comparison subset.")
    if source is not None:
        print(f"Source: {source}")
    print(f"Format version: {report['format_version']}; updated: {report['updated_at'] or 'unknown'}")
    if report["legacy_runtime_measurements"]:
        print("Runtime provenance: these measurements precede the truth-vector optimization; a fresh run is needed to assess the current implementation.")
    for kind, benchmark in report["benchmark"].items():
        print(
            f"{kind.title()} benchmark: {benchmark['configurations']} configurations, "
            f"{benchmark['oracle_paths']} oracle paths, "
            f"{benchmark['requirements']} requirements"
        )
    configuration = report["configuration"]
    print(
        f"Default bounds: structural scope {configuration.get('scope')}, "
        f"maximum trace length {configuration.get('temporal_trace_length')}; "
        f"batch synthesis budget {_fmt(configuration.get('synthesis_timeout_seconds'), 0)} s"
    )
    print("Methods: AS = Arbitrary Split; BS = Balanced Split; JC = Joint Cover; EC = Enumerated Cover.")


def _completion_row(row, label):
    return [label, row["configurations"], *(row["completion"][m]["completed"] for m in METHODS)]


def _print_paper_synthesis_table(rq2):
    static = rq2["static"]
    temporal = rq2["temporal"]
    _table("TABLE 4 (paper: tab:synthesis-cost): completion and common static synthesis medians", [
        "N/benchmark", "Configs", *(METHOD_LABELS[m] for m in METHODS)
    ], [
        *(_completion_row(row, row["candidate_count"]) for row in static["rows"][:-1]),
        _completion_row(static["summary"], "Static total"),
        _completion_row(temporal["summary"], "Temporal total"),
        ["Static median (s)", static["summary"]["paired_configurations"], *(
            _fmt(static["summary"]["synthesis_median"][m]) for m in METHODS
        )],
    ])
    print("  Completion uses every configuration; static medians use the same all-four completed subset.")


def _print_temporal_completion(report):
    _table("Additional table: temporal replication completion by candidate count", [
        "N", "Configs", *(METHOD_LABELS[m] for m in METHODS)
    ], [_completion_row(row, row["candidate_count"]) for row in report["rows"]])


def _print_sensitivity_summary(title, study):
    """Show every bound while keeping detailed failure diagnostics in the full report."""

    methods = study["methods"]
    paired = study["paired_all_bounds"]
    _explain_empty_sensitivity(title, study)
    if paired:
        _table(f"Additional table: {title}, synthesis seconds (completed/total)", [
            study["bound_label"], "Paired configs", *(METHOD_ABBREVIATIONS[m] for m in methods)
        ], [
            [row["bound"], row["paired_configurations"], *(
                f"{_fmt(row['synthesis_median'][m])} "
                f"({row['completion'][m]['completed']}/{row['completion'][m]['total']})"
                for m in methods
            )]
            for row in study["rows"]
        ])
        print(
            f"  N={study['candidate_count']}; median seconds use the same {paired} "
            f"completed configurations at every bound. Completion counts use all {study['configurations']} configurations."
        )
    else:
        _table(f"Additional table: {title}, completed-run synthesis seconds (completed/total)", [
            study["bound_label"], *(METHOD_ABBREVIATIONS[m] for m in methods)
        ], [
            [row["bound"], *(
                f"{_fmt(row['synthesis_median_completed'][m])} "
                f"({row['completion'][m]['completed']}/{row['completion'][m]['total']})"
                for m in methods
            )]
            for row in study["rows"]
        ])
        print(
            f"  N={study['candidate_count']}; medians use each method's own completed runs at each bound, "
            "so their subsets can differ. These are not paired timing comparisons."
        )
    if study["fixed_scope"] is not None:
        print(f"  Structural scope fixed at {study['fixed_scope']}.")
    if study["fixed_trace_length"] is not None:
        print(f"  Maximum trace length fixed at {study['fixed_trace_length']}.")
    _print_reduced_sensitivity(title, study)


def print_paper_report(document, source: Path | None = None):
    """Print the two paper tables and a compact set of supporting summaries."""

    report = build_paper_report(document)
    _print_header(report, source, "Paper results report")

    print("\nRQ1: Batch Cardinality")
    _print_cardinality("TABLE 3 (paper: tab:batch-cardinality): mean batch cardinality, static", report["rq1"]["static"])
    _print_cardinality("Additional table: temporal replication batch cardinality", report["rq1"]["temporal"])
    _print_sensitivity_sizes(
        "Additional table: static scope sensitivity, mean batch cardinality",
        report["rq1"]["static_scope"],
    )
    _print_sensitivity_sizes(
        "Additional table: temporal trace-length sensitivity, mean batch cardinality",
        report["rq1"]["temporal_trace"],
    )

    print("\nRQ2: Synthesis Cost and Scalability")
    print("Completion and paired times concern batch synthesis.")
    rq2 = report["rq2"]
    _print_paper_synthesis_table(rq2)
    _print_temporal_completion(rq2["temporal"])
    for key, title in (
        ("static_scope", "static scope sensitivity"),
        ("temporal_trace", "temporal trace-length sensitivity"),
        ("temporal_scope", "temporal structural-scope sensitivity"),
    ):
        _print_sensitivity_summary(title, rq2[key])
    details = rq2["construction_details"]["static"]
    print(
        "  Enumerated Cover divisions on completed static runs, median/maximum: "
        f"{_fmt(details['separation_patterns_median'], 0)}/"
        f"{_fmt(details['separation_patterns_maximum'], 0)}."
    )
    maximum = max(
        (rq2[kind]["summary"]["synthesis_maximum_completed"]["arbitrary-split"]
         for kind in ("static", "temporal")
         if rq2[kind]["summary"]["synthesis_maximum_completed"]["arbitrary-split"] is not None),
        default=None,
    )
    print(f"  Arbitrary Split maximum completed synthesis time: {_fmt(maximum)} s.")
    temporal_scope = rq2["temporal_scope"]
    if temporal_scope["rows"]:
        timeouts = sum(row["completion"][m]["statuses"].get("timeout", 0)
                       for row in temporal_scope["rows"] for m in temporal_scope["methods"])
        errors = sum(row["completion"][m]["statuses"].get("error", 0)
                     for row in temporal_scope["rows"] for m in temporal_scope["methods"])
        print(
            f"  Temporal structural-scope study: {temporal_scope['paired_all_bounds']} "
            f"common configurations across all bounds; synthesis timeouts: {timeouts}; synthesis errors: {errors}."
        )

    print("\nRQ3: Adaptive Iterative Classification")
    comparisons = (
        ("Static BS", report["rq3"]["static"]["summary"]),
        ("Static all four", report["rq3"]["static_all_methods"]["summary"]),
        ("Temporal BS", report["rq3"]["temporal"]["summary"]),
    )
    _table("Additional table: paired classification effort", [
        "Subset", "Configs", "Paths", "Bound", *(METHOD_ABBREVIATIONS[m] for m in METHODS), "Iterative"
    ], [
        [label, row["configurations"], row["oracle_paths"], _fmt(row["bound"], 6),
         *(_fmt(row["classification_mean"][m], 6) if m in row["classification_mean"] else "--" for m in METHODS),
         _fmt(row["classification_mean"]["iterative"], 6)]
        for label, row in comparisons
    ])
    print("  Path-weighted means; -- marks a batch method outside the comparison subset.")
    _table("Additional table: paired synthesis time, median seconds", [
        "Benchmark", "Configs", "Balanced Split", "Iterative", "Paired increase"
    ], [
        [kind.title(), row["runtime_configurations"],
         _fmt(row["batch_preparation_median"]["balanced-split"]),
         _fmt(row["iterative_synthesis_median"]), _fmt(row["paired_difference_median"]["balanced-split"])]
        for kind in ("static", "temporal") for row in [report["rq3"][kind]["summary"]]
    ])
    print("  Batch times cover upfront synthesis of the complete suite. Iterative times are cumulative synthesis along oracle paths, including generation and partitioning, averaged within each configuration; increases are medians of paired differences. Review simulation is excluded.")
    print(
        "  Static BS batch classification excess over the lower bound: "
        f"{_fmt(report['rq3']['static']['summary']['excess_over_bound']['balanced-split'], 4)}."
    )
    print("\nUse --full-report for per-candidate tables, failure diagnostics, and all pairwise comparisons.")
    return report


def print_full_report(document, source: Path | None = None):
    """Print all paper results, detailed supplementary tables, and diagnostics."""

    report = build_paper_report(document)
    _print_header(report, source, "Full results report")

    print("\nRQ1: Batch Cardinality")
    _print_cardinality("TABLE 3 (paper: tab:batch-cardinality): mean batch cardinality, static", report["rq1"]["static"])
    _print_cardinality("Additional table: temporal replication batch cardinality", report["rq1"]["temporal"])
    _print_sensitivity_sizes("Additional table: static scope sensitivity, mean batch cardinality", report["rq1"]["static_scope"])
    _print_sensitivity_sizes(
        "Additional table: temporal trace-length sensitivity, mean batch cardinality",
        report["rq1"]["temporal_trace"],
    )

    print("\nRQ2: Synthesis Cost and Scalability")
    print("Completion and paired times concern batch synthesis.")
    rq2 = report["rq2"]
    static = rq2["static"]
    temporal = rq2["temporal"]
    _print_paper_synthesis_table(rq2)
    _print_synthesis_medians("Additional table: static synthesis medians by candidate count (s)", static)
    _print_temporal_completion(temporal)
    _print_synthesis_medians(
        "Additional table: temporal replication synthesis medians by candidate count (s)", temporal
    )
    for kind, study in (("static", static), ("temporal", temporal)):
        _print_success_medians(
            f"Additional table: {kind} synthesis by candidate count, success-only diagnostics",
            study,
        )
    _table("Additional table: default-bound completion and success-only diagnostics", [
        "Benchmark", "Method", "Completed/total", "Timeout", "Error", "Partial", "Missing", "Median s", "Maximum s"
    ], [
        [kind, METHOD_LABELS[m], f"{study['summary']['completion'][m]['completed']}/{study['summary']['configurations']}",
         *(study["summary"]["completion"][m]["statuses"].get(status, 0) for status in ("timeout", "error", "partial", "missing")),
         _fmt(study["summary"]["synthesis_median_completed"][m]),
         _fmt(study["summary"]["synthesis_maximum_completed"][m])]
        for kind, study in (("Static", static), ("Temporal", temporal)) for m in METHODS
    ])
    print("  Diagnostic medians and maxima use each method's own completed subset.")
    construction_measures = (
        ("balanced_tree_nodes_mean", "Balanced Split tree nodes (mean)", 2),
        ("balanced_maxsat_calls_mean", "Balanced Split MaxSAT calls (mean)", 2),
        ("balanced_stored_tests_mean", "Balanced Split stored tests (mean)", 2),
        ("balanced_reuses_mean", "Balanced Split reuses (mean)", 2),
        ("both_covers_completed", "Both covers completed (configs)", 0),
        ("joint_cover_only", "Only Joint Cover completed (configs)", 0),
        ("enumerated_cover_only", "Only Enumerated Cover completed (configs)", 0),
        ("neither_cover_completed", "Neither cover completed (configs)", 0),
        ("separation_patterns_median", "Enumerated Cover divisions (median)", 0),
        ("separation_patterns_maximum", "Enumerated Cover divisions (maximum)", 0),
    )
    _table("Additional table: construction and cover diagnostics", ["Measure", "Static", "Temporal"], [
        [label, *(_fmt(rq2["construction_details"][kind][key], digits) for kind in ("static", "temporal"))]
        for key, label, digits in construction_measures
    ])
    for key, title in (
        ("static_scope", "static scope sensitivity"),
        ("temporal_trace", "temporal trace-length sensitivity"),
        ("temporal_scope", "temporal structural-scope sensitivity"),
    ):
        _print_sensitivity_costs(title, rq2[key])

    print("\nRQ3: Adaptive Iterative Classification")
    for key, title in (
        ("static", "static Balanced Split vs iterative"),
        ("static_all_methods", "static all-four batches vs iterative"),
        ("temporal", "temporal Balanced Split vs iterative"),
        ("temporal_all_methods", "temporal all-four batches vs iterative"),
    ):
        _print_iterative(title, report["rq3"][key])
    online_configuration = document.get("online_comparison", {}).get("configuration", {})
    print(
        "  Iterative traversal safety timeout: "
        f"{_fmt(online_configuration.get('synthesis_timeout_seconds'), 0)} s; "
        "maximum completed full-tree traversal (static/temporal): "
        f"{_fmt(report['rq3']['static']['summary']['maximum_full_tree_seconds'])}/"
        f"{_fmt(report['rq3']['temporal']['summary']['maximum_full_tree_seconds'])} s. "
        "Individual oracle costs include only their own paths through this tree."
    )

    print("\nSupplementary pairwise comparisons")
    for kind, pairs in report["supplementary_pairs"].items():
        _table(f"Additional table: {kind} pairwise completed subsets", [
            "Left / right", "Configs", "Paths", "Mean batch L/R", "Median seconds L/R", "Mean class L/R"
        ], [
            [f"{METHOD_LABELS[left]} / {METHOD_LABELS[right]}", pair["configurations"], pair["oracle_paths"],
             "/".join(_fmt(pair["suite_mean"][m]) for m in (left, right)),
             "/".join(_fmt(pair["synthesis_median"][m]) for m in (left, right)),
             "/".join(_fmt(pair["classification_mean"][m], 6) for m in (left, right))]
            for name, pair in pairs.items() for left, right in [name.split("_", 1)]
        ])
        _table(f"Additional table: {kind} pairwise outcomes (left smaller / tie / right smaller)", [
            "Left / right", "Batch size", "Synthesis time", "Class paths", "Mean class per config"
        ], [
            [f"{METHOD_LABELS[left]} / {METHOD_LABELS[right]}",
             *("/".join(str(pair[field].get(outcome, 0)) for outcome in ("left", "tie", "right"))
               for field in ("suite_outcomes", "time_outcomes", "path_outcomes", "configuration_outcomes"))]
            for name, pair in pairs.items() for left, right in [name.split("_", 1)]
        ])
    return report
