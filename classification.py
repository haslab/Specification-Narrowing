"""Evaluate specification candidates on synthesized Alloy tests."""

from alloy import command_scope

import jpype
import jpype.imports

if not jpype.isJVMStarted():
    jpype.startJVM(classpath=["AlloyMax-1.0.2.jar"])

from edu.mit.csail.sdg.parser import CompUtil
from edu.mit.csail.sdg.translator import A4Options, TranslateAlloyToKodkod


def predicate_holds(collector, instance, predicate, structural_scope):
    """Return whether ``predicate`` holds on one concrete generated test."""

    scope = command_scope(collector, structural_scope)
    analysis = (
        f"check {{ {{ {instance} }} implies {{ {predicate} }} }} {scope}\n"
        + collector.content
    )
    world = CompUtil.parseEverything_fromString(None, analysis)
    command = world.getAllCommands()[0]
    options = A4Options()
    options.solver = A4Options.SatSolver.SAT4J
    solution = TranslateAlloyToKodkod.execute_command(
        None,
        world.getAllReachableSigs(),
        command,
        options,
    )
    # A satisfiable Alloy check is a counterexample: the predicate is false
    # on the pinned instance. An unsatisfiable check means it is true.
    return not solution.satisfiable()
