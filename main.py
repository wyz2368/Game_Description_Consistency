from Algorithms import check_best_response_equivalence, check_better_response_equivalence, check_order_preserving_equivalence
from Match import switch_order, match_player
from Tree import EFGParser, compare_outcomes, compare_chance_probs, compare_information_sets
from utils import get_payoff_matrix
from Dataset.Constraints import check_bach_game_outcomes

def check_equivalence(reference_game, generated_game):
    print("Order-preserving equivalence:")
    print(check_order_preserving_equivalence(reference_game, generated_game))
    
    print("Better-response equivalence:")
    print(check_better_response_equivalence(reference_game, generated_game))

    print("Best-response equivalence:")
    print(check_best_response_equivalence(reference_game, generated_game))

gen_efg_path = "Dataset/Imperfect Information Games/Bach or Stravinsky/Correct/1.efg"
ref_efg_path = "Dataset/Imperfect Information Games/Bach or Stravinsky/Reference/ref.efg"

parser_gen = EFGParser()
parser_ref = EFGParser()

gen_game = parser_gen.parse_file(gen_efg_path)
ref_game = parser_ref.parse_file(ref_efg_path)

match_player(gen_game, ref_game)
switch_order(ref_game.root, gen_game.root)

parser_gen.save_to_efg("output.efg")

switch_gen_path = "output.efg"

reference_game = get_payoff_matrix(ref_efg_path)
print(reference_game)
generated_game = get_payoff_matrix(switch_gen_path)
print(generated_game)

check_equivalence(reference_game, generated_game)

# Additional constraints

path = parser_gen.collect_paths_to_terminal()
print(path)
print("Outcome", check_bach_game_outcomes(path))

# compare_information_sets(ref_game, gen_game)
# compare_chance_probs(ref_game, gen_game)