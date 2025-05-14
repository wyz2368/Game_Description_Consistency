from Tree import NodeType, EFGParser, compare_information_sets

"""
The game involves a single pile of five stones, with two players, Alice and Bob, taking turns. On each turn, a player can remove either one or two stones (but only one stone if only one remains). The goal is to avoid taking the last stone.
Here's how the moves unfold:
Alice starts and can choose to remove one or two stones.
   If Alice removes one stone, Bob can also remove one or two stones.
      If Bob removes one stone, Alice can again choose to remove one or two stones.
         If Alice removes one stone, Bob has the choice to remove one or two stones.
            If Bob removes one stone, Alice can remove one stone, which would result in Alice losing the game.
            If Bob removes two stones, Bob loses the game.
         If Alice removes two stones, Bob can remove one stone, leading to Bob's loss.
      If Bob removes two stones, Alice can remove one or two stones.
         If Alice removes one stone, Bob can remove one stone, leading to Bob's loss.
         If Alice removes two stones, Alice loses the game.
   If Alice removes two stones, Bob has the option to remove one or two stones.
      If Bob removes one stone, Alice can remove one or two stones.
         If Alice removes one stone, Bob can remove one stone, leading to Bob's loss.
         If Alice removes two stones, Alice loses the game.
      If Bob removes two stones, Alice has only one stone left and loses.

In this game, the winner earns one point, while the loser loses one point.
"""

# Constraints:
# Explicit payoffs are correct

paths_to_check = [
    (['Take 1', 'Take 1', 'Take 1', 'Take 1', 'Take 1'], [-1, 1]),
    (['Take 1', 'Take 1', 'Take 1', 'Take 2'], [1, -1]),
    (['Take 1', 'Take 1', 'Take 2', 'Take 1'], [1, -1]),
    (['Take 1', 'Take 2', 'Take 1', 'Take 1'], [1, -1]),
    (['Take 1', 'Take 2', 'Take 2'], [-1, 1]),
    (['Take 2', 'Take 1', 'Take 1', 'Take 1'], [1, -1]),
    (['Take 2', 'Take 1', 'Take 2'], [-1, 1]),
    (['Take 2', 'Take 2', 'Take 1'], [-1, 1])
]

def check_payoffs(game):
    """
    Check the payoffs: the winner earns one point, while the loser loses one point.
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

    return True