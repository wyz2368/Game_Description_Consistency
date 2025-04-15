import os
from Algorithms import (
    check_order_preserving_equivalence,
    check_better_response_equivalence,
    check_best_response_equivalence,
    check_best_response_equivalence_multiprocessing,
    check_better_response_equivalence_multiprocessing
)
from utils import get_payoff_matrix, check_strategy_counts


def check_equivalence(reference_game, generated_game):
    results = []
    results.append("Order-preserving equivalence:")
    results.append(str(check_order_preserving_equivalence(reference_game, generated_game)))

    results.append("Better-response equivalence:")
    results.append(str(check_better_response_equivalence_multiprocessing(reference_game, generated_game)))

    results.append("Best-response equivalence:")
    results.append(str(check_best_response_equivalence_multiprocessing(reference_game, generated_game)))

    return "\n".join(results)

output_root = "Output"
dataset_root = "Dataset"
equivalence_root = "Output_Equivalence"

for game_type in ["Imperfect_Information_Games", "Perfect_Information_Games"]:
    game_type_path = os.path.join(output_root, game_type)
    if not os.path.isdir(game_type_path):
        continue

    for game_name in os.listdir(game_type_path):
        game_path = os.path.join(game_type_path, game_name)
        if not os.path.isdir(game_path):
            continue

        ref_path = os.path.join(dataset_root, game_type, game_name, "Reference", "ref.efg")
        if not os.path.exists(ref_path):
            print(f"Reference file not found for {game_type}/{game_name}, skipping.")
            continue

        for filename in os.listdir(game_path):
            if not filename.endswith(".efg"):
                continue

            gen_efg_path = os.path.join(game_path, filename)
            print(f"Checking equivalence for {gen_efg_path}...")

            try:
                reference_game = get_payoff_matrix(ref_path)
                generated_game = get_payoff_matrix(gen_efg_path)
                if not check_strategy_counts(reference_game, generated_game):
                    print(f"Strategy counts do not match for {gen_efg_path}, skipping equivalence check.")

                    output_txt_dir = os.path.join(equivalence_root, game_type, game_name)
                    os.makedirs(output_txt_dir, exist_ok=True)

                    output_txt_path = os.path.join(output_txt_dir, filename.replace(".efg", ".txt"))
                    with open(output_txt_path, "w") as f:
                        f.write("Strategy counts do not match between reference and generated game.\nEquivalence check skipped.")
                    continue

                result_text = check_equivalence(reference_game, generated_game)

                # Write results to output_equivalence/<game_type>/<game_name>/<file>.txt
                output_txt_dir = os.path.join(equivalence_root, game_type, game_name)
                os.makedirs(output_txt_dir, exist_ok=True)

                output_txt_path = os.path.join(output_txt_dir, filename.replace(".efg", ".txt"))
                with open(output_txt_path, "w") as f:
                    f.write(result_text)

                print(f"Saved equivalence check to {output_txt_path}")

            except Exception as e:
                print(f"Error processing {gen_efg_path}: {e}, skipping.")
