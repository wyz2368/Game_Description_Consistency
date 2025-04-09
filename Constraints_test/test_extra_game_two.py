from Tree import NodeType, EFGParser

"""
In the first stage, Player 1 has three options: A, B, and C. 
In the second stage, Player 2, without knowing Player 1's choice, can select either D or E. 
In the third stage, Player 1 has two actions to choose from: F or G. 
Finally, in the fourth stage, Player 3 can decide between actions Q and W. 
If Player 3 selects Q in the final stage, all players receive a payoff of 3. 
However, if Player 3 opts for W, Player 1 and Player 2 each receive a payoff of 2, while Player 3 gets 3.
"""

# Constraints:
# Explicit payoffs are correct

paths_to_check = [
    (['A', 'D', 'F', 'Q'], [3, 3, 3]),
    (['A', 'D', 'F', 'W'], [2, 2, 3]),
    (['A', 'D', 'G', 'Q'], [3, 3, 3]),
    (['A', 'D', 'G', 'W'], [2, 2, 3]),
    (['A', 'E', 'F', 'Q'], [3, 3, 3]),
    (['A', 'E', 'F', 'W'], [2, 2, 3]),
    (['A', 'E', 'G', 'Q'], [3, 3, 3]),
    (['A', 'E', 'G', 'W'], [2, 2, 3]),
    
    (['B', 'D', 'F', 'Q'], [3, 3, 3]),
    (['B', 'D', 'F', 'W'], [2, 2, 3]),
    (['B', 'D', 'G', 'Q'], [3, 3, 3]),
    (['B', 'D', 'G', 'W'], [2, 2, 3]),
    (['B', 'E', 'F', 'Q'], [3, 3, 3]),
    (['B', 'E', 'F', 'W'], [2, 2, 3]),
    (['B', 'E', 'G', 'Q'], [3, 3, 3]),
    (['B', 'E', 'G', 'W'], [2, 2, 3]),

    (['C', 'D', 'F', 'Q'], [3, 3, 3]),
    (['C', 'D', 'F', 'W'], [2, 2, 3]),
    (['C', 'D', 'G', 'Q'], [3, 3, 3]),
    (['C', 'D', 'G', 'W'], [2, 2, 3]),
    (['C', 'E', 'F', 'Q'], [3, 3, 3]),
    (['C', 'E', 'F', 'W'], [2, 2, 3]),
    (['C', 'E', 'G', 'Q'], [3, 3, 3]),
    (['C', 'E', 'G', 'W'], [2, 2, 3])
]

def check_payoffs(game):
    """
    We need to check the following explicit payoffs in the game tree:
    If Player 3 selects Q in the final stage, all players receive a payoff of 3. 
    However, if Player 3 opts for W, Player 1 and Player 2 each receive a payoff of 2, while Player 3 gets 3.
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