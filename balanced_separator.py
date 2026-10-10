"""Single-test synthesis shared by Balanced Split and iterative classification."""

from itertools import combinations

from alloy import build_instance, int_bitwidth
from classification import reified_truth_vectors

import jpype
import jpype.imports

if not jpype.isJVMStarted():
    jpype.startJVM(classpath=["AlloyMax-1.0.2.jar"])

from edu.mit.csail.sdg.parser import CompUtil
from edu.mit.csail.sdg.translator import A4Options, TranslateAlloyToKodkod


def _instance_from_solution(
    collector, world, solution, instance_atom=None, truth_vector=None
):
    value = {}
    for signature in collector.signatures:
        tuples = solution.eval(
            CompUtil.parseOneExpression_fromString(world, signature)
        )
        if instance_atom is None:
            value[signature] = [
                [tuple_.atom(index) for index in range(tuple_.arity())]
                for tuple_ in tuples
            ]
        else:
            value[signature] = [
                [tuple_.atom(index) for index in range(1, tuple_.arity())]
                for tuple_ in tuples
                if tuple_.atom(0) == instance_atom
            ]
    for field in collector.fields:
        tuples = solution.eval(
            CompUtil.parseOneExpression_fromString(world, field)
        )
        start = 0 if instance_atom is None else 1
        value[field] = [
            [tuple_.atom(index) for index in range(start, tuple_.arity())]
            for tuple_ in tuples
            if instance_atom is None or tuple_.atom(0) == instance_atom
        ]
    return build_instance(collector, value, truth_vector=truth_vector)


def _solution_truth_vector(
    collector, world, solution, instance_atom, candidates, truth_predicates
):
    """Read encoded answers and evaluate any other requested candidates.

    The separator encodes only the current candidates in ``valid``. Batch
    synthesis also needs the original candidates for cross-branch reuse. Bind
    the original relation names to the single reified instance and evaluate
    their bodies directly on this solution, without changing the solver query.
    """

    truths = reified_truth_vectors(world, solution, candidates)[str(instance_atom)]
    missing = [predicate for predicate in truth_predicates if predicate not in truths]
    if missing:
        relations = list(collector.signatures) + list(collector.fields)
        bindings = ", ".join(f"{name} = Instance.{name}" for name in relations)
        for predicate in missing:
            formula = "{\n" + collector.predicates[predicate] + "\n}"
            expression = f"let {bindings} | {formula}" if bindings else formula
            truths[predicate] = bool(solution.eval(
                CompUtil.parseOneExpression_fromString(world, expression)
            ))
    return truths


def _balanced_separator_model(collector, candidates, scope):
    model = "sig Atom {}\nabstract sig Formula {}\n"
    model += "one sig " + ",".join(candidates) + " extends Formula {}\n"
    model += "one sig Instance {\n"
    for signature in sorted(collector.signatures):
        model += f"\t{signature} : set Atom,\n"
    for field, field_type in collector.fields.items():
        arity = field_type.count("->") + 1
        model += f"\t{field} : " + " -> ".join(["Atom"] * arity) + ",\n"
    model += "\tvalid : set Formula\n} {\n"

    for signature in sorted(collector.toplevel):
        if not (collector.temporal and signature == "State"):
            model += f"\t#{signature} <= {scope}\n"
    for signature, parent in collector.subsets.items():
        model += f"\t{signature} in {parent}\n"
    for left, right in combinations(sorted(collector.toplevel), 2):
        model += f"\tno {left} & {right}\n"
    for signature in sorted(collector.abstract):
        model += (
            f"\t{signature} = "
            + " + ".join(collector.extensions.get(signature, []))
            + "\n"
        )
    for parent in collector.extensions:
        for left, right in combinations(collector.extensions[parent], 2):
            model += f"\tno {left} & {right}\n"
    for signature, multiplicity in collector.multiplicities.items():
        model += f"\t{multiplicity} {signature}\n"
    for field, field_type in collector.fields.items():
        model += f"\t{field} in {field_type}\n"
    for formula in collector.facts.values():
        model += f"\t{{{formula}}}\n"
    for predicate in candidates:
        model += (
            f"\t{predicate} in valid iff "
            f"{{{collector.predicates[predicate]}\n\t}}\n"
        )
    model += "}\n"
    model += "fun separated : Formula -> Formula {\n"
    model += "\t{ f,g : Formula | f != g and "
    model += "(f in Instance.valid iff g not in Instance.valid) }\n"
    model += "}\n"

    atom_scope = scope * len(collector.toplevel)
    if collector.temporal:
        atom_scope += collector.trace_length - scope
    bitwidth = max(scope, int_bitwidth(atom_scope))
    analysis = model + "run {\n"
    analysis += "\tsome Instance.valid\n"
    analysis += "\tsome Formula - Instance.valid\n"
    analysis += "\tmaxsome separated\n"
    analysis += f"}} for {atom_scope} Atom, {bitwidth} Int\n"
    return analysis


def balanced_separator(collector, candidates, scope, truth_predicates=None):
    """Generate a balanced test with predictions for the requested candidates.

    By default only the current candidates are evaluated. Batch synthesis can
    request the full original set for cross-branch reuse and later review.
    """

    if len(candidates) < 2:
        return None
    analysis = _balanced_separator_model(collector, candidates, scope)
    world = CompUtil.parseEverything_fromString(None, analysis)
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
        raise RuntimeError(
            "the remaining predicates cannot be partitioned within the bounds"
        )
    instance_tuples = solution.eval(
        CompUtil.parseOneExpression_fromString(world, "Instance")
    )
    instance_atom = next(iter(instance_tuples)).atom(0)
    truth_vector = _solution_truth_vector(
        collector,
        world,
        solution,
        instance_atom,
        candidates,
        candidates if truth_predicates is None else truth_predicates,
    )
    return _instance_from_solution(
        collector,
        world,
        solution,
        instance_atom=instance_atom,
        truth_vector=truth_vector,
    )
