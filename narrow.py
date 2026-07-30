"""Unified command-line interface for specification narrowing algorithms."""

import argparse
from timeit import default_timer as timer

from alloy import Instance, parse, print_instances, requires_trace_length
from balanced import balanced_test_set
from classification import predicate_holds
from enumeration import enumerated_test_set
from exact import exact_test_set
from recursive import recursive_test_set
from visualizer import (
    AdaptiveTestSession,
    NativeInstanceVisualizer,
)


BATCH_ALGORITHMS = {
    "balanced": balanced_test_set,
    "exact": exact_test_set,
    "recursive": recursive_test_set,
    "enumerate": enumerated_test_set,
}


def _instance_command(instance, index, scope, name_prefix="Test"):
    command_name = f"{name_prefix}{index}"
    if isinstance(instance, Instance) and instance.alloy6_body is not None:
        return (
            f"run {command_name} {{\n{instance.alloy6_body}\n}} "
            f"for {scope} but {instance.trace_length}..{instance.trace_length} steps"
        )
    return f"run {command_name} {{\n{instance}\n}} for {scope}"


_predicate_holds = predicate_holds


def _read_classification(test_number, can_go_back, input_fn=input):
    while True:
        choices = (
            "[y]es/[n]o/[b]ack/[q]uit"
            if can_go_back
            else "[y]es/[n]o/[q]uit"
        )
        answer = input_fn(
            f"Is Test{test_number} desirable? {choices}: "
        ).strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        if can_go_back and answer in {"b", "back"}:
            return "back"
        if answer in {"q", "quit"}:
            return None
        print(
            "Please answer yes, no, back, or quit."
            if can_go_back
            else "Please answer yes, no, or quit."
        )


def _classification_evaluator(collector, instances, structural_scope):
    """Evaluate the fixed suite once so adaptive ordering is instantaneous."""

    truth_table = [
        {
            predicate: _predicate_holds(
                collector,
                instance,
                predicate,
                structural_scope,
            )
            for predicate in collector.predicates
        }
        for instance in instances
    ]
    instance_indices = {
        id(instance): index for index, instance in enumerate(instances)
    }
    return lambda instance, predicate: truth_table[
        instance_indices[id(instance)]
    ][predicate]


def classify_interactively(
    collector,
    instances,
    structural_scope,
    input_fn=input,
    evaluate=None,
):
    """Display tests, collect user labels, and return consistent predicates."""

    evaluate = evaluate or (
        lambda instance, predicate: _predicate_holds(
            collector,
            instance,
            predicate,
            structural_scope,
        )
    )
    session = AdaptiveTestSession(
        list(collector.predicates),
        instances,
        evaluate=evaluate,
    )
    return classify_session_interactively(collector, session, structural_scope, input_fn)


def classify_session_interactively(collector, session, structural_scope, input_fn=input):
    """Classify tests from either a fixed or dynamically synthesized session."""

    while len(session.remaining) > 1:
        current = session.current_test()
        if current is None:
            break
        _key, test_number, instance = current
        undesirable, desirable = session.current_partition()
        print(
            f"\n=== Test {test_number} "
            f"({len(undesirable)} / {len(desirable)} split) ==="
        )
        print(_instance_command(instance, test_number, structural_scope))
        try:
            classification = _read_classification(
                test_number,
                bool(session.history),
                input_fn=input_fn,
            )
        except (EOFError, KeyboardInterrupt):
            print("\nClassification cancelled.")
            return session.remaining
        if classification is None:
            print("Classification cancelled.")
            return session.remaining
        if classification == "back":
            session.undo()
            continue
        session.answer_current(classification)
        print(
            "Remaining specifications: "
            + (", ".join(session.remaining) if session.remaining else "none")
        )
    return session.remaining


def classify_graphically(collector, instances, structural_scope, evaluate=None):
    """Render the best remaining instance and collect reversible labels."""

    evaluate = evaluate or (
        lambda instance, predicate: _predicate_holds(
            collector,
            instance,
            predicate,
            structural_scope,
        )
    )
    visualizer = NativeInstanceVisualizer(
        collector,
        instances,
        evaluate=evaluate,
    )
    return visualizer.run()


def classify_session_graphically(collector, session):
    """Collect classifications from an adaptively presented fixed batch."""

    return NativeInstanceVisualizer(collector, session=session).run()


def simulate_session(session, ground_truth):
    """Return answers needed to isolate a ground truth in any session type."""

    if ground_truth not in session.predicates:
        raise ValueError(f"unknown candidate predicate: {ground_truth}")
    while len(session.remaining) > 1:
        if session.current_test() is None:
            raise RuntimeError(
                "the generated tests do not distinguish the remaining specifications"
            )
        # Match the interactive path: evaluate the complete partition before
        # looking up the simulated ground-truth answer.
        session.current_partition()
        session.answer_current(session.current_truth(ground_truth))
    if session.remaining != [ground_truth]:
        raise RuntimeError(
            f"simulation did not select the ground truth {ground_truth}"
        )
    return len(session.history)


