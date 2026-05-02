# Game Description Consistency

## Setup

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

For a faster version of `pygambit`, install the local copy from this repository. This is intentionally not included in `requirements.txt`.

```bash
cd gambit
pip install .
cd ..
```

We provide a test dataset to demonstrate that our framework can correctly identify both correct and incorrect EFGs.

To run the test, first export your API key:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

Then run the evaluation script:

```bash
bash run_evaluation_test.sh
```

## Pipeline

### Run Benchmarks

The benchmark launcher supports four generation methods:

- `direct`
- `gameinterpreter`
- `iterative`
- `mcp`

Use the unified benchmark runner:

```bash
python Benchmark/benchmark_runner.py --method <method> --model <model>
```

Useful options:

- `--method`: one of `direct`, `gameinterpreter`, `iterative`, `mcp`
- `--model`: model to benchmark, for example `gpt-5-mini`
- `--runs`: number of runs per game, default `10`
- `--dataset-dir`: dataset directory
- `--output-dir`: optional custom benchmark output folder name

Run direct generation with GPT:

```bash
python Benchmark/benchmark_runner.py \
  --method direct \
  --model gpt-5-mini \
  --runs 5 \
  --dataset-dir ../Dataset
```

Run MCP with GPT:

```bash
python Benchmark/benchmark_runner.py \
  --method mcp \
  --model gpt-5-mini \
  --runs 5 \
  --dataset-dir ../Dataset
```

Run GameInterpreter with GPT:

```bash
python Benchmark/benchmark_runner.py \
  --method gameinterpreter \
  --model gpt-5-mini \
  --runs 5 \
  --dataset-dir ../Dataset
```

Run iterative generation with GPT:

```bash
python Benchmark/benchmark_runner.py \
  --method iterative \
  --model gpt-5-mini \
  --runs 5 \
  --dataset-dir ../Dataset
```

Benchmark outputs are copied into:

```text
Benchmark/Dataset_Generate/
├── Direct/
├── GameInterpreter/
├── Iterative/
└── MCP/
```

### Evaluation

Export your OpenAI API key before running the Evaluation.

Then run the evaluation checker:

```bash
./run_evaluation_checker.sh
```

By default, `run_evaluation_checker.sh` evaluates `Benchmark/Dataset_Generate/Direct` with `5` generations and `gpt-5-mini`.

You can also pass the benchmark method, number of generations, and OpenAI model:

```bash
./run_evaluation_checker.sh GameInterpreter 5 gpt-5-mini
./run_evaluation_checker.sh Iterative 5 gpt-5-mini
./run_evaluation_checker.sh MCP 5 gpt-5-mini
```

The equivalent direct evaluation command is:

```bash
python match_and_check_all.py \
  --dataset_root Dataset \
  --generated_root Benchmark/Dataset_Generate/Direct \
  --output_root Results/Direct/Output \
  --report_root Results/Direct/Check_Reports \
  --num_generations 5 \
  -m gpt-5-mini
```

Arguments:

- `--dataset_root`: folder containing reference games.
- `--generated_root`: folder containing generated `.efg` samples.
- `--output_root`: folder where matched `.efg` files are saved.
- `--report_root`: folder where per-sample reports and `summary.txt` are saved.
- `--num_generations`, `-n`: required number of generated samples per game. This is used to calculate pass@N.
- `--model`, `-m`: OpenAI model used for matching. The default is `gpt-5-mini`.

`--num_generations` is required because the final summary reports pass@N.

## Data Format for Evaluation

Each reference game folder under `Dataset/` should look like:

```text
Dataset/
└── {Game_Name}/
    ├── game.efg
    ├── description.txt
    ├── metadata.yml
    └── constraints/
        └── *.json
```

Each generated game folder should contain `.efg` samples:

```text
Dataset_Generate/
└── {Game_Name}/
    ├── 1.efg
    ├── 2.efg
    └── 3.efg
```
