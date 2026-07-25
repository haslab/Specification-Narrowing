"""Cardinality-minimum distinguishing-batch synthesis with Exact MaxSAT."""

import argparse
from timeit import default_timer as timer
from itertools import combinations
from alloy import int_bitwidth, parse, build_instance, print_instances, requires_trace_length

import jpype
import jpype.imports

if not jpype.isJVMStarted():
    jpype.startJVM(classpath=["AlloyMax-1.0.2.jar"])

from edu.mit.csail.sdg.parser import CompUtil
from edu.mit.csail.sdg.translator import A4Options, TranslateAlloyToKodkod

def exact_test_set(content, scope, trace_length=None):
    collector = parse(content, trace_length=trace_length)

    model = "sig Atom {}\nabstract sig Formula {}\none sig " + ",".join(collector.predicates.keys()) + " extends Formula {}\nsig Instance {\n"

    for sig in sorted(collector.signatures):
        model += "\t" + sig + " : set Atom,\n"
    for field, typ in collector.fields.items():
        arity = typ.count("->") + 1
        model += "\t" + field + " : " + " -> ".join(["Atom"] * arity) + ",\n"
    model += "\tvalid : set Formula\n} {\n"

    for sig in sorted(collector.toplevel):
        if not (collector.temporal and sig == "State"):
            model += "\t#" + sig + " <= " + str(scope) + "\n"
    for sig, parent in collector.subsets.items():
        model += "\t" + sig + " in " + parent + "\n"
    for a,b in combinations(sorted(collector.toplevel), 2):
        model += "\tno " + a + " & " + b + "\n"
    for sig in sorted(collector.abstract):
        model += "\t" + sig + " = " + " + ".join(collector.extensions.get(sig, [])) + "\n"
    for sig in collector.extensions:
        for a,b in combinations(collector.extensions[sig], 2):
            model += "\tno " + a + " & " + b + "\n"
    for sig, mult in collector.multiplicities.items():
        model += "\t"+ mult + " " + sig + "\n"
    for field, typ in collector.fields.items():
        model += "\t" + field + " in " + typ + "\n"

    for formula in collector.facts.values():
        model += "\t{" + formula + "}\n"

    for pred,formula in collector.predicates.items():
        model += "\t" + pred + " in valid iff {" + formula + "\n\t}\n"


    atom_scope = scope * len(collector.toplevel)
    if collector.temporal:
        atom_scope += collector.trace_length - scope
    instance_scope = len(collector.predicates) - 1
    separation = "\tall disj f,g : Formula | some i : Instance | f in i.valid iff g not in i.valid\n"
    model += "}\n"
    bitwidth = max(scope, int_bitwidth(atom_scope))
    analysis = (
        model
        + "run {\n"
        + separation
        + f"\tminsome Instance}} for {atom_scope} Atom, "
        + f"{instance_scope} Instance, {bitwidth} Int\n"
    )
    world = CompUtil.parseEverything_fromString(None, analysis)
    command = world.getAllCommands()[0]
    options = A4Options()
    options.solver = A4Options.SatSolver.SAT4JMax
    solution = TranslateAlloyToKodkod.execute_command(
        None, world.getAllReachableSigs(), command, options
    )
    if not solution.satisfiable():
        print("Some predicates are equivalent.")
        return []

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
    argument_parser = argparse.ArgumentParser(
        description=(
            "Generate a cardinality-minimum distinguishing batch of Alloy "
            "instances or traces."
        )
    )
    argument_parser.add_argument("filename")
    argument_parser.add_argument("scope", type=int, help="structural Alloy scope")
    argument_parser.add_argument(
        "trace_length",
        type=int,
        nargs="?",
        help="maximum trace length (required for temporal models)",
    )
    args = argument_parser.parse_args()

    with open(args.filename, 'r') as file:
        content = file.read() 
        if requires_trace_length(content) and args.trace_length is None:
            argument_parser.error(
                "trace_length is required for models using Alloy 6 temporal features"
            )
        start = timer()
        test_set = exact_test_set(
            content,
            args.scope,
            args.trace_length,
        )
        end = timer()
        print(f"// Generated {len(test_set)} test cases in {end - start} seconds")
        print_instances(
            test_set,
            args.scope,
            parse(content, trace_length=args.trace_length),
        )

if __name__ == "__main__":
    main()
