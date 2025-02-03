from Algorithms import order_preserving_equivalence, best_response_equivalence, better_response_equivalence
from utils import get_payoff_matrix

def check_equivalence(reference_game, generated_game):
    print("Order-preserving equivalence:")
    print(order_preserving_equivalence.check_order_preserving_equivalence(reference_game, generated_game))
    
    # print("Better-response equivalence:")
    # print(better_response_equivalence.check_better_response_equivalence(reference_game, generated_game))

    # print("Best-response equivalence:")
    # print(best_response_equivalence.check_best_response_equivalence(reference_game, generated_game))


# generated_game_path = "EFG/Setting D/GPT-4o/Imperfect Information Games/Bach or Stravinsky/Correct/1.efg"
# reference_game_path = "ReferenceGame/bach.efg"

# generated_game_path = "EFG/Setting D/GPT-4o/Perfect Information Games/Market Entry Model/Correct/5.efg"
# reference_game_path = "ReferenceGame/simple_market.efg"
    
# generated_game_path = "EFG/Setting D/GPT-4o/Imperfect Information Games/Nuclear Crisis/Correct/1.efg"
# reference_game_path = "ReferenceGame/nuclear_crisis.efg"
    
# generated_game_path = "test.efg"
# reference_game_path = "ReferenceGame/bach.efg"

generated_game_path = "EFG/Setting D/GPT-4/Imperfect Information Games/Bagwell/Incorrect/1.efg"
reference_game_path = "ReferenceGame/bagwell.efg"

# generated_game_path = "EFG/Setting C/GPT-4o/Imperfect Information Games/Extra Game Two/Correct/1.efg"
# reference_game_path = "EFG/Setting C/GPT-4o/Imperfect Information Games/Extra Game Two/Correct/2.efg"

# generated_game_path = "EFG/Setting D/GPT-4o/Imperfect Information Games/A Three-Player Game/Correct/1.efg"
# reference_game_path = "ReferenceGame/three_player.efg"


reference_game = get_payoff_matrix(reference_game_path)
print(reference_game)
generated_game = get_payoff_matrix(generated_game_path)
print(generated_game)

check_equivalence(reference_game, generated_game)



