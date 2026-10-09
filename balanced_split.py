"""Balanced Split batch synthesis and iterative classification evaluation."""

from timeit import default_timer as timer

from alloy import parse
from balanced_separator import balanced_separator
from classification import predicate_holds


def _partition(candidates, truths):
    desirable = [predicate for predicate in candidates if truths[predicate]]
    undesirable = [predicate for predicate in candidates if not truths[predicate]]
    return desirable, undesirable


def _split_score(parts):
    """Return the larger partition size, or ``None`` for a non-splitting test."""

    desirable, undesirable = parts
    if not desirable or not undesirable:
        return None
    return max(len(desirable), len(undesirable))


def balanced_split_batch(
    content,
    scope,
    trace_length=None,
    statistics=None,
    generate=balanced_separator,
    evaluate=predicate_holds,
):
    """Synthesize a complete batch with Balanced Split and cross-branch reuse.

    At each tree node, an already stored test is reused immediately if it
    achieves the information-theoretic optimum ``ceil(|C| / 2)``. Otherwise a
    MaxSAT query establishes the best feasible split. If a stored test matches
    that split, it is reused and the newly synthesized test is discarded.
    """

    collector = parse(content, trace_length=trace_length)
    predicates = list(collector.predicates)
    if len(predicates) < 2:
        if statistics is not None:
            statistics.update(
                {
                    "tree_nodes": 0,
                    "maxsat_calls": 0,
                    "ideal_reuses": 0,
                    "matched_reuses": 0,
                    "generated_tests": 0,
                }
            )
        return []

    instances = []
    truth_tables = []
    todo = [predicates]
    tree_nodes = 0
    maxsat_calls = 0
    ideal_reuses = 0
    matched_reuses = 0

    while todo:
        candidates = todo.pop()
        tree_nodes += 1
        ideal_score = (len(candidates) + 1) // 2

        reusable = []
        for index, truths in enumerate(truth_tables):
            parts = _partition(candidates, truths)
            score = _split_score(parts)
            if score is not None:
                reusable.append((score, index, parts))
        best_reusable = min(reusable, default=None, key=lambda item: (item[0], item[1]))

        if best_reusable is not None and best_reusable[0] == ideal_score:
            _score, _index, parts = best_reusable
            ideal_reuses += 1
        else:
            instance = generate(collector, candidates, scope)
            maxsat_calls += 1
            if instance is None:
                raise RuntimeError("Balanced Split synthesis returned no separating test")
            truths = {
                predicate: evaluate(collector, instance, predicate, scope)
                for predicate in predicates
            }
            generated_parts = _partition(candidates, truths)
            generated_score = _split_score(generated_parts)
            if generated_score is None:
                raise RuntimeError("Balanced Split synthesis returned a non-splitting test")

            if best_reusable is not None and best_reusable[0] < generated_score:
                raise RuntimeError(
                    "Balanced Split synthesis returned a worse split than a stored test"
                )
            if (
                generated_score != ideal_score
                and best_reusable is not None
                and best_reusable[0] == generated_score
            ):
                _score, _index, parts = best_reusable
                matched_reuses += 1
            else:
                instances.append(instance)
                truth_tables.append(truths)
                parts = generated_parts

        desirable, undesirable = parts
        if len(desirable) > 1:
            todo.append(desirable)
        if len(undesirable) > 1:
            todo.append(undesirable)

    if statistics is not None:
        statistics.update(
            {
                "tree_nodes": tree_nodes,
                "maxsat_calls": maxsat_calls,
                "ideal_reuses": ideal_reuses,
                "matched_reuses": matched_reuses,
                "generated_tests": len(instances),
            }
        )
    return instances


def iterative_classification_path_costs(
    content,
    scope,
    trace_length=None,
    generate=balanced_separator,
    evaluate=predicate_holds,
    clock=timer,
):
    """Measure every oracle path of adaptive iterative classification.

    The tree is traversed once for evaluation, but each oracle is charged only
    for generation and partitioning at nodes on its root-to-leaf path. Tests
    synthesized on other branches are unavailable. Parsing is charged once to
    every path, as it would be in an independent narrowing session.
    """

    parse_start = clock()
    collector = parse(content, trace_length=trace_length)
    parse_seconds = clock() - parse_start
    predicates = list(collector.predicates)
    path_seconds = {predicate: parse_seconds for predicate in predicates}
    classifications = {predicate: 0 for predicate in predicates}
    node_seconds = []

    if len(predicates) < 2:
        return {
            "parse_seconds": parse_seconds,
            "tree_nodes": 0,
            "tree_synthesis_seconds": parse_seconds,
            "path_synthesis_seconds": path_seconds,
            "classifications": classifications,
            "node_seconds": node_seconds,
        }

    todo = [predicates]
    while todo:
        candidates = todo.pop()
        node_start = clock()
        instance = generate(collector, candidates, scope)
        if instance is None:
            raise RuntimeError("iterative classification returned no separating test")
        truths = {
            predicate: evaluate(collector, instance, predicate, scope)
            for predicate in candidates
        }
        elapsed = clock() - node_start

        desirable, undesirable = _partition(candidates, truths)
        if not desirable or not undesirable:
            raise RuntimeError("iterative classification returned a non-splitting test")

        node_seconds.append(
            {
                "candidate_count": len(candidates),
                "seconds": elapsed,
            }
        )
        for predicate in candidates:
            path_seconds[predicate] += elapsed
            classifications[predicate] += 1

        if len(desirable) > 1:
            todo.append(desirable)
        if len(undesirable) > 1:
            todo.append(undesirable)

    return {
        "parse_seconds": parse_seconds,
        "tree_nodes": len(node_seconds),
        "tree_synthesis_seconds": parse_seconds
        + sum(node["seconds"] for node in node_seconds),
        "path_synthesis_seconds": path_seconds,
        "classifications": classifications,
        "node_seconds": node_seconds,
    }
