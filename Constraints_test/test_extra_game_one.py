from Tree import NodeType, EFGParser

"""
In the first stage, Player 1 can choose among three actions: A, B, or C. In the second stage, Player 2 knows when action A was taken, but otherwise cannot tell whether B or C was taken. 
At this point, Player 2 has three options: D, E, and F. Selecting F ends the game. 
If Player 2 chooses either D or E, the game advances to the third stage, where Player 1 has a choice between actions G and H. 
Selecting H ends the game and player 1 gets payoff 2 and player 2 gets payoff -1. 
If Player 1 instead chooses G, Player 2 then decides between actions Q and W, with both players getting 3 after Q, and both players getting 0 after W.
"""

# Constraints:
# Explicit payoffs are correct

paths_to_check = [
    (['A', 'D', 'G', 'Q'], [3, 3]),
    (['A', 'D', 'G', 'W'], [0, 0]),
    (['A', 'D', 'H'], [2, -1]),
    (['A', 'E', 'G', 'Q'], [3, 3]),
    (['A', 'E', 'G', 'W'], [0, 0]),
    (['A', 'E', 'H'], [2, -1]),

    (['B', 'D', 'G', 'Q'], [3, 3]),
    (['B', 'D', 'G', 'W'], [0, 0]),
    (['B', 'D', 'H'], [2, -1]),
    (['B', 'E', 'G', 'Q'], [3, 3]),
    (['B', 'E', 'G', 'W'], [0, 0]),
    (['B', 'E', 'H'], [2, -1]),

    (['C', 'D', 'G', 'Q'], [3, 3]),
    (['C', 'D', 'G', 'W'], [0, 0]),
    (['C', 'D', 'H'], [2, -1]),
    (['C', 'E', 'G', 'Q'], [3, 3]),
    (['C', 'E', 'G', 'W'], [0, 0]),
    (['C', 'E', 'H'], [2, -1]),
]

def check_payoffs(game):
    """
    We need to check the following explicit payoffs in the game tree:
    Selecting H ends the game and player 1 gets payoff 2 and player 2 gets payoff -1. 
    If Player 1 instead chooses G, Player 2 then decides between actions Q and W, with both players getting 3 after Q, and both players getting 0 after W.

    Game description doesn't constrain the payoffs for the paths ['A', 'F'], ['B', 'F'], ['C', 'F'], so we don't check them.
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