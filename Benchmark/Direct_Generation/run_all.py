from pathlib import Path
import argparse
from utils import infer_code
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmark_dataset import load_games_from_dataset, save_generated_efg_text

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="qwen/qwen3.5-35b-a3b")
    parser.add_argument("--dataset-dir", type=str, default="../Dataset")
    parser.add_argument("--output-root", type=str, default=None)
    parser.add_argument("--runs", type=int, default=10)
    return parser.parse_args()


def sanitize_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    cleaned = cleaned.strip("._-")
    return cleaned or "game"


def main():
    args = parse_args()
    output_root = Path(
        args.output_root
        or f"Direct_Generation_{sanitize_name(args.model)}_benchmark"
    )
    import os
    os.environ["BENCHMARK_MODEL"] = args.model

    output_root.mkdir(parents=True, exist_ok=True)

    games = load_games_from_dataset(args.dataset_dir, base_dir=Path.cwd())

    print(f"Number of games: {len(games)}")

    for game in games:
        game_name = game.name
        description = game.description
        folder_name = sanitize_name(game_name)
        game_out_dir = output_root / folder_name
        game_out_dir.mkdir(parents=True, exist_ok=True)

        metadata_file = game_out_dir / "metadata.json"
        with metadata_file.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "game_name": game_name,
                    "dataset_path": str(game.path),
                    "description_path": str(game.path / "description.txt"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"\n=== Processing: {game_name} ===")
        print(f"Output -> {game_out_dir.resolve()}")

        for i in range(1, args.runs + 1):
            try:
                efg_text = infer_code(description)
            except Exception as e:
                print(f"  [!] Generation {i} failed for {game_name}: {e}")
                continue

            out_file = game_out_dir / f"{i}.efg"
            try:
                with out_file.open("w", encoding="utf-8") as out_f:
                    out_f.write(efg_text)
                print(f"  Saved: {out_file.name}")
            except Exception as e:
                print(f"  [!] Could not write {out_file}: {e}")
                continue

            try:
                generated_path = save_generated_efg_text("Direct", game_name, efg_text)
                print(f"  Evaluation copy: {generated_path}")
            except Exception as e:
                print(f"  [!] Could not save evaluation copy: {e}")


if __name__ == "__main__":
    main()
  
