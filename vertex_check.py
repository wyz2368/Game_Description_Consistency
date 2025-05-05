from Algorithms import check_vertex_best_response, check_better_response
from utils import get_payoff_gambit

gen_path = "Output/Imperfect_Information_Games/Kuhn_Poker/5.efg"
ref_path = "Dataset/Imperfect_Information_Games/Kuhn_Poker/Reference/ref.efg"

generated_game = get_payoff_gambit(gen_path)
ref_game = get_payoff_gambit(ref_path)

print("Result: ", check_better_response(ref_game, generated_game))
