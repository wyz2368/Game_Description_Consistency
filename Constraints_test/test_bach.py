from Tree import NodeType, EFGParser

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

after_switch_game_path ="Output/Imperfect_Information_Games/Bach_or_Stravinsky/5.efg"

parser_gen = EFGParser()

gen_game = parser_gen.parse_file(after_switch_game_path)

def test_payoffs():
    print("Checking payoffs...")
    check_payoffs(gen_game)
    assert check_payoffs(gen_game) == True
    