def simulate_classification(collector, instances, evaluate, ground_truth):
    """Simulate adaptively ordered consumption of a batch-generated suite."""

    session = AdaptiveTestSession(
        list(collector.predicates),
        instances,
        evaluate=evaluate,
    )
    return simulate_session(session, ground_truth)


def fixed_classification_evaluation_seconds(session):
    """Return cached test ordering and filtering time for a fixed suite."""

    return sum(
        timing.preparation_seconds + (timing.filtering_seconds or 0.0)
        for timing in session.timings
    )


def _print_classification_result(collector, remaining):
    source = collector.original or collector
    if len(remaining) == 1:
        predicate = remaining[0]
        print(f"\nConsistent specification: {predicate}")
        print(source.predicates[predicate].strip())
    elif not remaining:
        print("\nNo specification is consistent with all classifications.")
    else:
        print("\nSpecifications still consistent with the classifications:")
        for predicate in remaining:
            print(f"- {predicate}")


def argument_parser():
    argument_parser = argparse.ArgumentParser(
        description="Generate a distinguishing set of Alloy instances or traces."
    )
    argument_parser.add_argument(
        "algorithm",
        choices=(
            "balanced",
            "recursive",
            "exact",
            "enumerate",
        ),
        metavar="{balanced,recursive,exact,enumerate}",
        help="batch-construction method",
    )
    argument_parser.add_argument("filename")
    argument_parser.add_argument("scope", type=int, help="structural Alloy scope")
    argument_parser.add_argument(
        "trace_length",
        type=int,
        nargs="?",
        help="maximum trace length (required for temporal models)",
    )
    interaction = argument_parser.add_mutually_exclusive_group()
    interaction.add_argument(
        "--classify",
        action="store_true",
        help=(
            "graphically classify one selected test at a time and identify "
            "the consistent specification"
        ),
    )
    interaction.add_argument(
        "--simulate",
        metavar="PREDICATE",
        help=(
            "simulate ordered classification using PREDICATE as ground "
            "truth and report the number of classifications"
        ),
    )
    return argument_parser


def main():
    parser = argument_parser()
    args = parser.parse_args()
    algorithm = args.algorithm

    with open(args.filename, "r") as file:
        content = file.read()

    temporal_input = requires_trace_length(content)
    if temporal_input and args.trace_length is None:
        parser.error(
            "trace_length is required for models using Alloy 6 temporal features"
        )
    collector = parse(content, trace_length=args.trace_length)
    if args.simulate is not None and args.simulate not in collector.predicates:
        parser.error(f"unknown candidate predicate: {args.simulate}")

    start = timer()
    test_set = BATCH_ALGORITHMS[algorithm](
        content,
        args.scope,
        args.trace_length,
    )
    end = timer()
    print(f"// Generated {len(test_set)} test cases")
    print(f"// Synthesis time: {end - start} seconds")
    if args.classify or args.simulate is not None:
        print("// Evaluating generated tests against all candidates...", flush=True)
        evaluation_start = timer()
        evaluator = _classification_evaluator(
            collector,
            test_set,
            args.scope,
        )
        evaluation_end = timer()
        evaluation_before = evaluation_end - evaluation_start
        if args.simulate is not None:
            session = AdaptiveTestSession(
                list(collector.predicates),
                test_set,
                evaluate=evaluator,
            )
            classifications = simulate_session(session, args.simulate)
            print(
                f"// Simulated classifications required for {args.simulate}: "
                f"{classifications}"
            )
            print(
                "// Evaluation time before classification: "
                f"{evaluation_before} seconds"
            )
            print(
                "// Evaluation time during classification: "
                f"{fixed_classification_evaluation_seconds(session)} seconds"
            )
        else:
            session = AdaptiveTestSession(
                list(collector.predicates),
                test_set,
                evaluate=evaluator,
            )
            try:
                remaining = classify_session_graphically(collector, session)
            except RuntimeError as error:
                print(
                    f"Graphical viewer unavailable ({error}); using terminal mode."
                )
                remaining = classify_session_interactively(
                    collector,
                    session,
                    args.scope,
                )
            _print_classification_result(collector, remaining)
            print(
                "// Evaluation time before classification: "
                f"{evaluation_before} seconds"
            )
            print(
                "// Evaluation time during classification: "
                f"{fixed_classification_evaluation_seconds(session)} seconds"
            )
    else:
        print_instances(test_set, args.scope, collector)


if __name__ == "__main__":
    main()
