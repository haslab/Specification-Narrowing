"""Explicit separation-pattern enumeration followed by minimum test cover."""

from itertools import combinations
from timeit import default_timer as timer

from alloy import (
    build_instance,
    command_scope,
    int_bitwidth,
    parse,
    requires_trace_length,
)

import jpype
import jpype.imports

if not jpype.isJVMStarted():
    jpype.startJVM(classpath=["AlloyMax-1.0.2.jar"])

from edu.mit.csail.sdg.parser import CompUtil
from edu.mit.csail.sdg.translator import A4Options, TranslateAlloyToKodkod


def _instance_from_solution(collector, world, solution):
    value = {}
    for signature in collector.signatures:
        tuples = solution.eval(
            CompUtil.parseOneExpression_fromString(world, signature)
        )
        value[signature] = [
            [tuple_.atom(index) for index in range(tuple_.arity())]
            for tuple_ in tuples
        ]
    for field in collector.fields:
        tuples = solution.eval(
            CompUtil.parseOneExpression_fromString(world, field)
        )
        value[field] = [
            [tuple_.atom(index) for index in range(tuple_.arity())]
            for tuple_ in tuples
        ]
    return build_instance(collector, value)


def _coverage_mask(truths, pair_bits):
    mask = 0
    for (left, right), bit in pair_bits.items():
        if truths[left] != truths[right]:
            mask |= bit
    return mask


def _nontrivial_pattern_constraint(predicates):
    """Require some candidate to disagree with the first candidate."""

    first = predicates[0]
    return "(" + " or ".join(
        f"not ({first} iff {predicate})" for predicate in predicates[1:]
    ) + ")"


def _pattern_constraint(predicates, truths):
    """Describe a candidate bipartition, identifying complementary vectors."""

    first = predicates[0]
    first_truth = truths[0]
    terms = []
    for predicate, truth in zip(predicates[1:], truths[1:]):
        equivalent = f"({first} iff {predicate})"
        terms.append(equivalent if truth == first_truth else f"not {equivalent}")
    return "(" + " and ".join(terms) + ")"


def _pattern_analysis(collector, scope, predicates, blocked_patterns):
    constraints = [_nontrivial_pattern_constraint(predicates)]
    constraints.extend(f"not {pattern}" for pattern in blocked_patterns)
    command = "run {\n\t" + "\n\tand ".join(constraints) + "\n} "
    return command + command_scope(collector, scope) + "\n" + collector.content


def minimum_test_cover(coverage_masks, pair_count):
    """Select a minimum family of explicit tests using AlloyMax."""

    if pair_count == 0:
        return []
    full_coverage = (1 << pair_count) - 1
    union = 0
    for mask in coverage_masks:
        union |= mask
    if union != full_coverage:
        return None

    test_names = [f"T{index}" for index in range(len(coverage_masks))]
    model = "abstract sig Test {}\n"
    model += "one sig " + ",".join(test_names) + " extends Test {}\n"
    model += "one sig Selection { selected: set Test }\n"
    model += "fact Separation {\n"
    for pair_index in range(pair_count):
        covering = [
            test_names[index]
            for index, mask in enumerate(coverage_masks)
            if mask & (1 << pair_index)
        ]
        model += "\tsome Selection.selected & (" + " + ".join(covering) + ")\n"
    model += "}\n"
    bitwidth = int_bitwidth(len(coverage_masks))
    model += f"run {{ minsome Selection.selected }} for {bitwidth} Int\n"

    world = CompUtil.parseEverything_fromString(None, model)
    command = world.getAllCommands()[0]
    options = A4Options()
    options.solver = A4Options.SatSolver.SAT4JMax
    solution = TranslateAlloyToKodkod.execute_command(
        None,
        world.getAllReachableSigs(),
        command,
        options,
    )
    if not solution.satisfiable():
        raise RuntimeError("finite minimum test-cover encoding is unsatisfiable")
    return [
        index
        for index, name in enumerate(test_names)
        if bool(
            solution.eval(
                CompUtil.parseOneExpression_fromString(
                    world,
                    f"{name} in Selection.selected",
                )
            )
        )
    ]


