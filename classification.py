"""Evaluate specification candidates on synthesized Alloy tests."""

from alloy import Instance

import jpype
import jpype.imports

if not jpype.isJVMStarted():
    jpype.startJVM(classpath=["AlloyMax-1.0.2.jar"])

from edu.mit.csail.sdg.parser import CompUtil


def solution_truth_vector(world, solution, predicates):
    """Evaluate candidates on a native Alloy solution without further solving."""

    return {
        predicate: bool(solution.eval(
            CompUtil.parseOneExpression_fromString(world, predicate)
        ))
        for predicate in predicates
    }


def reified_truth_vectors(world, solution, predicates):
    """Read the candidate/test relation already computed by a cover solver."""

    valid = solution.eval(CompUtil.parseOneExpression_fromString(world, "valid"))
    accepted = {(str(item.atom(0)), str(item.atom(1))) for item in valid}
    formula_atoms = {}
    for predicate in predicates:
        atoms = solution.eval(
            CompUtil.parseOneExpression_fromString(world, predicate)
        )
        formula_atoms[predicate] = str(next(iter(atoms)).atom(0))
    instances = solution.eval(
        CompUtil.parseOneExpression_fromString(world, "Instance")
    )
    return {
        str(item.atom(0)): {
            predicate: (str(item.atom(0)), atom) in accepted
            for predicate, atom in formula_atoms.items()
        }
        for item in instances
    }


def predicate_holds(collector, instance, predicate, structural_scope):
    """Read a prediction for one of the test's original synthesis candidates.

    Missing predictions indicate an incomplete synthesis result. Never launch
    a new solver query to reconstruct information discarded by a caller.
    """

    if (
        not isinstance(instance, Instance)
        or instance.truth_vector is None
        or predicate not in instance.truth_vector
    ):
        raise ValueError(f"test has no synthesized prediction for {predicate}")
    return instance.truth_vector[predicate]
