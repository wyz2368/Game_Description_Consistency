from Tree import NodeType, compare_chance_probs, compare_information_sets, EFGParser

"""
This is a game with three players.
In the first stage, a chance event determines either "A" or "B" with equal probability (1/2 for each). 
In the second stage, player 1 chooses between "L" and "R" without knowing the outcome of the chance event. If player 1 selects "R," the game ends with a payoff of (1, 1, 1) to all players. 
In the third stage, if player 1 chooses "L", then player 2 can select either "l" or "r." Player 2 does not see player 1's choice from the previous stage. If player 2 chooses "r," the game ends with a payoff of (2, 2, 2) to all players.
In the fourth stage, if player 2 selects "l," then player 3 can choose between "a" and "b." Player 3 does not know player 2's prior choice. The game concludes with a payoff of (3, 3, 3) once player 3 makes a decision.
Throughout the game, none of the players have knowledge of the previous moves of other players or the chance event.
"""

# Constraints:
# Explicit payoffs are correct
# Cance probabilities are correct

paths_to_check = [
    (['A', 'L', 'l', 'a'], [3, 3, 3]),
    (['A', 'L', 'l', 'b'], [3, 3, 3]),
    (['A', 'L', 'r'], [2, 2, 2]),
    (['A', 'R'], [1, 1, 1]),
    (['B', 'L', 'l', 'a'], [3, 3, 3]),
    (['B', 'L', 'l', 'b'], [3, 3, 3]),
    (['B', 'L', 'r'], [2, 2, 2]),
    (['B', 'R'], [1, 1, 1])
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