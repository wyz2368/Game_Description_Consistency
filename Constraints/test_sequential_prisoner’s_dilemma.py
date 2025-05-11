from Tree import NodeType, EFGParser, compare_information_sets

def check_payoffs(game):
    """
    Checks that each specific path in the Prisoner's Dilemma leads to the correct payoffs.
    """
    expected_paths = [
        (['Cooperate', 'Cooperate'], [3, 3]),
        (['Cooperate', 'Defect'], [0, 5]),
        (['Defect', 'Cooperate'], [5, 0]),
        (['Defect', 'Defect'], [1, 1])
    ]

    def traverse_path(node, path):
        current = node
        for action in path:
            if action not in current.children:
                return None
            current = current.children[action]
        return current if current.node_type == NodeType.TERMINAL else None

    all_correct = True
    for path, expected_payoff in expected_paths:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            print(f"Path {path} does not lead to a terminal node.")
            all_correct = False
            continue
        if terminal_node.payoffs != expected_payoff:
            print(f"Path {path} has incorrect payoff {terminal_node.payoffs}, expected {expected_payoff}.")
            all_correct = False
        else:
            print(f"Path {path} correctly leads to payoff {terminal_node.payoffs}.")

    if all_correct:
        print("All Prisoner's Dilemma payoffs are correct.")
    return all_correct

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