import sys
from timeit import default_timer as timer
from alloy import parse, build_instance, print_instances

import jpype
import jpype.imports

if not jpype.isJVMStarted():
    jpype.startJVM(classpath=["AlloyMax-1.0.2.jar"])

from edu.mit.csail.sdg.parser import CompUtil
from edu.mit.csail.sdg.translator import A4Options, TranslateAlloyToKodkod

def non_optimal1_test_set(content, scope):
    collector = parse(content)
    content = content.replace("(","{").replace(")","}")

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
            command = f"run {{ {{ {inst} }} and {{ {formula} }} }} for {scope}\n"
            model = command + "\n" + content
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
            command = f"run {{ {formula} }} for {scope}"
            model = command + "\n" + content
            world = CompUtil.parseEverything_fromString(None,model)
            command = world.getAllCommands()[0]
            options = A4Options()
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
            command = f"check {{ {{ {instance} }} implies {{ {pred} }} }} for {scope}\n"
            model = command + "\n" + content
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
    if len(sys.argv) != 3:
        print("Usage: python parser.py <filename> <scope>")
        sys.exit(1)

    filename = sys.argv[1]
    scope = int(sys.argv[2])
    
    start = timer()
    with open(filename,'r') as file:
        content = file.read() 
        # print commands for instances
        print_instances(non_optimal1_test_set(content, scope), scope)
    end = timer()
    print(f"Time taken: {end - start} seconds")

if __name__ == "__main__":
    main()