from Tree import NodeType, EFGParser    

"""
Consider a three-stage game. 
In the first stage, a chance event randomly selects either ``L'' or ``R'', each with a probability of 1/2. 
In the second stage, Player 1 observes this outcome and then selects either l or r. 
In the third stage, Player 1 must choose between ``A'', and ``B'', but at this point, she has forgotten the outcome of the first stage and only remembers her decision from the second stage. 
The payoffs in all outcomes are set to 0.
"""

# Constraints:
# Explicit payoffs are correct

paths_to_check = [
    (['L', 'l', 'A'], [0]),
    (['L', 'l', 'B'], [0]),
    (['L', 'r', 'A'], [0]),
    (['L', 'r', 'B'], [0]),
    (['R', 'l', 'A'], [0]),
    (['R', 'l', 'B'], [0]),
    (['R', 'r', 'A'], [0]),
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

after_switch_game_path =""

parser_gen = EFGParser()

gen_game = parser_gen.parse_file(after_switch_game_path)

def test_payoffs():
    print("Checking payoffs...")
    check_payoffs(gen_game)
    assert check_payoffs(gen_game) == True