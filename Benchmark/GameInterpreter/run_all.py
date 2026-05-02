from pathlib import Path
import argparse
import os
import re
import sys

from gpt import LLMBackend

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmark_dataset import load_games_from_dataset


parser = argparse.ArgumentParser()

parser.add_argument(
    "-m",
    "--model",
    type=str,
    default="gpt-5-mini",
    help="Model name to use.",
)

args = parser.parse_args()

if args.model in {"deepseek", "deepseek-chat"}:
    api_key = os.getenv("DEEPSEEK_API_KEY")
elif "/" in args.model:
    api_key = os.getenv("OPENROUTER_API_KEY")
else:
    api_key = os.getenv("OPENAI_API_KEY")

LLM = LLMBackend(api_key=api_key, model=args.model)

# === Settings ===
DATASET_DIR = os.getenv("BENCHMARK_DATASET_DIR", "../Dataset")
N_RUNS_PER_GAME = int(os.getenv("BENCHMARK_RUNS", "10"))


def sanitize_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    cleaned = cleaned.strip("._-")
    return cleaned or "game"


def build_game_folder_name(game_id, raw_game_name: str) -> str:
    safe_name = sanitize_name(raw_game_name)
    safe_id = sanitize_name(str(game_id)) if game_id is not None else "no_id"
    return f"{safe_id}_{safe_name}"


def main():
    games = load_games_from_dataset(DATASET_DIR, base_dir=Path.cwd())

    print(f"Number of games: {len(games)}")

    for game in games:
        raw_game_name = game.name
        description = game.description

        print(f"\n=== Processing: {raw_game_name} ===")

        try:
            LLM.infer_code(description, raw_game_name, N_RUNS_PER_GAME)
        except Exception as e:
            print(f"  [!] Generation failed for {folder_game_name}: {e}")
            continue


if __name__ == "__main__":
    main()
