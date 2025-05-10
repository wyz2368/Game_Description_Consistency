import os
import argparse
from Match import switch_order, match_player
from Tree import EFGParser

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--models', type=str, default="gemini", help="Select the model to use: 'gpt', 'gemini' or 'deepseek'")
args = parser.parse_args()
model = args.models

dataset_root = "Dataset"
output_root = "Output"

# Iterate through both game type folders
for game_type in ["Imperfect_Information_Games", "Perfect_Information_Games"]:
    game_type_path = os.path.join(dataset_root, game_type)
    if not os.path.isdir(game_type_path):
        continue

    # Iterate through each game under that type
    for game_name in os.listdir(game_type_path):
        game_path = os.path.join(game_type_path, game_name)
        if not os.path.isdir(game_path):
            continue

        ref_path = os.path.join(game_path, "Reference", "ref.efg")
        if not os.path.exists(ref_path):
            print(f"Reference file not found for game: {game_type}/{game_name}, skipping.")
            continue

        for subfolder in ["Correct", "Incorrect"]:
            subfolder_path = os.path.join(game_path, subfolder)
            if not os.path.isdir(subfolder_path):
                continue

            for filename in os.listdir(subfolder_path):
                if not filename.endswith(".efg"):
                    continue

                gen_efg_path = os.path.join(subfolder_path, filename)
                print(f"Processing {gen_efg_path}...")

                try:
                    parser_gen = EFGParser()
                    parser_ref = EFGParser()

                    gen_game = parser_gen.parse_file(gen_efg_path)
                    ref_game = parser_ref.parse_file(ref_path)

                    match_player(gen_game, ref_game, model)
                    switch_order(ref_game.root, gen_game.root, model)

                    # Save output under Output/{game_type}/{game_name}/{filename}
                    output_dir = os.path.join(output_root, game_type, game_name)
                    os.makedirs(output_dir, exist_ok=True)

                    output_path = os.path.join(output_dir, filename)
                    parser_gen.save_to_efg(output_path)
                    print(f"Saved to {output_path}")

                except ValueError as ve:
                    print(f"ValueError in {gen_efg_path}: {ve}, skipping.")
                except Exception as e:
                    print(f"Unexpected error in {gen_efg_path}: {e}, skipping.")

