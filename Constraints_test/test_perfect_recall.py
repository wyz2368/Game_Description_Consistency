from Tree import NodeType, EFGParser, compare_information_sets, compare_chance_probs   

"""
Consider a three-stage game. In the first stage, a chance event randomly selects either ``L'' or ``R'', each with a probability of 1/2. In the second stage, Player 1 observes this outcome and then selects either l or r. In the third stage, Player 1 must choose between ``A'', and ``B'', and at this point, she remembers both the outcome of the first stage and her decision from the second stage. The payoffs at the end of the game depend on the full sequence of moves and are given as follows:
If the sequence is (L, l, A), Player 1 receives 3
If the sequence is (L, l, B), Player 1 receives 1
If the sequence is (L, r, A), Player 1 receives 0
If the sequence is (L, r, B), Player 1 receives 2
If the sequence is (R, l, A), Player 1 receives 4
If the sequence is (R, l, B), Player 1 receives 2
If the sequence is (R, r, A), Player 1 receives 1
If the sequence is (R, r, B), Player 1 receives 0
"""

# Constraints:
# Explicit payoffs are correct
# Check information set
# Check chance probabilities

paths_to_check = [
    (['L', 'l', 'A'], [3]),
    (['L', 'l', 'B'], [1]),
    (['L', 'r', 'A'], [0]),
    (['L', 'r', 'B'], [2]),
    (['R', 'l', 'A'], [4]),
    (['R', 'l', 'B'], [2]),
    (['R', 'r', 'A'], [1]),
    (['R', 'r', 'B'], [0])
]

def check_payoffs(game):
    """
    We need to check for all paths in the game tree, the payoffs are set to 0.
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

ref_game_path = ""
after_switch_game_path =""

parser_ref = EFGParser()
parser_gen = EFGParser()

ref_game = parser_ref.parse_file(ref_game_path)
gen_game = parser_gen.parse_file(after_switch_game_path)

def test_payoffs():
    print("Checking payoffs...")
    check_payoffs(gen_game)
    assert check_payoffs(gen_game) == True
    
def test_information_sets():
    print("Checking information sets...")
    assert compare_information_sets(ref_game, gen_game) == True
    
def test_chance():
    print("Checking chance probabilities...")
    assert compare_chance_probs(ref_game, gen_game) == True