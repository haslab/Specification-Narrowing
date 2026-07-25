# Data

- [`dataset.json`](./dataset.json): a set of requirements with semantically different specifications, collected from this [dataset](https://zenodo.org/records/17392203).
- [`generate.py`](./generate.py): script for the generation of the benchmark Alloy models from the dataset.
- [`problems`](./problems): pre-generated benchmark of Alloy models.
- [`evaluation.py`](./evaluation.py): script for evaluating the four batch-construction methods over the benchmarks.
- [`alloy.py`](./alloy.py): script to process Alloy 5 models.
- [`narrow.py`](./narrow.py): unified command-line interface for distinguishing-batch construction
- [`evaluation-results.json`](./evaluation-results.json): consolidated,
  resumable evaluation data and summaries.
- [`AlloyMax-1.0.2.jar`](./AlloyMax-1.0.2.jar): snapshot of AlloyMax, used to parse and execute Alloy models and commands.
- [`paper`](./paper/): directory with the running example used in the paper, including GPT-5.2 interaction.

# Results

The evaluation uses four stable method IDs. The two tree-guided methods build an
implicit decision tree and reuse tests across its nodes; the two cover-based
methods minimize the set of tests that separates every candidate pair.

| Method ID | Display name | Family | Primary objective |
|-----------|--------------|--------|-------------------|
| `balanced` | Balanced MaxSAT | tree-guided | classification cost |
| `recursive` | Recursive SAT | tree-guided | robust synthesis |
| `exact` | Exact MaxSAT | cover-based | minimum cardinality |
| `enumerate` | Separation-pattern enumeration | cover-based | minimum cardinality |

The authoritative measurements and generated summaries are stored in
[`evaluation-results.json`](./evaluation-results.json). At scope 3, Balanced,
Recursive, Exact, and Enumeration complete 176, 196, 163, and 152 of the 196
configurations, respectively. On the 151 configurations jointly completed by
Balanced, Recursive, and Exact, their mean batch sizes are 7.36, 8.09, and 5.17
tests. The paper reports the paired classification, cardinality, synthesis-time,
scope, and always-online analyses derived from this file.

The JSON records the same method IDs together with a display name and family.
Every result uses `synthesis_timeout_seconds` for the total batch-synthesis
budget; post-synthesis truth-table evaluation and classification simulation are
timed separately.

# Scripts

Start by installing the requirements.

```
pip install -r requirements.txt
```

## Data preparation

Script `generate.py`, for each pair model/requirements in `dataset.json`, creates an Alloy model with alternative requirement specifications as predicates. The specifications in `dataset.json` are from a [dataset](https://zenodo.org/records/17392203) that guarantees that the alternatives are non-equivalent, as required by all four methods. Exact MaxSAT relies on AlloyMax, which accepts Alloy 5 input; although the requirements in `dataset.json` are static, temporal Alloy 6 features occasionally occur in student submissions. Those submissions are filtered out by `generate.py`.

The script takes as argument a range of sizes for the set of alternative specifications. If a certain requirement does not have the required number of specifications, it is skipped.

### Usage

Run the script as:

```
Usage: python generate.py <min_size> <max_size> <step_size> <models>
```

### Results

The script was run for models Social Network (`x3JXgWhJ3uti5Dzxz`), Production line (`dyj49tEp7j6aWAQQX`) and Train Station (`cXPP9QBPTYgTX6WJ6`), ranging from 4 to 28 specifications, with step of 4 (the minimal number of specifications among all requirements in `dataset.json` is 29). The pre-generated models are available in [problems](./problems).

```
python3 generate.py 4 28 4 x3JXgWhJ3uti5Dzxz dyj49tEp7j6aWAQQX cXPP9QBPTYgTX6WJ6
```

## Experiment execution

`evaluation.py` runs all experiments used by the paper. The main study compares
balanced, recursive, exact, and enumeration-based batch construction on every static
model in `problems` at scope 3. The scope study runs balanced, recursive, and
exact construction on the 28 configurations with 16 candidates at scopes
3 through 7. The online comparison measures every balanced oracle path on the
176 configurations completed by balanced batch construction. Batch methods
receive the same 60-second budget for synthesizing one complete batch; the
online tree traversal uses a 180-second safety timeout. Every candidate
specification is used as the oracle:

```
python3 evaluation.py
```

Each completed problem is reported immediately on standard output. Detailed
per-oracle classification counts, two-decimal timing measurements in seconds,
per-problem statistics, and summaries grouped by candidate count are saved
incrementally to `evaluation-results.json`. Results include complete batch
sizes, per-node and per-oracle online measurements, and the RQ2 scope study.
Truth-table evaluation and classification simulation occur after construction
and are timed separately from the synthesis budget. For the online comparison,
each oracle is charged only for nodes on its root-to-leaf path, and those path
costs are averaged within each configuration.

Existing output is resumed automatically, so an interrupted evaluation does
not repeat saved work. `--resume` can still be supplied explicitly:

```
python3 evaluation.py --resume
```

Older schemas in `evaluation-results.json` are migrated in place. Existing
recursive, exact, enumeration, scope-study, and online-comparison results are
retained. Migration can be performed without starting synthesis:

```
python3 evaluation.py --migrate-only
```

To run only the missing RQ2 scope experiment after migration:

```
python3 evaluation.py --study scope
```

Use `--study main`, `--study scope`, or `--study online` to run one
experiment, and `--overwrite` to deliberately discard an existing result
file and start over.

`--min-size`, `--max-size`, and `--limit` are available for shorter trial
runs. A timed-out worker is terminated before the evaluation continues, so it
does not leave a Python/JVM synthesis process running.

## Temporal Alloy 6 specifications

The narrowing scripts also accept future-time Alloy 6 specifications such as
[`paper/light.als`](paper/light.als). Mutable subset signatures and mutable
fields are translated to explicit state-indexed relations, and temporal
operators are embedded into Alloy 5 over a bounded lasso trace. The back-loop
from the last state is mandatory, so every generated test denotes an infinite,
ultimately periodic execution.

Temporal models require a separate `trace-length` argument. It is an upper
bound, so the solver may generate any lasso containing between one and that
many states. For example, the following commands use structural scope 3 and a
maximum trace length of 5:

```
python3 narrow.py recursive paper/light.als 3 5
python3 narrow.py exact paper/light.als 3 5
```

With the Exact MaxSAT method, AlloyMax minimizes the number of generated
instances. Trace length is only an upper bound and is not a secondary
optimization objective.

The unified command syntax is:

```
python3 narrow.py <method> <filename> <scope> [trace-length]
```

Every method constructs a complete distinguishing batch before
classification:

- `balanced` (tree-guided) recursively constructs a balanced decision tree. At each node it
  first reuses a stored test if that test achieves an ideal split. Otherwise it
  synthesizes the best feasible split with AlloyMax and reuses a stored test
  when it matches that optimum; only genuinely better tests are added.
- `recursive` (tree-guided) generates a complete suite using recursive SAT-based
  partitioning and test reuse.
- `exact` (cover-based) generates a complete minimum test cover with
  AlloyMax.
- `enumerate` (cover-based) uses repeated SAT calls to enumerate every attainable
  nontrivial separation pattern of the candidates, retains one representative
  instance per pattern, and applies an exact finite minimum test-cover
  encoding. This cover-based method is intentionally exponential and
  static-only; temporal models are rejected.

The optional classification flags consume the generated fixed suite; without
them the complete suite is printed.

After finding a representative instance, explicit enumeration blocks its
complete candidate bipartition. The blocker is expressed relative to the first
candidate, so it also blocks the complementary truth vector, which has the
same pair coverage. Structurally different Alloy instances with that behavior
are therefore never enumerated. There can nevertheless be up to
`2^(N-1)-1` nontrivial patterns for `N` candidates. The command reports
progress for the first ten patterns and then every hundred patterns. At
smaller scopes, it reports candidate pairs that have become equivalent within
the bound and cannot be separated. The comparison evaluator applies its
common total synthesis timeout to the complete enumeration-and-cover task and
terminates the worker on timeout.

Use `--classify` to open the native graphical classifier. It presents one
generated test at a time and identifies the alternative specification whose
truth values agree with the answers:

```
python3 narrow.py balanced paper/light.als 3 5 --classify
```

Each step chooses from the fixed generated suite the unused test that most
evenly partitions the specifications still consistent with previous answers.
The session stops as soon as one or no specification remains. **Back** undoes
the previous answer, restores
eliminated specifications, and lets the classification be revised. If Tk is
unavailable, the same ordering and backtracking are provided in the terminal.

The balanced constructor defines `separated` as the relation containing
each ordered pair of remaining predicates that disagree on the synthesized
instance and applies AlloyMax's `maxsome separated` objective. If the instance
is accepted by `p` candidates and rejected by `n-p`, `separated` has
`2*p*(n-p)` tuples. Maximizing its cardinality therefore minimizes the largest
side of the partition. Hard constraints require both sides to be nonempty.

Use `--simulate PREDICATE` instead of `--classify` to answer the adaptively
ordered tests automatically, treating the named predicate as the ground
truth. The command reports how many classifications are required to select it:

```
python3 narrow.py balanced paper/light.als 3 5 --simulate Spec2
```

Both interactive and simulated runs report aggregate synthesis and evaluation
time. Evaluation is divided into the post-synthesis construction of the truth
table and the cached ordering/filtering work performed during classification.

`--classify` and `--simulate` are mutually exclusive.

The displayed card depicts atoms, signature membership, and field arrows, and
has Desirable and Undesirable buttons. Temporal cards also have controls for
moving through their states; advancing from the final state follows the
mandatory back-loop. A unique result is shown as a complete Alloy predicate.
Instance graphs use a type-aware layered layout: signature extensions are
ordered by field direction, with collision-spaced atom slots. Cyclic type
groups share a layer. Atoms can be dragged to pin their positions, and their
incident edges update while dragging;
double-click an atom to unpin it or use **Reset layout** to restore the
automatic arrangement. Positions remain stable while moving through temporal
states. The **Relations** menu can show or hide individual field relations,
or all of them at once, without changing the layout.
As in the Alloy visualizer, an atom is named after its deepest signature in
the `extends` hierarchy. Membership in signatures declared with `in` is shown
as an annotation below the atom instead of changing its name. Every extension
signature has its own stable color across all instances and temporal states.
Field relations also receive distinct, stable edge and label colors; the same
relation keeps its color across instances and temporal states.
Arrowheads terminate at atom boundaries instead of underneath nodes. Relation
labels appear when an edge or incident atom is hovered; when filtering leaves
only one visible relation, its labels remain visible.
The viewer uses Python's bundled Tk GUI and does not launch Alloy Analyzer or
any background worker processes. If Tk is unavailable, it falls back to the
terminal classifier.

Exact MaxSAT and Recursive SAT are implemented in `exact.py` and
`recursive.py`, matching the method names used by the CLI and evaluation
data.

Internal Alloy 5 commands explicitly increase the signed `Int` bitwidth when
needed, so cardinality constraints such as `#State <= trace-length` cannot
overflow. In the Exact MaxSAT meta-model the bitwidth covers the complete `Atom`
bound, since each test's `State` relation is represented as an `Instance`
field rather than as a separately scopeable signature.

For temporal inputs, the Alloy 5 encoding is internal: output test cases are
reconstructed in Alloy 6 syntax so they can be pasted into the original model
and visualized as traces by the Alloy 6 Analyzer. The supported temporal operators are `after`,
`always`, `eventually`, `until`, and `releases`, including Boolean combinations
and first-order quantifiers. For now, mutable declarations are deliberately
restricted to fieldless subset signatures of the form `var sig X in Parent {}`
(with an optional multiplicity). Mutable fields declared on static signatures
are encoded using the local-state idiom. Parameterized helper predicates,
signature facts, past-time operators, mutable `extends` signatures, and mutable
top-level signatures are rejected rather than silently mistranslated.
