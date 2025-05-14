from Tree import NodeType, EFGParser, compare_information_sets

"""
The ``Bach or Stravinsky?'' game involves two players, Alexis and Beverley, who want to attend a concert together. 
Alexis prefers Bach, while Beverley prefers Stravinsky. 
Both players make their choice between Bach and Stravinsky simultaneously and independently. 
If they both choose Bach, Alexis, the Bach enthusiast, receives a higher payoff, while Beverley receives a lower payoff. 
Conversely, if they both choose Stravinsky, Beverley, who favors Stravinsky, receives a higher payoff, and Alexis receives a lower payoff. 
If they choose different concerts, neither player receives any payoff.
"""

# Constraints:
# Explicit payoffs are correct

paths_to_check = [
    ['Stravinsky', 'Bach'],
    ['Bach', 'Stravinsky'],
    ['Bach', 'Bach'],
    ['Stravinsky', 'Stravinsky']
]



def check_payoffs(game):
    """
    The constraints needed to check are:
    If they both choose Bach, Alexis, the Bach enthusiast, receives a higher payoff, while Beverley receives a lower payoff. 
    Conversely, if they both choose Stravinsky, Beverley, who favors Stravinsky, receives a higher payoff, and Alexis receives a lower payoff. 
    If they choose different concerts, neither player receives any payoff.
    """
    def traverse_path(node, path):
        current = node
        for action in path:
            if action not in current.children:
                return None
            current = current.children[action]
        return current if current.node_type == NodeType.TERMINAL else None

    any_correct = False  # Start assuming none are correct

    for path in paths_to_check:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            print(f"Path {path} does not lead to a terminal node.")
            return False
        
        outcome = terminal_node.payoffs

        if path in [['Stravinsky', 'Bach'], ['Bach', 'Stravinsky']]:
            if outcome != [0, 0]:
                print(f"Path {path} should have payoff [0, 0], got {outcome}.")
                return False
        
        elif path == ['Bach', 'Bach']:
            if outcome[0] <= outcome[1]:
                print(f"Path {path} should satisfy payoff[0] > payoff[1], got {outcome}.")
                return False
            
        elif path == ['Stravinsky', 'Stravinsky']:
            if outcome[1] <= outcome[0]:
                print(f"Path {path} should satisfy payoff[1] < payoff[0], got {outcome}.")
                return False
        
        any_correct = True
    
    if any_correct:
        print("All paths lead to the correct expected payoff.")
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
    