from Tree import NodeType, EFGParser, compare_chance_probs, compare_information_sets

"""
There are two players in this scenario: Country A and Country B. 
The status quo is that Country A receives revenue from Country B. 
Initially, Country B has the choice to either ``Accept'' this arrangement or ``Rebel.''
If Country B accepts the status quo, Country A then decides whether to ``Tax'' or ``Drop Taxes.'' 
If Country A continues to tax, it gains 6, while Country B loses 2. 
If Country A drops the taxes, Country A earns 4, and Country B breaks even with 0. 
However, if Country B decides to rebel, Country A faces a choice to either ``Grant Independence'' to Country B or attempt to ``Suppress'' the rebellion. 
Granting independence results in Country A earning 0, while Country B gains 3. Attempting to suppress the rebellion leads to war, with the outcome determined by chance. 
In the event of war, Country B has a 0.3 probability of winning. 
If Country B wins the war, it loses 3, while Country A loses 1. If Country B loses the war, it loses 5, and Country A still loses 1.
"""

# Constraints:
# Explicit payoffs are correct
# Cance probabilities are correct

paths_to_check = [
    (['Accept', 'Tax'], [6, -2]),
    (['Accept', 'Drop Taxes'], [4, 0]),
    (['Rebel', 'Grant Independence'], [0, 3]),
    (['Rebel', 'Suppress', 'B Wins'], [-1, -3]),
    (['Rebel', 'Suppress', 'B Loses'], [-1, -5])
]

def check_payoffs(game):
    """
    We need to check the explicit payoffs specified in the game description as shown in the paths_to_check list.
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

def test_constraints(ref_game_path, output_game_path, original_game_path):

    parser_ref = EFGParser()
    parser_gen = EFGParser()
    parser_orig = EFGParser()

    ref_game = parser_ref.parse_file(ref_game_path)
    gen_game = parser_gen.parse_file(output_game_path)
    orig_game = parser_orig.parse_file(original_game_path)


    if not compare_information_sets(ref_game, gen_game):
        print("Information sets do not match between reference and generated game.")
        return False

    if not check_payoffs(gen_game):
        return False

    if not compare_chance_probs(ref_game, gen_game):
        return False

    return True