def enumerated_test_set(content, scope, trace_length=None, statistics=None):
    """Enumerate attainable candidate bipartitions, then minimize their cover.

    Every SAT call returns one instance whose candidate truth values induce a
    previously unseen nontrivial bipartition.  The next call blocks that whole
    pattern, including its complementary truth vector.  Exhausting these
    patterns gives the complete finite set needed for exact test cover without
    enumerating structurally distinct instances that behave identically.
    """

    statistics = statistics if statistics is not None else {}
    if requires_trace_length(content):
        raise ValueError(
            "batch enumerate is restricted to static Alloy models"
        )
    collector = parse(content, trace_length=trace_length)
    predicates = list(collector.predicates)
    if len(predicates) < 2:
        statistics.update(
            enumerated_instances=0,
            pattern_witnesses=0,
            separation_patterns=0,
            enumeration_solver_calls=0,
            selected_tests=0,
            enumeration_seconds=0.0,
            cover_seconds=0.0,
        )
        return []

    pairs = list(combinations(range(len(predicates)), 2))
    pair_bits = {pair: 1 << index for index, pair in enumerate(pairs)}
    representatives = {}
    blocked_patterns = []
    options = A4Options()
    options.solver = A4Options.SatSolver.SAT4J

    enumeration_start = timer()
    pattern_witnesses = 0
    solver_calls = 0
    while True:
        analysis = _pattern_analysis(
            collector,
            scope,
            predicates,
            blocked_patterns,
        )
        world = CompUtil.parseEverything_fromString(None, analysis)
        command = world.getAllCommands()[0]
        predicate_expressions = [
            CompUtil.parseOneExpression_fromString(world, predicate)
            for predicate in predicates
        ]
        solution = TranslateAlloyToKodkod.execute_command(
            None,
            world.getAllReachableSigs(),
            command,
            options,
        )
        solver_calls += 1
        if not solution.satisfiable():
            break
        pattern_witnesses += 1
        truths = tuple(
            bool(solution.eval(expression))
            for expression in predicate_expressions
        )
        coverage = _coverage_mask(truths, pair_bits)
        if not coverage or coverage in representatives:
            raise RuntimeError(
                "separation-pattern blocker returned a duplicate pattern"
            )
        representatives[coverage] = _instance_from_solution(
            collector,
            world,
            solution,
        )
        blocked_patterns.append(_pattern_constraint(predicates, truths))
        if pattern_witnesses <= 10 or pattern_witnesses % 100 == 0:
            print(
                "// Enumerated "
                f"{pattern_witnesses} distinct separation patterns",
                flush=True,
            )
    enumeration_seconds = timer() - enumeration_start

    full_coverage = (1 << len(pairs)) - 1
    available_coverage = 0
    for coverage in representatives:
        available_coverage |= coverage
    missing_pairs = [
        (predicates[left], predicates[right])
        for pair_index, (left, right) in enumerate(pairs)
        if not available_coverage & (1 << pair_index)
    ]
    if pattern_witnesses == 0:
        statistics.update(
            enumerated_instances=0,
            pattern_witnesses=0,
            separation_patterns=0,
            enumeration_solver_calls=solver_calls,
            selected_tests=0,
            enumeration_seconds=enumeration_seconds,
            cover_seconds=0.0,
            error=(
                "no instance distinguishes any candidates within the "
                "configured bounds"
            ),
        )
        missing_pairs = list(pairs)
        statistics["equivalent_pairs"] = [
            (predicates[left], predicates[right])
            for left, right in missing_pairs
        ]
        print("No candidates can be distinguished within the configured bounds.")
        return []
    if available_coverage != full_coverage:
        statistics.update(
            enumerated_instances=pattern_witnesses,
            pattern_witnesses=pattern_witnesses,
            separation_patterns=len(representatives),
            enumeration_solver_calls=solver_calls,
            selected_tests=0,
            enumeration_seconds=enumeration_seconds,
            cover_seconds=0.0,
            equivalent_pairs=missing_pairs,
        )
        rendered = ", ".join(f"{left}/{right}" for left, right in missing_pairs)
        print(f"Some predicates are equivalent within the bounds: {rendered}.")
        return []

    coverage_masks = list(representatives)
    cover_start = timer()
    selected = minimum_test_cover(coverage_masks, len(pairs))
    cover_seconds = timer() - cover_start
    if selected is None:
        raise RuntimeError("enumerated separation patterns do not form a test cover")
    instances = [representatives[coverage_masks[index]] for index in selected]
    statistics.update(
        enumerated_instances=pattern_witnesses,
        pattern_witnesses=pattern_witnesses,
        separation_patterns=len(representatives),
        enumeration_solver_calls=solver_calls,
        selected_tests=len(instances),
        enumeration_seconds=enumeration_seconds,
        cover_seconds=cover_seconds,
    )
    print(
        f"// Enumerated {len(representatives)} separation patterns with "
        f"{solver_calls} SAT calls"
    )
    return instances
