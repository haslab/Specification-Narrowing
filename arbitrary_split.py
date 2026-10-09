"""Arbitrary Split batch synthesis using SAT queries and cross-branch reuse."""

import sys
from timeit import default_timer as timer
from alloy import parse, build_instance, command_scope, print_instances, requires_trace_length

import jpype
import jpype.imports

if not jpype.isJVMStarted():
    jpype.startJVM(classpath=["AlloyMax-1.0.2.jar"])

from edu.mit.csail.sdg.parser import CompUtil
from edu.mit.csail.sdg.translator import A4Options, TranslateAlloyToKodkod

def arbitrary_split_batch(content, scope, trace_length=None):
    """Synthesize a complete distinguishing batch with Arbitrary Split."""

    collector = parse(content, trace_length=trace_length)
    model_content = collector.content
    scope_clause = command_scope(collector, scope)

    predicates = list(collector.predicates)

    if len(predicates) < 2:
        return []

    todo = [predicates]
    instances = []

    while todo:
        predicates = todo.pop()
        formula = "{" + " or ".join(predicates) + "} and { not {" + " and ".join(predicates) + "} }"
        # check if any previous instance can be reused
        for inst in instances:
            command = f"run {{ {{ {inst} }} and {{ {formula} }} }} {scope_clause}\n"
            model = command + "\n" + model_content
            world = CompUtil.parseEverything_fromString(None,model)
            command = world.getAllCommands()[0]
            options = A4Options()
            options.solver = A4Options.SatSolver.SAT4J
            solution = TranslateAlloyToKodkod.execute_command(None, world.getAllReachableSigs(), command, options)
            if solution.satisfiable():
                instance = inst
                break
        else:
            # generate a new instance
            command = f"run {{ {formula} }} {scope_clause}"
            model = command + "\n" + model_content
            world = CompUtil.parseEverything_fromString(None,model)
            command = world.getAllCommands()[0]
            options = A4Options()
            options.solver = A4Options.SatSolver.SAT4J
            solution = TranslateAlloyToKodkod.execute_command(None, world.getAllReachableSigs(), command, options)
            if not solution.satisfiable():
                print(f"Some predicates are equivalent.")
                return []

            # build formula for instance
            value = {}
            for sig in collector.signatures:
                tuples = solution.eval(CompUtil.parseOneExpression_fromString(world, sig))
                value[sig] = [[t.atom(i) for i in range(t.arity())] for t in tuples]
            for field in collector.fields:
                tuples = solution.eval(CompUtil.parseOneExpression_fromString(world, field))
                value[field] = [[t.atom(i) for i in range(t.arity())] for t in tuples]
            instance = build_instance(collector, value)
            instances.append(instance)

        # split predicates into positive and negative sets
        pos = []
        neg = []
        for pred in predicates:
            command = f"check {{ {{ {instance} }} implies {{ {pred} }} }} {scope_clause}\n"
            model = command + "\n" + model_content
            world = CompUtil.parseEverything_fromString(None,model)
            command = world.getAllCommands()[0]
            options = A4Options()
            options.solver = A4Options.SatSolver.SAT4J
            solution = TranslateAlloyToKodkod.execute_command(None, world.getAllReachableSigs(), command, options)
            if solution.satisfiable():
                neg.append(pred)
            else:
                pos.append(pred)
        if len(pos) > 1:
            todo.append(pos)
        if len(neg) > 1:
            todo.append(neg)
    return instances

def main():
        # check command line arguments
    if len(sys.argv) not in (3, 4):
        print("Usage: python arbitrary_split.py <filename> <scope> [trace-length]")
        sys.exit(1)

    filename = sys.argv[1]
    scope = int(sys.argv[2])
    trace_length = int(sys.argv[3]) if len(sys.argv) == 4 else None
    
    with open(filename,'r') as file:
        content = file.read() 
        if requires_trace_length(content) and trace_length is None:
            print("Error: trace-length is required for models using Alloy 6 temporal features.")
            sys.exit(1)
        start = timer()
        test_set = arbitrary_split_batch(content, scope, trace_length)
        end = timer()
        print(f"// Generated {len(test_set)} test cases in {end - start} seconds")
        print_instances(test_set, scope, parse(content, trace_length=trace_length))

if __name__ == "__main__":
    main()
