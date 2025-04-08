from Tree import NodeType

"""
Firm 1 is a monopolist already established in the market. Firm 2, a potential competitor, can choose to enter the market or stay out (if it stays out, the game ends). If Firm 2 enters, Firm 1 must decide whether to compete aggressively (Fight) or allow some market share to Firm 2 (Accommodate). This game only lasts for one round.
The payoffs are structured as follows:
Firm 1 earns more if Firm 2 decides not to enter.
If Firm 2 enters and Firm 1 accommodates, both firms earn an equal amount.
If Firm 2 enters and Firm 1 fights, Firm 2 earns more than Firm 1.
"""

paths_to_check = [
    ['Enter', 'Fight'],
    ['Enter', 'Accommodate'],
    ['Out']
]

def check_payoffs(game):
    """
    We need to check the payoffs for satisfying the following constraints:
    Firm 1 earns more if Firm 2 decides not to enter.
    If Firm 2 enters and Firm 1 accommodates, both firms earn an equal amount.
    If Firm 2 enters and Firm 1 fights, Firm 2 earns more than Firm 1.
    """
    def traverse_path(node, path):
        current = node
        for action in path:
            if action not in current.children:
                return None
            current = current.children[action]
        return current if current.node_type == NodeType.TERMINAL else None

    fight_payoff = None
    accommodate_payoff = None
    out_payoff = None

    for path in paths_to_check:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            raise ValueError(f"Path {path} does not lead to a terminal node.")

        if path == ['Enter', 'Fight']:
            fight_payoff = terminal_node.payoffs
        elif path == ['Enter', 'Accommodate']:
            accommodate_payoff = terminal_node.payoffs
        elif path == ['Out']:
            out_payoff = terminal_node.payoffs

    # Check constraints
    if out_payoff is None or fight_payoff is None or accommodate_payoff is None:
        raise ValueError("One or more required paths are missing from the game tree.")

    firm1_out, firm2_out = out_payoff
    firm1_accom, firm2_accom = accommodate_payoff
    firm1_fight, firm2_fight = fight_payoff

    # 1. Firm 1 earns more if Firm 2 decides not to enter.
    if firm1_out <= firm2_out:
        raise ValueError(f"Constraint failed: Firm 1 should earn more if Firm 2 stays out (got {firm1_out}) than if it enters and game proceeds to accommodate ({firm1_accom}) or fight ({firm1_fight}).")

    # 2. If Firm 2 enters and Firm 1 accommodates, both firms earn equally.
    if firm1_accom != firm2_accom:
        raise ValueError(f"Constraint failed: Expected equal payoffs on accommodate, got {firm1_accom} and {firm2_accom}.")

    # 3. If Firm 2 enters and Firm 1 fights, Firm 2 earns more than Firm 1.
    if firm2_fight <= firm1_fight:
        raise ValueError(f"Constraint failed: Firm 2 should earn more than Firm 1 when fighting, got {firm1_fight} and {firm2_fight}.")

    print("All payoff constraints are satisfied.")
    return True
