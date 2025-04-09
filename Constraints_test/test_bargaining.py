from Tree import NodeType, EFGParser

"""
A and B are negotiating how to split 10,000 pounds in cash, following these rules: 
First, A proposes a plan where A receives 5,500 pounds, and B receives 4,500 pounds. 
If B accepts, the negotiation concludes, with A getting 5,500 pounds and B getting 4,500 pounds. 
If B rejects, B then proposes an equal split of 5,000 pounds each. If A accepts B’s offer, both players finalize the negotiation with each receiving 4,750 pounds. 
If A rejects B’s offer, A proposes a new split where A receives 5,200 pounds, and B receives 4,800 pounds. 
Here, B has no choice but to accept, resulting in A receiving 4,693 pounds and B receiving 4,332 pounds.
The final amount each player receives is their payoff in the negotiation.
"""

# Constraints:
# Explicit payoffs are correct

paths_to_check = [
    (['Propose 5500-4500', 'Accept'], [5500, 4500]),
    (['Propose 5500-4500', 'Reject', 'Propose 5000-5000', 'Accept'], [4750, 4750]),
    (['Propose 5500-4500', 'Reject', 'Propose 5000-5000', 'Reject', 'Propose 5200-4800'], [4693, 4332])
]

def check_payoffs(game):
    """
    We need to check the following explicit payoffs specified in the game description as shown in the paths_to_check list.
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