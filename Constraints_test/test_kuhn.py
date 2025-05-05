from Tree import NodeType, EFGParser, compare_chance_probs

"""
This is a two-player card game between Alice and Bob, using a deck of only three cards: a King, Queen, and Jack. 
Each player contributes 1 to the pot at the start. 

Each player is dealt one of the three cards, and the third is put aside unseen by a chance node.
There are six possible allocations of the cards, each with probability 1/6: JQ, JK, QJ, QK, KJ, and KQ.

The game proceeds as follows for each of the six possible allocations:
Alice can check or bet 1, WITHOUT knowing the allocation of the chance node.

    If Alice checks then Bob can check or bet 1, WITHOUT knowing Alice’s card.
        If Bob checks, the game ends (i.e. the higher card wins 1 from the other player).

        If Bob bets then Alice can fold or call, WITHOUT knowing Bob's card.
            If Alice folds then Bob takes the pot of 3 (i.e. winning 1 from player 1).
            If Alice calls, the game ends. (i.e. the higher card wins 2 from the other player).
            
    If Alice bets then Bob can fold or call, WITHOUT knowing the Alice's card.
        If Bob folds then Alice takes the pot of 3 (i.e. winning 1 from player 2).
        If Bob calls, the game ends. (i.e. the higher card wins 2 from the other player).
"""

# Constraints:
# Explicit payoffs are correct
# Check chance probabilities

paths_to_check = [
    (['J-Q', 'check', 'check'], [-1, 1]),
    (['J-Q', 'check', 'bet', 'fold'], [-1, 1]),
    (['J-Q', 'check', 'bet', 'call'], [-2, 2]),
    (['J-Q', 'bet', 'fold'], [1, -1]),
    (['J-Q', 'bet', 'call'], [-2, 2]),

    (['J-K', 'check', 'check'], [-1, 1]),
    (['J-K', 'check', 'bet', 'fold'], [-1, 1]),
    (['J-K', 'check', 'bet', 'call'], [-2, 2]),
    (['J-K', 'bet', 'fold'], [1, -1]),
    (['J-K', 'bet', 'call'], [-2, 2]),

    (['Q-J', 'check', 'check'], [1, -1]),
    (['Q-J', 'check', 'bet', 'fold'], [-1, 1]),
    (['Q-J', 'check', 'bet', 'call'], [2, -2]),
    (['Q-J', 'bet', 'fold'], [1, -1]),
    (['Q-J', 'bet', 'call'], [2, -2]),

    (['Q-K', 'check', 'check'], [-1, 1]),
    (['Q-K', 'check', 'bet', 'fold'], [-1, 1]),
    (['Q-K', 'check', 'bet', 'call'], [-2, 2]),
    (['Q-K', 'bet', 'fold'], [1, -1]),
    (['Q-K', 'bet', 'call'], [-2, 2]),

    (['K-J', 'check', 'check'], [1, -1]),
    (['K-J', 'check', 'bet', 'fold'], [-1, 1]),
    (['K-J', 'check', 'bet', 'call'], [2, -2]),
    (['K-J', 'bet', 'fold'], [1, -1]),
    (['K-J', 'bet', 'call'], [2, -2]),

    (['K-Q', 'check', 'check'], [1, -1]),
    (['K-Q', 'check', 'bet', 'fold'], [-1, 1]),
    (['K-Q', 'check', 'bet', 'call'], [2, -2]),
    (['K-Q', 'bet', 'fold'], [1, -1]),
    (['K-Q', 'bet', 'call'], [2, -2])
]

def check_payoffs(game):
    """
    We need to check for each path, the winning pots and losing pots are correct.
    """
    def traverse_path(node, path):
        current = node
        for action in path:
            if action not in current.children:
                return None
            current = current.children[action]
        return current if current.node_type == NodeType.TERMINAL else None

    any_correct = False  # Start assuming none are correct

    for path, expected_payoff in paths_to_check:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            print(f"Path {path} does not lead to a terminal node.")
            return False
        elif terminal_node.payoffs != expected_payoff:
            print(f"Path {path} leads to payoff {terminal_node.payoffs}, expected {expected_payoff}.")
            return False
        
        any_correct = True

    if any_correct:
        print("All path leads to the correct expected payoff.")
        return True
    else:
        print("No path matched the expected payoffs.")
        return False


#========Test Functions Below===================================================================================

after_switch_game_path ="Output/Imperfect_Information_Games/Kuhn_Poker/5.efg"
# ref_path = ""

# parser_ref = EFGParser()
parser_gen = EFGParser()

gen_game = parser_gen.parse_file(after_switch_game_path)
# ref_game = parser_ref.parse_file(ref_path)

def test_payoffs():
    print("Checking payoffs...")
    check_payoffs(gen_game)
    assert check_payoffs(gen_game) == True

# def test_chance():
#     print("Checking chance probabilities...")
#     assert compare_chance_probs(ref_game, gen_game) == True
