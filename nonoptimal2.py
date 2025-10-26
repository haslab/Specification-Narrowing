import sys
from timeit import default_timer as timer
from alloy import parse, build_instance, print_instances

import jpype
import jpype.imports

if not jpype.isJVMStarted():
    jpype.startJVM(classpath=["AlloyMax-1.0.2.jar"])

from edu.mit.csail.sdg.parser import CompUtil
from edu.mit.csail.sdg.translator import A4Options, TranslateAlloyToKodkod

def non_optimal2_test_set(content, scope):
    collector = parse(content)

    predicates = list(collector.predicates)

    instances = []
    done = set()
    for i in range(len(predicates)):
        for j in range(i + 1, len(predicates)):
            # no need to generate more than one instance per predicate
            if j in done:
                continue
            # check if any previous instance can be reused
            for inst in instances:
                command = f"check {{ {{ {inst} }} implies {{ {predicates[i]} iff {predicates[j]} }} }} for {scope}\n"
                model = command + "\n" + content
                world = CompUtil.parseEverything_fromString(None,model)
                command = world.getAllCommands()[0]
                options = A4Options()
                options.solver = A4Options.SatSolver.SAT4J
                solution = TranslateAlloyToKodkod.execute_command(None, world.getAllReachableSigs(), command, options)
                if solution.satisfiable():
                   break
            else:
                # generate a new instance
                #print(f"Generating new instance for predicates {predicates[i]} and {predicates[j]}...")
                command = f"check {{ {predicates[i]} iff {predicates[j]} }} for {scope}"
                model = command + "\n" + content
                world = CompUtil.parseEverything_fromString(None,model)
                command = world.getAllCommands()[0]
                options = A4Options()
                solution = TranslateAlloyToKodkod.execute_command(None, world.getAllReachableSigs(), command, options)
                if not solution.satisfiable():
                    print(f"Predicates {predicates[i]} and {predicates[j]} are equivalent.")
                    exit(1)

                # build formula for instance
                value = {}
                for sig in collector.signatures:
                    tuples = solution.eval(CompUtil.parseOneExpression_fromString(world, sig))
                    value[sig] = [[t.atom(i) for i in range(t.arity())] for t in tuples]
                for field in collector.fields:
                    tuples = solution.eval(CompUtil.parseOneExpression_fromString(world, field))
                    value[field] = [[t.atom(i) for i in range(t.arity())] for t in tuples]
                instances.append(build_instance(collector, value))
                done.add(j)
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
        print_instances(non_optimal2_test_set(content, scope), scope)
    end = timer()
    print(f"Time taken: {end - start} seconds")

if __name__ == "__main__":
    main()