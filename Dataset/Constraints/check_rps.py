from Tree import NodeType

"""
Both players simultaneously reveal one of three symbols: rock, paper, or scissors. 
Rock defeats scissors by blunting it, scissors defeat paper by cutting it, and paper defeats rock by covering it.
"""

paths_to_check = [
    ['Rock', 'Rock'],
    ['Rock', 'Paper'],
    ['Rock', 'Scissors'],
    ['Paper', 'Rock'],
    ['Paper', 'Paper'],
    ['Paper', 'Scissors'],
    ['Scissors', 'Rock'],
    ['Scissors', 'Paper'],
    ['Scissors', 'Scissors']
]

def check_payoffs(game):
    """
    Because the game is zero-sum and the game description doesn't give the explicit values, we have to check the payoffs of each path.
    """
    def traverse_path(node, path):
        current = node
        for action in path:
            if action not in current.children:
                return None
            current = current.children[action]
        return current if current.node_type == NodeType.TERMINAL else None

    win_payoff_value = None  # To track consistent winner's payoff

    for path in paths_to_check:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            raise ValueError(f"Path {path} does not lead to a terminal node.")
        
        payoffs = terminal_node.payoffs

        if path[0] == path[1]:  # Draw
            if payoffs != [0, 0]:
                raise ValueError(f"Path {path} is a draw but payoff is not [0, 0]: {payoffs}")
        else:
            # 1. Zero-sum
            if sum(payoffs) != 0:
                raise ValueError(f"Path {path} is not zero-sum: sum is {sum(payoffs)}, payoffs={payoffs}")
            
            if path == ['Rock', 'Paper']:
                if payoffs[0] >= payoffs[1]:
                    raise ValueError(f"Path {path} should have loser payoff < winner payoff: {payoffs}")
                winner = payoffs[1]
            elif path == ['Rock', 'Scissors']:
                if payoffs[0] <= payoffs[1]:
                    raise ValueError(f"Path {path} should have winner payoff > loser payoff: {payoffs}")
                winner = payoffs[0]
            elif path == ['Paper', 'Rock']:
                if payoffs[0] <= payoffs[1]:
                    raise ValueError(f"Path {path} should have winner payoff > loser payoff: {payoffs}")
                winner = payoffs[0]
            elif path == ['Paper', 'Scissors']:
                if payoffs[0] >= payoffs[1]:
                    raise ValueError(f"Path {path} should have loser payoff < winner payoff: {payoffs}")
                winner = payoffs[1]
            elif path == ['Scissors', 'Rock']:
                if payoffs[0] >= payoffs[1]:
                    raise ValueError(f"Path {path} should have loser payoff < winner payoff: {payoffs}")
                winner = payoffs[1]
            elif path == ['Scissors', 'Paper']:
                if payoffs[0] <= payoffs[1]:
                    raise ValueError(f"Path {path} should have winner payoff > loser payoff: {payoffs}")
                winner = payoffs[0]

            if win_payoff_value is None:
                win_payoff_value = winner
            elif winner != win_payoff_value:
                raise ValueError(f"Inconsistent winner payoff in {path}. Expected {win_payoff_value}, got {winner}")

    print("All paths satisfy draw, zero-sum, winner-higher, and consistent reward conditions.")
    return True
