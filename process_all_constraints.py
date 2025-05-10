import os
import importlib.util
from natsort import natsorted  # For natural filename sorting

output_root = "Output"
constraints_root = "Constraints"
dataset_root = "Dataset"
constraints_output_root = "Output_Constraints"

# Loop through game types
for game_type in ["Imperfect_Information_Games", "Perfect_Information_Games"]:
    game_type_path = os.path.join(output_root, game_type)
    if not os.path.isdir(game_type_path):
        continue

    for game_name in os.listdir(game_type_path):
        game_path = os.path.join(game_type_path, game_name)
        if not os.path.isdir(game_path):
            continue

        test_module_name = "test_" + game_name.lower()
        test_module_path = os.path.join(constraints_root, f"{test_module_name}.py")

        if not os.path.exists(test_module_path):
            print(f"No constraint test for {game_name}, skipping.")
            continue

        # Load test module
        spec = importlib.util.spec_from_file_location(test_module_name, test_module_path)
        test_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(test_module)
        except Exception as e:
            print(f"Failed to load test module for {game_name}: {e}")
            continue

        if not hasattr(test_module, "test_constraints"):
            print(f"'test_constraints' not found in {test_module_path}, skipping.")
            continue

        ref_game_path = os.path.join(dataset_root, game_type, game_name, "Reference", "ref.efg")
        if not os.path.exists(ref_game_path):
            print(f"Missing ref.efg for {game_name}, skipping.")
            continue

        # Get sorted .efg files
        efg_files = [f for f in os.listdir(game_path) if f.endswith(".efg")]
        efg_files = natsorted(efg_files)

        result_lines = []
        for filename in efg_files:
            output_efg_path = os.path.join(game_path, filename)

            # Determine original file path (Correct or Incorrect)
            correct_path = os.path.join(dataset_root, game_type, game_name, "Correct", filename)
            incorrect_path = os.path.join(dataset_root, game_type, game_name, "Incorrect", filename)
            original_efg_path = correct_path if os.path.exists(correct_path) else incorrect_path

            print(f"Testing constraints on {output_efg_path}...")

            try:
                result = test_module.test_constraints(ref_game_path, output_efg_path, original_efg_path)
                result_lines.append(f"{filename} {result}")
            except Exception as e:
                print(f"Error testing {output_efg_path}: {e}")
                result_lines.append(f"{filename} ERROR")

        # Save to Output_Constraints/<Game_Type>/<Game_Name>.txt
        output_dir = os.path.join(constraints_output_root, game_type)
        os.makedirs(output_dir, exist_ok=True)
        result_txt_path = os.path.join(output_dir, f"{game_name}.txt")
        with open(result_txt_path, "w") as f:
            f.write("\n".join(result_lines))

        print(f"Saved constraint check results to {result_txt_path}")

