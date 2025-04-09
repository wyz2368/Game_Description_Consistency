from Tree import NodeType, EFGParser

"""
Firm 1 is a monopolist already established in the market. Firm 2, a potential competitor, can choose to enter the market or stay out (if it stays out, the game ends). If Firm 2 enters, Firm 1 must decide whether to compete aggressively (Fight) or allow some market share to Firm 2 (Accommodate). This game only lasts for one round.
The payoffs are structured as follows:
Firm 1 earns more if Firm 2 decides not to enter.
If Firm 2 enters and Firm 1 accommodates, both firms earn an equal amount.
If Firm 2 enters and Firm 1 fights, Firm 2 earns more than Firm 1.
"""

# Constraints:
# 1. Check Firm 1 earns more than Firm 2 enters and Firm 1 accommodates, which is not checked by order_preserving.
# 2. If Firm 2 enters and Firm 1 accommodates, both firms earn an equal amount.
# 3. If Firm 2 enters and Firm 1 fights, Firm 2 earns more than Firm 1.

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
            print(f"Path {path} does not lead to a terminal node.")
            return False

        if path == ['Enter', 'Fight']:
            fight_payoff = terminal_node.payoffs
        elif path == ['Enter', 'Accommodate']:
            accommodate_payoff = terminal_node.payoffs
        elif path == ['Out']:
            out_payoff = terminal_node.payoffs

    # Check constraints
    if out_payoff is None or fight_payoff is None or accommodate_payoff is None:
        print("One or more required paths are missing from the game tree.")
        return False

    firm1_out, firm2_out = out_payoff
    firm1_accom, firm2_accom = accommodate_payoff
    firm1_fight, firm2_fight = fight_payoff

    # 1. Check Firm 1 earns more than Firm 2 enters and Firm 1 accommodates, which is not checked by order_preserving.
    if firm1_out <= firm1_accom:
        print(f"Constraint failed: Firm 1 should earn more when Firm 2 is out, got {firm1_out} and {firm1_accom}.")
        return False
    
    # 2. If Firm 2 enters and Firm 1 accommodates, both firms earn equally.
    if firm1_accom != firm2_accom:
        print(f"Constraint failed: Expected equal payoffs on accommodate, got {firm1_accom} and {firm2_accom}.")
        return False

    # 3. If Firm 2 enters and Firm 1 fights, Firm 2 earns more than Firm 1.
    if firm2_fight <= firm1_fight:
        print(f"Constraint failed: Firm 2 should earn more than Firm 1 when fighting, got {firm1_fight} and {firm2_fight}.")
        return False

    print("All payoff constraints are satisfied.")
    return True

#========Test Functions Below===================================================================================

after_switch_game_path ="Dataset/Reference/market_entry.efg"

parser_gen = EFGParser()

gen_game = parser_gen.parse_file(after_switch_game_path)

def test_payoffs():
    print("Checking payoffs...")
    check_payoffs(gen_game)
    assert check_payoffs(gen_game) == True
