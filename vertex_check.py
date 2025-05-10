from Algorithms import check_vertex_best_response, check_better_response
from utils import get_payoff_gambit

# gen_path = "Output/Imperfect_Information_Games/Kuhn_Poker/5.efg"
# ref_path = "Dataset/Imperfect_Information_Games/Kuhn_Poker/Reference/ref.efg"

# generated_game = get_payoff_gambit(gen_path)
# ref_game = get_payoff_gambit(ref_path)

# print("Result: ", check_better_response(ref_game, generated_game))

gen_path = "two_player_game.efg"
ref_path = "Dataset_added/Imperfect_Information_Games/A_Two_Player_Game/Reference/ref.efg"
generated_game = get_payoff_gambit(gen_path)
print("Generated Game: ", generated_game)
ref_game = get_payoff_gambit(ref_path)
print("Reference Game: ", ref_game)

print("Result: ", check_vertex_best_response(ref_game, generated_game, "A_Two_Player_Game"))
# print("Result: ", check_better_response(ref_game, generated_game))