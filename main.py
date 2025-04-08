from Algorithms import check_best_response_equivalence, check_better_response_equivalence, check_order_preserving_equivalence
from Match import switch_order, match_player
from Tree import EFGParser, compare_chance_probs, compare_information_sets
from utils import get_payoff_matrix
import argparse
import importlib.util
import os

parser = argparse.ArgumentParser()

parser.add_argument('-m', '--models', type=str, default="gemini", help="Select the model to use: 'gpt', 'gemini' or 'deepseek'")
args = parser.parse_args()

model = args.models

def check_equivalence(reference_game, generated_game):
    print("Order-preserving equivalence:")
    print(check_order_preserving_equivalence(reference_game, generated_game))
    
    print("Better-response equivalence:")
    print(check_better_response_equivalence(reference_game, generated_game))

    print("Best-response equivalence:")
    print(check_best_response_equivalence(reference_game, generated_game))

# Step 1: Parse the EFG files
path = "Dataset/Imperfect_Information_Games/Bach_or_Stravinsky"
gen_efg_path = path + "Correct/1.efg"
ref_efg_path = path + "Reference/ref.efg"

parser_gen = EFGParser()
parser_ref = EFGParser()

gen_game = parser_gen.parse_file(gen_efg_path)
ref_game = parser_ref.parse_file(ref_efg_path)

# Step 2: Match players
match_player(gen_game, ref_game, model)

# Step 3: Read constraints needed for the game and import the constraints functions.
# Define the dynamic path
function_path = os.path.join(path, "Constraints", "functions.py")
# Dynamically load the module
spec = importlib.util.spec_from_file_location("functions", function_path)
functions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(functions)

with open(path + 'Constraints/constraints.txt', 'r') as file:
    constraints = [line.strip() for line in file]

if "player order" in constraints:
    if not functions.check_player_order(gen_game):
        raise ValueError("Player order is not correct.")

# Step 4: Switch the order of the players in the generated game if simlutaneous moves are involved
# At the same time, the name of the actions are mathed to the reference game
switch_order(ref_game.root, gen_game.root, model)

# save the mathed game
switch_gen_path = "output.efg"
parser_gen.save_to_efg("output.efg")

# Step 5: Check the strategic equivalence of the games
reference_game = get_payoff_matrix(ref_efg_path)
print(reference_game)
generated_game = get_payoff_matrix(switch_gen_path)
print(generated_game)

check_equivalence(reference_game, generated_game)

# Step 6: Check the chance probabilities and information sets if needed
compare_information_sets(ref_game, gen_game)
compare_chance_probs(ref_game, gen_game)