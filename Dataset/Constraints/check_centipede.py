from Tree import NodeType

"""
Consider a game with two players, Alice and Bob, where Alice makes the first move. 
At the start, Alice has two piles of coins in front of her: one pile with 4 coins and another with 1 coin. 
Each player has two options on their turn: they can either take the larger pile, giving the smaller pile to the other player, or they can push both piles to the other player. 
Whenever the piles are pushed across the table, the number of coins in each pile doubles. 
For instance, if Alice chooses to push on her first turn, the piles of 1 and 4 coins are handed over to Bob, increasing to 2 and 8 coins. 
Bob can then decide either to take the pile of 8 coins and leave 2 for Alice or to push the piles back to Alice, further doubling them to 4 and 16 coins. 
If neither player takes the coins by the end of the game, Alice will receive the pile with the higher value, and Bob will get the one with the lower value. 
The game has four moves in total: Alice moves (take or push), Bob moves (take or push, where the final push also doubles the piles before the game ends), Alice moves again, and finally, Bob moves. 
All actions are visible to both players.
"""

paths_to_check = [
    (['take'], [4, 1]),
    (['push', 'take'], [2, 8]),
    (['push', 'push', 'take'], [16, 4]),
    (['push', 'push', 'push', 'take'], [8, 32]),
    (['push', 'push', 'push', 'push'], [64, 16])
]

def check_payoffs(game):
    """
    The game start with one pile with 4 coins and another with 1 coin so the payoff are explicitly defined.
    Then, we need to check all the payoffs in the game tree.
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
