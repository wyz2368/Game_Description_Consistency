from Tree import NodeType, EFGParser

"""
A chance node will select one of four possible outcomes: A, B, C, or D. 
After observing the result of the chance node, Player 1 will choose from three available actions: E, F, or G. In the following stage, Player 2, having observed Player 1's choice, will choose between two actions: Q or W. 
Payoffs are as follows: under A, Q gives (1, -1) and W gives (2, -2); under B, Q gives (3, -3) and W gives (-3, 3); under C, Q gives (0, 0) and W gives (-1, 1); and under D, Q gives (4, -4) and W gives (-4, 4). 
"""

# Constraints:
# Explicit payoffs are correct

paths_to_check = [
    (['A', 'E', 'Q'], [1, -1]),
    (['A', 'E', 'W'], [2, -2]),
    (['A', 'F', 'Q'], [1, -1]),
    (['A', 'F', 'W'], [2, -2]),
    (['A', 'G', 'Q'], [1, -1]),
    (['A', 'G', 'W'], [2, -2]),

    (['B', 'E', 'Q'], [3, -3]),
    (['B', 'E', 'W'], [-3, 3]),
    (['B', 'F', 'Q'], [3, -3]),
    (['B', 'F', 'W'], [-3, 3]),
    (['B', 'G', 'Q'], [3, -3]),
    (['B', 'G', 'W'], [-3, 3]),

    (['C', 'E', 'Q'], [0, 0]),
    (['C', 'E', 'W'], [-1, 1]),
    (['C', 'F', 'Q'], [0, 0]),
    (['C', 'F', 'W'], [-1, 1]),
    (['C', 'G', 'Q'], [0, 0]),
    (['C', 'G', 'W'], [-1, 1]),

    (['D', 'E', 'Q'], [4, -4]),
    (['D', 'E', 'W'], [-4, 4]),
    (['D', 'F', 'Q'], [4, -4]),
    (['D', 'F', 'W'], [-4, 4]),
    (['D', 'G', 'Q'], [4, -4]),
    (['D', 'G', 'W'], [-4, 4])
]

def check_payoffs(game):
    """
    We need to check the following explicit payoffs in the game tree:
    Payoffs are as follows: under A, Q gives (1, -1) and W gives (2, -2); under B, Q gives (3, -3) and W gives (-3, 3); under C, Q gives (0, 0) and W gives (-1, 1); and under D, Q gives (4, -4) and W gives (-4, 4). 
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
            raise ValueError(f"Path {path} does not lead to a terminal node.")
        elif terminal_node.payoffs != expected_payoff:
            raise ValueError(f"Path {path} leads to payoff {terminal_node.payoffs}, expected {expected_payoff}.")
        
        any_correct = True

    if any_correct:
        print("All path leads to the correct expected payoff.")
        return True
    else:
        raise ValueError("No path matched the expected payoffs.")

#========Test Functions Below===================================================================================

after_switch_game_path =""

parser_gen = EFGParser()

gen_game = parser_gen.parse_file(after_switch_game_path)

def test_payoffs():
    print("Checking payoffs...")
    check_payoffs(gen_game)
    assert check_payoffs(gen_game) == True