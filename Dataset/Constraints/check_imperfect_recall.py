from Tree import NodeType

"""
Consider a three-stage game. 
In the first stage, a chance event randomly selects either ``L'' or ``R'', each with a probability of 1/2. 
In the second stage, Player 1 observes this outcome and then selects either l or r. 
In the third stage, Player 1 must choose between ``A'', and ``B'', but at this point, she has forgotten the outcome of the first stage and only remembers her decision from the second stage. 
The payoffs in all outcomes are set to 0.
"""

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
            raise ValueError(f"Path {path} does not lead to a terminal node.")
        elif terminal_node.payoffs != expected_payoff:
            raise ValueError(f"Path {path} leads to payoff {terminal_node.payoffs}, expected {expected_payoff}.")
        
        any_correct = True

    if any_correct:
        print("All path leads to the correct expected payoff.")
        return True
    else:
        raise ValueError("No path matched the expected payoffs.")