import os
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from benchmark_dataset import copy_generated_efg, load_games_from_dataset

from utils import (
    classify_game_with_llm,
    load_efg_from_dir,
    extract_player_actions_dict,
    make_perfect_information,
)
from oracle import assign_information_sets_with_labels
from Tree_Infer import infer_game_tree_CoT

DATASET_DIR = os.getenv("BENCHMARK_DATASET_DIR", "../Dataset")
OUTPUT_DIR = os.getenv("BENCHMARK_OUTPUT_DIR", "Benchmark_iterative")
RUNS_PER_GAME = int(os.getenv("BENCHMARK_RUNS", "10"))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run game tree inference over all game descriptions in a JSONL dataset."
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gpt-5-mini",
        help="Model name to use for inference.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=1.0 if "/" in os.getenv("BENCHMARK_MODEL", "gpt-5-mini") else 0.7,
        help="Generation temperature.",
    )

    return parser.parse_args()


def infer_game_tree(
    description,
    output_dir,
    model,
    temperature=0.0,
):
    return infer_game_tree_CoT(
        game_description=description,
        output_dir=output_dir,
        model=model,
        temperature=temperature,
    )


def safe_name(text: str) -> str:
    keep = []
    for ch in text:
        if ch.isalnum() or ch in ("-", "_", " "):
            keep.append(ch)
        else:
            keep.append("_")
    return "".join(keep).strip().replace(" ", "_")


if __name__ == "__main__":
    args = parse_args()

    # if not os.getenv("OPENAI_API_KEY"):
    #     raise RuntimeError("OPENAI_API_KEY is not set. Please export it before running.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    games = load_games_from_dataset(DATASET_DIR, base_dir=Path.cwd())

    print(f"Number of games: {len(games)}")

    for game in games:
        game_name = game.name
        description = game.description
        folder_name = safe_name(game_name)

        print(f"\n=== Game: {game_name} ===")
        print(f"Dataset path: {game.path}")

        game_dir = os.path.join(OUTPUT_DIR, folder_name)
        os.makedirs(game_dir, exist_ok=True)

        metadata_path = os.path.join(game_dir, "metadata.txt")
        with open(metadata_path, "w", encoding="utf-8") as f:
            f.write(f"game_name: {game_name}\n")
            f.write(f"dataset_path: {game.path}\n")
            f.write(f"description_path: {game.path / 'description.txt'}\n")

        description_path = os.path.join(game_dir, "description.txt")
        with open(description_path, "w", encoding="utf-8") as f:
            f.write(description)

        for i in range(1, RUNS_PER_GAME + 1):
            run_dir = os.path.join(game_dir, f"run_{i}")
            os.makedirs(run_dir, exist_ok=True)

            print(f"  Run {i}/{RUNS_PER_GAME} -> {run_dir} [model={args.model}]")

            try:
                info_type = classify_game_with_llm(
                    description,
                    model=args.model,
                    temperature=args.temperature,
                )
                print(f"Game info type: {info_type}")

                ok = infer_game_tree(
                    description=description,
                    output_dir=run_dir,
                    model=args.model,
                    temperature=args.temperature,
                )

                if ok == 1 and info_type == "perfect":
                    g, _ = load_efg_from_dir(run_dir)
                    g = make_perfect_information(g)

                    labeled_efg_path = os.path.join(run_dir, "game.efg")
                    g.to_efg(labeled_efg_path)
                    try:
                        generated_path = copy_generated_efg("Iterative", game_name, labeled_efg_path)
                        print(f"  Evaluation copy: {generated_path}")
                    except Exception as copy_error:
                        print(f"  [!] Could not save evaluation copy: {copy_error}")

                if ok == 1 and info_type != "perfect":
                    g, _ = load_efg_from_dir(run_dir)
                    g = make_perfect_information(g)

                    player_actions_dict = extract_player_actions_dict(g)
                    print("player_actions_dict:", player_actions_dict)

                    max_retries = 5 # Set a Max retry number for information set assignment
                    last_error = None

                    for attempt in range(1, max_retries + 1):
                        try:
                            assign_information_sets_with_labels(
                                g=g,
                                game_description=description,
                                player_actions_dict=player_actions_dict,
                                model=args.model,
                                temperature=args.temperature,
                                log_dir=run_dir,
                            )
                            break

                        except Exception as e:
                            last_error = e
                            print(
                                f"  [RETRY INFOSETS] Error in assign_information_sets_with_labels "
                                f"for {game_name} run {i}, attempt {attempt}/{max_retries}: {e}"
                            )

                            if attempt == max_retries:
                                raise last_error

                    labeled_efg_path = os.path.join(run_dir, "game.efg")
                    g.to_efg(labeled_efg_path)
                    try:
                        generated_path = copy_generated_efg("Iterative", game_name, labeled_efg_path)
                        print(f"  Evaluation copy: {generated_path}")
                    except Exception as copy_error:
                        print(f"  [!] Could not save evaluation copy: {copy_error}")

            except Exception as e:
                print(f"  [SKIP RUN] Error in {game_name} run {i}: {e}")

    print("\nAll games finished.")
