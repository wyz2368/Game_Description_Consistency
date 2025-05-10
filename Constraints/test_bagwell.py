from Tree import NodeType, EFGParser, compare_chance_probs, compare_information_sets

"""
In this game, Player 1, the leader, first selects a strategy: either ``S'' or ``C.'' 
Player 2, the follower, then tries to interpret Player 1's choice, but there is a small probability of misinterpretation (e.g., if Player 1 selects S, there’s a 1\% chance that Player 2 will perceive it as C). 
Based on what Player 2 believes Player 1 chose, Player 2 then picks either ``S'' or ``C.'' 
The resulting payoffs for each player are based on the chosen combination (Player 1's actual selection, not Player 2's interpretation): 
if both choose S, the payoff is (A, B); if Player 1 chooses S and Player 2 chooses C, it is (W, D); 
if Player 1 chooses C and Player 2 chooses S, it is (E, W); and if both choose C, the payoff is (F, F). 
The payoff rankings from highest to lowest are: E (highest), A, F, W, B, and D (lowest). 
Assign values to each of these payoffs and set all the outcomes.
"""

# Constraints:
# payoff values A>F, W>B
# Compare all chance probabilities

paths_to_check = [
    ['S', 'Received S', 'S'],
    ['S', 'Received S', 'C'],
    ['C', 'Received S', 'C']
]

def check_payoffs(game):
    """
    The payoffs are implicitly defined in the game tree by a ranking: E (highest), A, F, W, B, and D (lowest). 
    Here we only check relationshios between A and F
    """
    def traverse_path(node, path):
        current = node
        for action in path:
            if action not in current.children:
                return None
            current = current.children[action]
        return current if current.node_type == NodeType.TERMINAL else None
    
    A = F = W = B = None
    
    for path in paths_to_check:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            print(f"Path {path} does not lead to a terminal node.")
            return False
        
        outcome = terminal_node.payoffs

        if path[0] == 'S' and path[2] == 'S':
            A = outcome[0]
            B = outcome[1]
        
        elif path[0] == 'S' and path[2] == 'C':
            W = outcome[0]

        elif path[0] == 'C' and path[2] == 'C':
            F = outcome[0]


    if A>F and W>B:
        print("All path leads to the correct expected payoff logic.")
        return True
    else:
        print(f"Condition failed: Expected A > F, but got A={A}, F={F}")
        return False


#========Test Functions Below===================================================================================

# ref_game_path = "Dataset/Imperfect_Information_Games/Bagwell/Reference/ref.efg"
# after_switch_game_path = "Output/Imperfect_Information_Games/Bagwell/5.efg"

# # parser_ref = EFGParser()
# parser_gen = EFGParser()

# # ref_game = parser_ref.parse_file(ref_game_path)
# gen_game = parser_gen.parse_file(after_switch_game_path)

# def test_payoffs():
#     print("Checking payoffs...")
#     check_payoffs(gen_game)
#     assert check_payoffs(gen_game) == True
    
# def test_chance():
#     print("Checking chance probabilities...")
#     assert compare_chance_probs(ref_game, gen_game) == True

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

    

