from Tree import NodeType, EFGParser, compare_information_sets, compare_chance_probs   

paths_to_check = [
    (['a'], [0, 0]),
    (['b', 'B', 'f'], [2, 0]),
    (['b', 'B', 'e', 'O'], [5, -1]),
    (['b', 'B', 'e', 'P'], [-2, 5]),
    (['b', 'C', 'g'], [1, 1]),
    (['b', 'C', 'h', 'W'], [0, 2]),
    (['b', 'C', 'h', 'R'], [-1, 1]),
    (['b', 'C', 'h', 'Y'], [1, 1])
]

def check_payoffs(game):
    """
    This function checks that each specific path in the game tree leads to the expected payoff.
    """
    def traverse_path(node, path):
        current = node
        for action in path:
            if action not in current.children:
                return None
            current = current.children[action]
        return current if current.node_type == NodeType.TERMINAL else None

    all_correct = True

    for path, expected_payoff in paths_to_check:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            print(f"Path {path} does not lead to a terminal node.")
            all_correct = False
        elif terminal_node.payoffs != expected_payoff:
            print(f"Path {path} leads to payoff {terminal_node.payoffs}, expected {expected_payoff}.")
            all_correct = False
        else:
            print(f"Path {path} correctly leads to {expected_payoff}.")

    if all_correct:
        print("All path payoffs are correct.")
    else:
        print("Some path payoffs are incorrect.")
    return all_correct

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