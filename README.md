# Game Description Consistency

## Setup

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

## Run Benchmarks

First export your API key:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

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

Benchmark outputs are in the following format:

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

By default, `run_evaluation_checker.sh` evaluates `Benchmark/Dataset_Generate/Direct` with `20` generations and `gpt-5-mini`.

You can also pass the benchmark method, number of generations, and OpenAI model:

```bash
./run_evaluation_checker.sh GameInterpreter 20 gpt-5-mini
./run_evaluation_checker.sh Iterative 20 gpt-5-mini
./run_evaluation_checker.sh MCP 20 gpt-5-mini
./run_evaluation_checker.sh Direct 20 gpt-5-mini
```

Arguments:

- `--dataset_root`: folder containing reference games.
- `--generated_root`: folder containing generated `.efg` samples.
- `--output_root`: folder where matched `.efg` files are saved.
- `--report_root`: folder where per-sample reports and `summary.txt` are saved.
- `--num_generations`, `-n`: required number of generated samples per game.
- `--model`, `-m`: OpenAI model used for matching. The default is `gpt-5-mini`.