from Tree import NodeType, EFGParser, compare_information_sets

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

# Constraints:
# Check zero-sum and intro payoffs between players

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

    for path in paths_to_check:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            print(f"Path {path} does not lead to a terminal node.")
            return False
        
        payoffs = terminal_node.payoffs

        if path[0] == path[1]:  # Draw
            if payoffs != [0, 0]:
                print(f"Path {path} is a draw but payoff is not [0, 0]: {payoffs}")
                return False
        else:
            # 1. Zero-sum
            if sum(payoffs) != 0:
                print(f"Path {path} is not zero-sum: sum is {sum(payoffs)}, payoffs={payoffs}")
                return False
            
            if path == ['Rock', 'Paper']:
                if payoffs[0] >= payoffs[1]:
                    print(f"Path {path} should have loser payoff < winner payoff: {payoffs}")
                    return False

            elif path == ['Rock', 'Scissors']:
                if payoffs[0] <= payoffs[1]:
                    print(f"Path {path} should have winner payoff > loser payoff: {payoffs}")
                    return False

            elif path == ['Paper', 'Rock']:
                if payoffs[0] <= payoffs[1]:
                    print(f"Path {path} should have winner payoff > loser payoff: {payoffs}")
                    return False

            elif path == ['Paper', 'Scissors']:
                if payoffs[0] >= payoffs[1]:
                    print(f"Path {path} should have loser payoff < winner payoff: {payoffs}")
                    return False

            elif path == ['Scissors', 'Rock']:
                if payoffs[0] >= payoffs[1]:
                    print(f"Path {path} should have loser payoff < winner payoff: {payoffs}")
                    return False

            elif path == ['Scissors', 'Paper']:
                if payoffs[0] <= payoffs[1]:
                    print(f"Path {path} should have winner payoff > loser payoff: {payoffs}")
                    return False


    print("All paths satisfy draw, zero-sum, winner-higher, and consistent reward conditions.")
    return True


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