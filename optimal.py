import sys
from timeit import default_timer as timer
from itertools import combinations
from alloy import parse, build_instance, print_instances

import jpype
import jpype.imports

if not jpype.isJVMStarted():
    jpype.startJVM(classpath=["AlloyMax-1.0.2.jar"])

from edu.mit.csail.sdg.parser import CompUtil
from edu.mit.csail.sdg.translator import A4Options, TranslateAlloyToKodkod

def optimal_test_set(content, scope):
    collector = parse(content)

    model = "sig Atom {}\nabstract sig Formula {}\none sig " + ",".join(collector.predicates.keys()) + " extends Formula {}\nsig Instance {\n"

    for sig in collector.signatures:
        model += "\t" + sig + " : set Atom,\n"
    for field, typ in collector.fields.items():
        arity = typ.count("->") + 1
        model += "\t" + field + " : " + " -> ".join(["Atom"] * arity) + ",\n"
    model += "\tvalid : set Formula\n} {\n"

    for sig in collector.toplevel:
        model += "\t#" + sig + " <= " + str(scope) + "\n"
    for sig, parent in collector.subsets.items():
        model += "\t" + sig + " in " + parent + "\n"
    for a,b in combinations(collector.toplevel, 2):
        model += "\tno " + a + " & " + b + "\n"
    for sig in collector.abstract:
        model += "\t" + sig + " = " + " + ".join(collector.extensions.get(sig, [])) + "\n"
    for sig in collector.extensions:
        for a,b in combinations(collector.extensions[sig], 2):
            model += "\tno " + a + " & " + b + "\n"
    for sig, mult in collector.multiplicities.items():
        model += "\t"+ mult + " " + sig + "\n"
    for field, typ in collector.fields.items():
        model += "\t" + field + " in " + typ + "\n"

    for fact,formula in collector.facts.items():
        model += "\t{" + formula + "}\n"

    for pred,formula in collector.predicates.items():
        model += "\t" + pred + " in valid iff {" + formula + "\n\t}\n"


    model += "}\nrun {\n\tall disj f,g : Formula | some i : Instance | f in i.valid iff g not in i.valid\n\tminsome Instance\n} for " + str(scope*len(collector.toplevel)) + " Atom, " + str(len(collector.predicates)-1) + " Instance\n"
    
    world = CompUtil.parseEverything_fromString(None,model)
    command = world.getAllCommands()[0]
    options = A4Options()
    options.solver = A4Options.SatSolver.SAT4JMax
    solution = TranslateAlloyToKodkod.execute_command(None, world.getAllReachableSigs(), command, options)
    if not solution.satisfiable():
        print("Some predicates are equivalent.")
        exit(1)

    # build formulas for instances
    instances = []
    full_value = {}
    for sig in collector.signatures:
        full_value[sig] = solution.eval(CompUtil.parseOneExpression_fromString(world, sig))
    for field in collector.fields:
        full_value[field] = solution.eval(CompUtil.parseOneExpression_fromString(world, field))
    for tuple in solution.eval(CompUtil.parseOneExpression_fromString(world, "Instance")):
        id = tuple.atom(0)
        value = {}
        for sig in collector.signatures:
            value[sig] = [[t.atom(1)] for t in full_value[sig] if t.atom(0) == id]
        for field in collector.fields:
            value[field] = [[t.atom(i) for i in range(1, t.arity())] for t in full_value[field] if t.atom(0) == id]
        instances.append(build_instance(collector, value))
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
        print_instances(optimal_test_set(content, scope), scope)
    end = timer()
    print(f"Time taken: {end - start} seconds")

if __name__ == "__main__":
    main()

