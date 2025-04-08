from Tree import NodeType

"""
A new manufacturer plans to enter the market, and its strength, determined by chance (not as a player decision), can be either strong (S) with probability 2/3 or weak (W) with probability 1/3. The new manufacturer will then send a signal, either strong (S) or weak (W). The current manufacturer does not know the new manufacturer’s actual strength but observes the signal, which could indicate either strong (S) or weak (W). Based on this signal, the current manufacturer must decide to either compete aggressively (F) or accommodate the new competitor (A). The payoffs for each scenario are as follows:
If the new manufacturer is strong and sends a strong signal, and the existing manufacturer chooses to fight, the payoffs are (1, 0) for the new and existing manufacturers, respectively. If the existing manufacturer adapts, the payoffs are (3, 1).
If the new manufacturer is strong and sends a weak signal, and the existing manufacturer chooses to fight, the payoff is (0, 0). If the existing manufacturer adapts, the payoff is (2, 1).
If the new manufacturer is weak and sends a strong signal, and the existing manufacturer chooses to fight, the payoff is (0, 2). If the existing manufacturer adapts, the payoff is (2, 1).
If the new manufacturer is weak and sends a weak signal, and the existing manufacturer chooses to fight, the payoff is (1, 2). If the existing manufacturer adapts, the payoff is (3, 1).
"""

paths_to_check = [
    (['Strong', 'Signal Strong', 'Fight'], [1, 0]),
    (['Strong', 'Signal Strong', 'Adapt'], [3, 1]),
    (['Strong', 'Signal Weak', 'Fight'], [0, 0]),
    (['Strong', 'Signal Weak', 'Adapt'], [2, 1]),
    (['Weak', 'Signal Strong', 'Fight'], [0, 2]),
    (['Weak', 'Signal Strong', 'Adapt'], [2, 1]),
    (['Weak', 'Signal Weak', 'Fight'], [1, 2]),
    (['Weak', 'Signal Weak', 'Adapt'], [3, 1])
]

def check_payoffs(game):
    """
    Each path in the game tree is checked against the expected payoffs in the game description.
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
