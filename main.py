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

gen_efg_path = "Test_EFG/Gen_EFG/output_gen.efg"
ref_efg_path = "Test_EFG/Ref_EFG/output_ref.efg"
# gen_efg_path = "Test_EFG/Gen_EFG/multiple_sim_gen.efg"
# ref_efg_path = "Test_EFG/Ref_EFG/multiple_sim.efg"

parser = EFGParser()

ref_game = parser.parse_file(ref_efg_path)
gen_game = parser.parse_file(gen_efg_path)

gen_game.print_tree()

switch_order(ref_game.root, gen_game.root)
# match_actions(ref_game.root, gen_game.root)

gen_game.print_tree()

# reference_game = get_payoff_matrix(ref_efg_path)
# print(reference_game)
# generated_game = get_payoff_matrix(gen_efg_path)
# print(generated_game)

# check_equivalence(reference_game, generated_game)



