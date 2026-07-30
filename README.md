# Data

- [`dataset.json`](./dataset.json): a set of requirements with semantically different specifications, collected from this [dataset](https://zenodo.org/records/17392203).
- [`generate.py`](./generate.py): script for the generation of the benchmark Alloy models from the dataset.
- [`problems`](./problems): pre-generated benchmark of Alloy models.
- [`evaluation.py`](./evaluation.py): script for evaluating the four batch-construction methods over the benchmarks.
- [`alloy.py`](./alloy.py): structure-aware Alloy parser and bounded Alloy 6-to-5 temporal translator.
- [`narrow.py`](./narrow.py): unified command-line interface for distinguishing-batch construction.
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
[`evaluation-results.json`](./evaluation-results.json). At structural scope 3,
Balanced, Recursive, Exact, and Enumeration complete 176, 196, 163, and 152 of
the 196 static configurations, and 30, 32, 9, and 31 of the 32 temporal
configurations, respectively. On the 151 static configurations jointly
completed by Balanced, Recursive, and Exact, their mean batch sizes are 7.36,
8.09, and 5.17 tests. The paper reports the paired classification,
cardinality, synthesis-time, scope, trace-length, and always-online analyses
derived from this file.

The JSON records the same method IDs together with a display name and family.
Batch entries record `synthesis_timeout_seconds` as the total batch-synthesis
budget, while the online-study configuration records its separate traversal
safety timeout. Post-synthesis truth-table evaluation and classification
simulation are timed separately.

# Scripts

Start by installing the requirements.

```
pip install -r requirements.txt
```

## Data preparation

Script `generate.py`, for each pair model/requirements in `dataset.json`, creates an Alloy model with alternative requirement specifications as predicates. The specifications in `dataset.json` are from a [dataset](https://zenodo.org/records/17392203) that guarantees that the alternatives are non-equivalent, as required by all four methods. Models and specifications are filtered with the same parser and bounded Alloy 6-to-5 translation used by `narrow.py`; the translated Alloy 5 is then parsed and typechecked by AlloyMax, as it is during narrowing.

The script takes as arguments a range of sizes for the set of alternative specifications and the model IDs to process. `--mode static` (the default) accepts only static inputs. `--mode temporal` uses an internal positive trace bound for validation and accepts the bounded temporal subset supported by `narrow.py`; that validation bound is not embedded in the generated problem. Unsupported base models are skipped once; unsupported candidate specifications are discarded individually. If a requirement does not retain the requested number of specifications, it is skipped.

### Usage

Run the script as:

```
python3 generate.py [--mode {static,temporal}] <min_size> <max_size> <step_size> <models> [<models> ...]
```

### Results

The script was run for the static Social Network (`x3JXgWhJ3uti5Dzxz`),
Production Line (`dyj49tEp7j6aWAQQX`), and Train Station
(`cXPP9QBPTYgTX6WJ6`) models, ranging from 4 to 28 specifications in steps of
4. Each of the 28 selected static requirements has at least 29 source
specifications. The pre-generated models are available in
[`problems`](./problems).

```
python3 generate.py 4 28 4 x3JXgWhJ3uti5Dzxz dyj49tEp7j6aWAQQX cXPP9QBPTYgTX6WJ6
```

For a temporal model, use:

```
python3 generate.py --mode temporal 4 16 4 FwCGymHmbqcziisH5
```

## Experiment execution

`evaluation.py` can run all experiments used by the paper. The main study
compares balanced, recursive, exact, and enumeration-based batch construction
on every static or temporal model in `problems` at structural scope 3. The
static scope experiment runs Balanced, Recursive, and Exact, matching the
paper. The temporal scope and trace-length experiments run all four methods,
including Enumeration, while independently varying structural scope and
maximum trace length. The online comparison measures every Balanced oracle
path on configurations completed by Balanced batch construction. Batch methods
receive the same 60-second budget for synthesizing one complete batch; the
online tree traversal uses a 180-second safety timeout. Every candidate
specification is used as the oracle. Because the bundled benchmark includes
temporal problems, the main comparison requires a trace bound:

```
python3 evaluation.py --trace-length 3
```

The default is the main comparison only. A complete run of every paper study uses
16 candidates for the static scope study and four for the more expensive
temporal sensitivity studies:

```
python3 evaluation.py --study all --trace-length 3 \
  --scope-study-size 16 --temporal-study-size 4
```

Each completed problem is reported immediately on standard output. Detailed
per-oracle classification counts, batch timings rounded to two decimal places,
per-problem statistics, and summaries grouped by candidate count are saved
incrementally to `evaluation-results.json`. Online node and path timings retain
higher precision. Results include complete batch sizes, per-node and
per-oracle online measurements, the structural-scope study, and the independent
temporal trace-length study. Truth-table evaluation and classification
simulation occur after construction and are timed separately from the
synthesis budget. For the online comparison, each oracle is charged only for
nodes on its root-to-leaf path, and those path costs are averaged within each
configuration.

To reproduce the aggregate numbers presented in the paper from the saved raw
entries, run:

```
python3 evaluation.py --paper-report
```

This option is read-only: it does not run Alloy, resume an experiment, or
modify `evaluation-results.json`. It recomputes all three result tables, their
supporting RQ statistics, and the temporal completion, scope, trace-length, and
online results. Pairwise values are labelled with their joint-completion
subset rather than being taken from the cached summaries. Displayed values use
Python's round-to-nearest formatting at the precision shown in the report.

Existing output is resumed automatically, so an interrupted evaluation does
not repeat saved work. `--resume` can still be supplied explicitly:

```
python3 evaluation.py --resume
```

When the selected problem set contains temporal models, supply the maximum
lasso trace length. The same bound is passed to every method and recorded in
the result configuration:

```
python3 evaluation.py --resume --trace-length 3
```

Legacy format-7 results without this setting can be resumed with a trace
length; their completed static problems are retained. Later resumes inherit
the recorded bound when `--trace-length` is omitted, while specifying a
different bound is rejected to avoid mixing incompatible measurements.

The scope mode performs two independent sweeps. The structural sweep varies
scope from `--scope-study-min` through `--scope-study-max` while keeping trace
length fixed at `--trace-length`. The temporal-depth sweep varies trace length
from `--trace-study-min` through `--trace-study-max` while keeping scope fixed
at `--scope`. With the defaults and `--scope 3 --trace-length 3`, the evaluated
pairs are therefore `(3,3), (4,3), ..., (7,3)` and `(3,3), (3,4), ...,
(3,7)`. The shared `(3,3)` result is reused.

Static and temporal scope experiments can use different candidate counts. The
paper configuration uses 16 candidates for the static experiment and four for
the more expensive temporal experiments:

```
python3 evaluation.py --study scope --trace-length 3 \
  --scope-study-size 16 --temporal-study-size 4
```

`--temporal-study-size` defaults to `--scope-study-size`. The trace-study
minimum defaults to `--trace-length`; its maximum defaults to the same number
of increments as the structural scope range, and both can be overridden with
`--trace-study-min` and `--trace-study-max`.

Use `--study main`, `--study scope`, or `--study online` to run one study
family, and `--overwrite` to deliberately discard an existing result file and
start over. The online study consumes completed Balanced entries from the main
study, so run the main study first or use `--study all`.

`--min-size`, `--max-size`, and `--limit` are available for shorter trial
runs. A timed-out worker is terminated before the evaluation continues, so it
does not leave a Python/JVM synthesis process running.

## Running the narrowing tool

The included [`paper/courses.als`](paper/courses.als) model contains six
alternative static specifications. For example, these commands construct
recursive and cardinality-minimum distinguishing batches at scope 3:

```
python3 narrow.py recursive paper/courses.als 3
python3 narrow.py exact paper/courses.als 3
```

The scripts also accept future-time Alloy 6 specifications. Mutable subset
signatures and mutable fields are translated to explicit state-indexed
relations, and temporal operators are embedded into Alloy 5 over a bounded
lasso trace. The mandatory back-loop makes every generated temporal test an
infinite, ultimately periodic execution.

Temporal models require a separate `trace-length` argument. It is an upper
bound, so the solver may generate any lasso containing between one and that
many states.

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
  encoding. This cover-based method is intentionally exponential. For temporal
  inputs, it enumerates patterns over the same bounded lasso traces used by the
  other methods.

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
python3 narrow.py balanced paper/courses.als 3 --classify
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
python3 narrow.py balanced paper/courses.als 3 --simulate Spec2
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
`always`, `eventually`, `until`, `releases`, and postfix prime (`'`), including
repeated primes, primed parenthesized relational expressions, Boolean combinations,
implicit conjunctions between formulas in blocks, `implies ... else ...`
conditionals, and first-order quantifiers. For now, mutable declarations are deliberately
restricted to fieldless subset signatures of the form `var sig X in Parent {}`
(with an optional multiplicity). Mutable fields declared on static signatures
are encoded using the local-state idiom. Parameterized helper predicates,
signature facts, past-time operators, mutable `extends` signatures, and mutable
non-subset signatures are rejected rather than silently mistranslated.
