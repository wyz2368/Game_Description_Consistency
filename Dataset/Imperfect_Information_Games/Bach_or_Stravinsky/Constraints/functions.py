from Tree import NodeType

paths_to_check = [
    ['Stravinsky', 'Bach'],
    ['Bach', 'Stravinsky'],
    ['Bach', 'Bach'],
    ['Stravinsky', 'Stravinsky']
]

def check_payoff(game):
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
            raise ValueError(f"Path {path} does not lead to a terminal node.")
        
        outcome = terminal_node.payoffs

        if path in [['Stravinsky', 'Bach'], ['Bach', 'Stravinsky']]:
            if outcome != [0, 0]:
                raise ValueError(f"Path {path} should have payoff [0, 0], got {outcome}.")
        
        elif path == ['Bach', 'Bach']:
            if outcome[0] <= outcome[1]:
                raise ValueError(f"Path {path} should satisfy payoff[0] > payoff[1], got {outcome}.")
            
        elif path == ['Stravinsky', 'Stravinsky']:
            if outcome[1] <= outcome[0]:
                raise ValueError(f"Path {path} should satisfy payoff[1] < payoff[0], got {outcome}.")
        
        any_correct = True
    
    if any_correct:
        print("All paths lead to the correct expected payoff.")
        return True
    else:
        raise ValueError("No path matched the expected payoffs.")
