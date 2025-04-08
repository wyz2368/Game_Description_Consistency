from Tree import NodeType

"""
You’re playing a two-player paper-and-pencil game, where players take turns marking a three-by-three grid with either an "x" or an "o." The objective is to get three of your marks in a row, column, or diagonal to win.
The winner gains 1 point, while the loser loses 1 point.
Assuming "e" represents empty, the current board state is: 
e | o | e
e | x | o
x | x | o
The next move is "x" 

The game tree could be generated as follows:
"x" can place the mark on (0,0), (0,2) and (1,0).
If "x" places the mark on (0,0), 
   "o" can then place the mark on (0,2) and (1,0).
   If "o" places the mark on (0,2), "o" wins.
   If "o" places the mark on (1,0), 
      "x" can then place the mark on (0,2), 
      If "x" places the mark on (0,2), "x" wins.
If "x" places the mark on (0,2), "x" wins.
If "x" places the mark on (1,0), 
   "o" can then place the mark on (0,0) and (0,2).
   If "o" places the mark on (0,0), 
      "x" can then place the mark on (0,2), 
      If "x" places the mark on (0,2), "x" wins.
   If "o" places the mark on (0,2), "o" wins.
"""

paths_to_check = [
    (['(0,0)', '(0,2)'], [-1, 1]),
    (['(0,0)', '(1,0)', '(0,2)'], [1, -1]),
    (['(0,2)'], [1, -1]),
    (['(1,0)', '(0,0)', '(0,2)'], [1, -1]),
    (['(1,0)', '(0,2)'], [-1, 1])
]

def check_payoffs(game):
    """
    Each path in the game tree is checked against the expected payoffs in the game description.
    Payoff: The winner gains 1 point, while the loser loses 1 point.
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
