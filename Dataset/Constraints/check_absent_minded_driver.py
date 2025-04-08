from Tree import NodeType

"""
At junction X, an absent-minded driver has two choices: EXIT, reaching destination A with a payoff of 0, or CONTINUE to junction Y. 
At junction Y, the driver can choose to EXIT, arriving at destination B with a payoff of 4, or CONTINUE to C, which yields a payoff of 1. 
The key assumption is that the driver cannot tell the difference between junctions X and Y and does not remember if he has already passed one of them.
"""

paths_to_check = [
    (['EXIT'], [0]),
    (['CONTINUE', 'EXIT'], [4]),
    (['CONTINUE', 'CONTINUE'], [1])
]

def check_payoffs(game):
    """
    The payoffs are explicitly defined in the game tree as shown in the paths_to_check list.
    We need to chek the payoffs for each path in the generated game tree are correct.
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
