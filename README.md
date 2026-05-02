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

Export your OpenAI API key before running the GPT matcher:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

## Run The Evaluation

An example command is:

```bash
python match_and_check_all.py \
  --dataset_root Dataset \
  --generated_root Dataset_Check_Evaluator \
  --output_root Results/Output \
  --report_root Results/Check_Reports \
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

## Check The Evaluation

To check the evaluation, simply run:

```bash
./run_evaluation_checker.sh
```

## Data Format

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
