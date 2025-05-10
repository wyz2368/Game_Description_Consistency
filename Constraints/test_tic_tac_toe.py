from Tree import NodeType, EFGParser, compare_information_sets

"""
You’re playing a two-player paper-and-pencil game, where players take turns marking a three-by-three grid with either an "x" or an "o." The objective is to get three of your marks in a row, column, or diagonal to win.
The winner gains 1 point, while the loser loses 1 point.
Assuming "e" represents empty, the current board state is: 
e | o | e
e | x | o
x | x | o
The next move is "x" 

The game tree could be generated as follows:
"x" can place the mark on (0,0), (0,2) and (1,0).
If "x" places the mark on (0,0), 
   "o" can then place the mark on (0,2) and (1,0).
   If "o" places the mark on (0,2), "o" wins.
   If "o" places the mark on (1,0), 
      "x" can then place the mark on (0,2), 
      If "x" places the mark on (0,2), "x" wins.
If "x" places the mark on (0,2), "x" wins.
If "x" places the mark on (1,0), 
   "o" can then place the mark on (0,0) and (0,2).
   If "o" places the mark on (0,0), 
      "x" can then place the mark on (0,2), 
      If "x" places the mark on (0,2), "x" wins.
   If "o" places the mark on (0,2), "o" wins.
"""

# Constraints:
# Explicit payoffs are correct

paths_to_check = [
    (['(0,0)', '(0,2)'], [-1, 1]),
    (['(0,0)', '(1,0)', '(0,2)'], [1, -1]),
    (['(0,2)'], [1, -1]),
    (['(1,0)', '(0,0)', '(0,2)'], [1, -1]),
    (['(1,0)', '(0,2)'], [-1, 1])
]

def check_payoffs(game):
    """
    Each path in the game tree is checked against the expected payoffs in the game description.
    Payoff: The winner gains 1 point, while the loser loses 1 point.
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

# after_switch_game_path = "Output/Perfect_Information_Games/Tic_Tac_Toe/3.efg"

# parser_gen = EFGParser()

# gen_game = parser_gen.parse_file(after_switch_game_path)

# def test_payoffs():
#     print("Checking payoffs...")
#     check_payoffs(gen_game)
#     assert check_payoffs(gen_game) == True

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