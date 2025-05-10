from Tree import NodeType, EFGParser, compare_information_sets

paths = [
    ['Remove 1 from heap 1', 'Remove 1 from heap 1', 'Remove 1 from heap 2', 'Remove 1 from heap 2'],
    ['Remove 1 from heap 1', 'Remove 1 from heap 1', 'Remove 2 from heap 2'],
    ['Remove 1 from heap 1', 'Remove 1 from heap 2', 'Remove 1 from heap 1', 'Remove 1 from heap 2'],
    ['Remove 1 from heap 1', 'Remove 1 from heap 2', 'Remove 1 from heap 2', 'Remove 1 from heap 1'],
    ['Remove 1 from heap 1', 'Remove 2 from heap 2', 'Remove 1 from heap 1'],
    ['Remove 2 from heap 1', 'Remove 1 from heap 2', 'Remove 1 from heap 2'],
    ['Remove 2 from heap 1', 'Remove 2 from heap 2'],
    ['Remove 1 from heap 2', 'Remove 1 from heap 1', 'Remove 1 from heap 1', 'Remove 1 from heap 2'],
    ['Remove 1 from heap 2', 'Remove 1 from heap 1', 'Remove 1 from heap 2', 'Remove 1 from heap 1'],
    ['Remove 1 from heap 2', 'Remove 2 from heap 1', 'Remove 1 from heap 2'],
    ['Remove 1 from heap 2', 'Remove 1 from heap 2', 'Remove 1 from heap 1', 'Remove 1 from heap 1'],
    ['Remove 1 from heap 2', 'Remove 1 from heap 2', 'Remove 2 from heap 1'],
    ['Remove 2 from heap 2', 'Remove 1 from heap 1', 'Remove 1 from heap 1'],
    ['Remove 2 from heap 2', 'Remove 2 from heap 1']
]

def check_payoffs(game):
    """
    Check that each given action path leads to a terminal node
    where the payoffs are zero-sum and have equal absolute values.
    """
    def traverse_path(node, path):
        current = node
        for action in path:
            if action not in current.children:
                return None
            current = current.children[action]
        return current if current.node_type == NodeType.TERMINAL else None

    all_valid = True
    for path in paths:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            print(f"Path {path} does not lead to a terminal node.")
            all_valid = False
            continue

        payoffs = terminal_node.payoffs
        if len(payoffs) != 2:
            print(f"Path {path} leads to invalid payoff structure: {payoffs}")
            all_valid = False
            continue

        if payoffs[0] + payoffs[1] != 0 or abs(payoffs[0]) != abs(payoffs[1]):
            print(f"Path {path} leads to non-zero-sum or unequal payoffs: {payoffs}")
            all_valid = False

    if all_valid:
        print("All paths lead to valid zero-sum, equal-absolute-value payoffs.")
    return all_valid


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