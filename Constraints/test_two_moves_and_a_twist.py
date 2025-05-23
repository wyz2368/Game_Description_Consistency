from Tree import NodeType, EFGParser, compare_chance_probs, compare_information_sets

paths_to_check = [
    ['A', 'C'],
    ['B', 'F', 'J'],
    ['B', 'F', 'K']
]

def check_payoffs(game):
    
    def traverse_path(node, path):
        current = node
        for action in path:
            if action not in current.children:
                return None
            current = current.children[action]
        return current if current.node_type == NodeType.TERMINAL else None
    
    D = C = B = A = None
    
    for path in paths_to_check:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            print(f"Path {path} does not lead to a terminal node.")
            return False
        
        outcome = terminal_node.payoffs

        if path[0] == 'A' and path[1] == 'C':
            D = outcome[0]
        
        elif path[0] == 'B' and path[1] == 'F' and path[2] == 'J':
            C = outcome[0]

        elif path[0] == 'B' and path[1] == 'F' and path[2] == 'K':
            B = outcome[0]
            A = outcome[1]

    print(f"Payoffs: D={D}, C={C}, B={B}, A={A}")
    if D>C and B>A:
        print("All path leads to the correct expected payoff logic.")
        return True
    else:
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

ref_game_path = "Dataset_added/Perfect_Information_Games/Two_Moves_and_a_Twist/Reference/ref.efg"
output_game_path = "Results/Output/Perfect_Information_Games/Two_Moves_and_a_Twist/1.efg"
original_game_path = "Dataset_added/Perfect_Information_Games/Two_Moves_and_a_Twist/Correct/1.efg"

test_constraints(ref_game_path, output_game_path, original_game_path)
