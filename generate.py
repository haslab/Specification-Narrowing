"""Generate narrowing benchmark problems from the Alloy4Fun dataset."""

import argparse
import json
from pathlib import Path

from alloy import AlloyParseError, parse


# Validation only needs a positive bound to exercise the same Alloy 6 -> Alloy 5
# translation used by narrow.py.  The generated problem does not embed this bound.
VALIDATION_TRACE_LENGTH = 1


def argument_parser():
    parser = argparse.ArgumentParser(
        description="Generate benchmark Alloy models from dataset.json."
    )
    parser.add_argument("min_size", type=int)
    parser.add_argument("max_size", type=int)
    parser.add_argument("step_size", type=int)
    parser.add_argument("models", nargs="+")
    parser.add_argument(
        "--mode",
        choices=("static", "temporal"),
        default="static",
        help=(
            "validation mode: static rejects Alloy 6 temporal features; temporal "
            "accepts the bounded temporal subset supported by narrow.py"
        ),
    )
    return parser


def _trace_length(mode):
    return VALIDATION_TRACE_LENGTH if mode == "temporal" else None


def _alloy5_error(content):
    """Return an AlloyMax parse/type error for translated content, if any."""

    import jpype
    import jpype.imports

    if not jpype.isJVMStarted():
        jar = Path(__file__).with_name("AlloyMax-1.0.2.jar")
        jpype.startJVM(classpath=[str(jar)])

    from edu.mit.csail.sdg.alloy4 import Err
    from edu.mit.csail.sdg.parser import CompUtil

    try:
        CompUtil.parseEverything_fromString(None, content)
        return None
    except Err as error:
        return str(error.msg)


def validation_error(content, mode):
    """Return why the narrowing input path rejects content, or None."""

    try:
        collector = parse(content, trace_length=_trace_length(mode))
    except AlloyParseError as error:
        return str(error)
    return _alloy5_error(collector.content)


def specification_error(base, specification, mode):
    """Validate one candidate in the same predicate shape written to a problem."""

    candidate = f"{base}\npred __generate_candidate {{ {specification} }}"
    return validation_error(candidate, mode)


def generate_problems(dataset, sizes, model_ids, mode, output_dir=Path("problems")):
    """Filter accepted models/specifications and write the requested problems."""

    generated = []
    selected = set(model_ids)
    for example in (item for item in dataset if item["id"] in selected):
        base_model = example["model"]
        error = validation_error(base_model, mode)
        if error is not None:
            print(f"Skipped model {example['id']}: {error}")
            continue

        for requirement in example["requirements"]:
            specifications = []
            for specification in [requirement["oracle"], *requirement["erroneous"]]:
                error = specification_error(base_model, specification, mode)
                if error is None:
                    specifications.append(specification)
                else:
                    print(
                        "Discarded specification for "
                        f"{example['id']} {requirement['pred']}: {error}"
                    )

            for size in sizes:
                if size > len(specifications):
                    print(
                        f"Skipping generation for {example['id']} "
                        f"{requirement['pred']} size {size} since only "
                        f"{len(specifications)} specifications are available."
                    )
                    continue

                model = base_model
                for index, specification in enumerate(specifications[:size]):
                    model += f"\npred S{index} {{ {specification} }}\n"

                output_dir.mkdir(parents=True, exist_ok=True)
                requirement_name = requirement["pred"][5:]
                output = output_dir / (
                    f"{example['id']}_{requirement_name}_{size}.als"
                )
                output.write_text(model)
                generated.append(output)
    return generated


def main(argv=None):
    args = argument_parser().parse_args(argv)
    sizes = range(args.min_size, args.max_size + 1, args.step_size)
    with open("dataset.json", "r") as file:
        dataset = json.load(file)
    generate_problems(dataset, sizes, args.models, args.mode)


if __name__ == "__main__":
    main()
