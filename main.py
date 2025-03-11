from Algorithms import check_best_response_equivalence, check_better_response_equivalence, check_order_preserving_equivalence
from Match import switch_order, match_player
from Tree import EFGParser
from utils import get_payoff_matrix

def check_equivalence(reference_game, generated_game):
    print("Order-preserving equivalence:")
    print(check_order_preserving_equivalence(reference_game, generated_game))
    
    print("Better-response equivalence:")
    print(check_better_response_equivalence(reference_game, generated_game))

    print("Best-response equivalence:")
    print(check_best_response_equivalence(reference_game, generated_game))

# gen_efg_path = "Test_EFG/Incorrect/Gen/3.efg"
# ref_efg_path = "Test_EFG/Incorrect/Ref/3.efg"

gen_efg_path = "Test_EFG/Correct/Gen/1.efg"
ref_efg_path = "Test_EFG/Correct/Ref/1.efg"

parser = EFGParser()

ref_game = parser.parse_file(ref_efg_path)
gen_game = parser.parse_file(gen_efg_path)

# gen_game.print_tree()
match_player(gen_game, ref_game)
switch_order(ref_game.root, gen_game.root, gen_game)

# parser.save_to_efg("Test_EFG/Incorrect/Switch/output3.efg")
parser.save_to_efg("Test_EFG/Correct/Switch/output1.efg")

# switch_gen_path = "Test_EFG/Switch/output4.efg"

# reference_game = get_payoff_matrix(ref_efg_path)
# print(reference_game)
# generated_game = get_payoff_matrix(switch_gen_path)
# print(generated_game)

# check_equivalence(reference_game, generated_game)



