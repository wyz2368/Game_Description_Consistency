from Algorithms import check_best_response_equivalence, check_better_response_equivalence, check_order_preserving_equivalence
from Match import match_actions, switch_order
from Tree import EFGParser
from utils import get_payoff_matrix

def check_equivalence(reference_game, generated_game):
    print("Order-preserving equivalence:")
    print(check_order_preserving_equivalence(reference_game, generated_game))
    
    print("Better-response equivalence:")
    print(check_better_response_equivalence(reference_game, generated_game))

    print("Best-response equivalence:")
    print(check_best_response_equivalence(reference_game, generated_game))

gen_efg_path = "Test_EFG/Gen/1.efg"
ref_efg_path = "Test_EFG/Ref/1.efg"

parser = EFGParser()

ref_game = parser.parse_file(ref_efg_path)
gen_game = parser.parse_file(gen_efg_path)

# gen_game.print_tree()

switch_order(ref_game.root, gen_game.root, gen_game)
match_actions(ref_game.root, gen_game.root)

gen_game.print_tree()

parser.save_to_efg("Test_EFG/Switch/output1.efg")

# switch_gen_path = "Test_EFG/Switch/output4.efg"

# reference_game = get_payoff_matrix(ref_efg_path)
# print(reference_game)
# generated_game = get_payoff_matrix(switch_gen_path)
# print(generated_game)

# check_equivalence(reference_game, generated_game)



