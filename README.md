# Data

- [`dataset.json`](./dataset.json): a set of requirements with semantically different specifications, collected from this [dataset](https://zenodo.org/records/17392203).
- [`generate.py`](./generate.py): script for the generation of the benchmark Alloy models from the dataset.
- [`problems`](./problems): pre-generated benchmark of Alloy models.
- [`evaluation.py`](./evaluation.py): script for executing the evaluation of the narrowing algorithms over the benchmarks.
- [`alloy.py`](./alloy.py): script to process Alloy 5 models.
- [`optimal.py`](./optimal.py) and [`nonoptimal.py`](./nonoptimal.py): directory containing scripts to call LLM APIs and ask for valid/invalid instances given a dataset of requirements and header prompts
- [`results.txt`](./results): pre-collected results from running the evaluation over the benchmark.
- [`AlloyMax-1.0.2.jar`](./AlloyMax-1.0.2.jar): snapshot of AlloyMax, used to parse and execute Alloy models and commands.
- [`paper`](./paper/): directory with the running example used in the paper, including GPT-5.2 interaction.

# Results

## RQ1 and RQ2: Effect of specification set size

### Optimal algorithm, scope 3

| Specifications | 4     | 8    | 12   | 16    | 20    | 24    | 28    |
|----------------|-------|------|------|-------|-------|-------|-------|     
|     Completed  | 27    | 27   | 26   | 25    | 22    | 19    | 12    |
|          Size  | 2.44  | 4.07 | 5.04 | 5.76  | 6.68  | 7.05  | 7.67  |
|           Min  | 2     | 3    | 4    | 4     | 5     | 5     | 6     |
|           Max  | 3     | 6    | 6    | 7     | 8     | 9     | 9     |
|        Median  | 2.00  | 4.00 | 5.00 | 6.00  | 7.00  | 7.00  | 8.00  |
|          Time  | 0.27  | 1.71 | 3.48 | 6.78  | 13.10 | 20.99 | 25.68 |
|           Min  | 0.17  | 0.29 | 0.48 | 0.74  | 1.78  | 3.97  | 7.33  |
|           Max  | 0.51  | 25.73| 34.87| 25.59 | 46.59 | 55.92 | 57.33 |
|        Median  | 0.24  | 0.60 | 1.66 | 4.14  | 8.09  | 19.86 | 22.61 |

### Non-optimal algorithm, scope 3

| Specifications | 4     | 8   | 12   | 16    | 20    | 24    | 28    |
|----------------|-------|-----|------|-------|-------|-------|-------|     
|     Completed  | 28    | 28  | 28   | 28    | 28    | 28    | 28    |
|          Size  | 2.82  | 5.93| 7.86 | 9.82  | 11.43 | 12.96 | 14.39 |
|           Min  | 2     | 4   | 6    | 7     | 7     | 8     | 9     |
|           Max  | 3     | 7   | 10   | 13    | 15    | 18    | 22    |
|        Median  | 3.00  | 6.00| 8.00 | 10.00 | 11.50 | 13.00 | 14.00 |
|          Time  | 0.44  | 0.96| 1.58 | 2.21  |  2.92 |  3.82 | 4.82  |
|           Min  | 0.28  | 0.56| 0.88 | 1.24  |  1.49 |  1.91 | 2.19  |
|           Max  | 0.60  | 1.47| 2.79 | 3.67  |  5.56 |  7.75 | 10.60 |
|        Median  | 0.49  | 1.02| 1.65 | 2.29  |  3.05 |  3.90 | 4.78  |

## RQ3: Effect of scope size

### Optimal algorithm, scope 3

| Specifications | 16    |
|----------------|-------|
|     Completed  | 25    |
|          Size  | 5.76  |
|           Min  | 4     |
|           Max  | 7     |
|        Median  | 6.00  |
|          Time  | 6.78  |
|           Min  | 0.74  |
|           Max  | 25.59 |
|        Median  | 4.14  |

### Optimal algorithm, scope 4

| Specifications | 16    |
|----------------|-------|
|      Completed | 22    |
|           Size | 5.68  |
|            Min | 4     |
|            Max | 7.    |
|         Median | 6.00  |
|           Time | 11.20 |
|            Min | 1.26  |
|            Max | 49.18 |
|         Median | 7.81  |


### Optimal algorithm, scope 5

| Specifications | 16    |
|----------------|-------|
|      Completed | 18    |
|           Size | 5.72  |
|            Min | 4     |
|            Max | 7     |
|         Median | 6.00  |
|           Time | 18.35 |
|            Min | 2.69  |
|            Max | 47.75 |
|         Median | 18.55 |

### Optimal algorithm, scope 6

| Specifications |  16   |
|----------------|-------|
|      Completed | 11    |
|           Size | 5.64  |
|            Min | 4     |
|            Max | 7     |
|         Median | 6.00  |
|           Time | 20.95 |
|            Min | 3.66  |
|            Max | 41.91 |
|         Median | 17.59 |

### Optimal algorithm, scope 7

| Specifications |  16   |
|----------------|-------|
|      Completed | 10    |
|           Size | 5.50  |
|            Min | 4     |
|            Max | 7     |
|         Median | 5.50  |
|           Time | 32.08 |
|            Min | 7.95  |
|            Max | 57.90 |
|         Median | 35.73 |

### Non-optimal algorithm, scope 3

| Specifications | 16    |
|----------------|-------|
|     Completed  | 28    |
|          Size  | 9.82  |
|           Min  | 7     |
|           Max  | 13    |
|        Median  | 10.00 |
|          Time  | 2.21  |
|           Min  | 1.24  |
|           Max  | 3.67  |
|        Median  | 2.29  |

### Non-optimal algorithm, scope 4

| Specifications | 16    |
|----------------|-------|
|      Completed | 28    |
|           Size | 9.93  |
|            Min | 7     |
|            Max | 14    |
|         Median | 10.00 |
|           Time | 4.31  |
|            Min | 1.48  |
|            Max | 10.94 |
|         Median | 4.60  |

### Non-optimal algorithm, scope 5

| Specifications | 16    |
|----------------|-------|
|      Completed | 28    |
|           Size | 10.25 |
|            Min | 7     |
|            Max | 14    |
|         Median | 10.00 |
|           Time | 6.34  |
|            Min | 1.65  |
|            Max | 21.13 |
|         Median | 6.03  |

### Non-optimal algorithm, scope 6

| Specifications | 16    |
|----------------|-------|
|      Completed | 28    |
|           Size | 10.21 |
|            Min | 8     |
|            Max | 13    |
|         Median | 10.00 |
|           Time | 11.55 |
|            Min | 3.99  |
|            Max | 43.27 |
|         Median | 9.20  |

### Non-optimal algorithm, scope 7

| Specifications | 16    |
|----------------|-------|
|      Completed | 27    |
|           Size | 10.04 |
|            Min | 7     |
|            Max | 13    |
|         Median | 10.00 |
|           Time | 14.91 |
|            Min | 5.93  |
|            Max | 46.21 |
|         Median | 9.43  |

# Scripts

Start by installing the requirements.

```
pip install -r requirements.txt
```

## Data preparation

Script `generate.py`, for each pair model/requirements in `dataset.json`, creates an Alloy model with alternative requirement specifications as predicates. The specifications in `dataset.json` are from a [dataset](https://zenodo.org/records/17392203) that guarantees that the alternative specifications are non-equivalent, as required by the algorithms. The optimal narrowing algorithm relies on AlloyMax which does not support Alloy 6; although the requirements in `dataset.json` are purely static, temporal Alloy 6 features occasionally occur in student submissions. Those are filtered out by `generate.py`.

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

Script `evaluation.py` calls a given narrowing algorithms (either `optimal` or `nonoptimal`) and runs it for Alloy models available in folder [problems](./problems) withing a given range of specification set size, and a range of scopes (the default upper-bound for top-level signatures). Results are presented in the standard output. 

Note that, even though the selected alternative specifications are guaranteed to be non-equivalent, they may become equivalent within certain smaller scopes. In those cases ...

### Usage

To evaluate a narrowing algorithm, the evaluation script is run as:

```
"Usage: python evaluation.py <algorithm> <min_scope> <max_scope> <min_size> <max_size>"
```

Where `<algorithm>` is either `optimal` or `nonoptimal`.

### Results

The script was run for some combinations of specification set size and scopes to answer the paper's RQs. The pre-calculated results is available at [`results.txt`](results.txt).

```
python3 evaluation.py optimal 3 3 4 28
python3 evaluation.py nonoptimal 3 3 4 28
python3 evaluation.py optimal 3 7 16 16
python3 evaluation.py nonoptimal 3 7 16 16
```
