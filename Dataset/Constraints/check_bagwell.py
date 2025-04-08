from Tree import NodeType

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

paths_to_check = [
    ['S', 'Interpreted as S', 'S'],
    ['S', 'Interpreted as S', 'C'],
    ['S', 'Misinterpreted as C', 'S'],
    ['S', 'Misinterpreted as C', 'C'],
    ['C', 'Interpreted as C', 'S'],
    ['C', 'Interpreted as C', 'C'],
    ['C', 'Misinterpreted as S', 'S'],
    ['C', 'Misinterpreted as S', 'C']
]

def check_payoffs(game):
    """
    The payoffs are implicitly defined in the game tree by a ranking: E (highest), A, F, W, B, and D (lowest). 
    Then we need to get the these values from the payoffs and compare them.
    """
    def traverse_path(node, path):
        current = node
        for action in path:
            if action not in current.children:
                return None
            current = current.children[action]
        return current if current.node_type == NodeType.TERMINAL else None

    E = A = F = W = B = D = None
    store_outcomes = {"(S, S)": None, "(S, C)": None, "(C, S)": None, "(C, C)": None}

    for path in paths_to_check:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            raise ValueError(f"Path {path} does not lead to a terminal node.")
        
        outcome = terminal_node.payoffs

        if path[0] == 'S' and path[2] == 'S':
            if A is None:
                A = outcome[0]
            else:
                if outcome[0] != A:
                    raise ValueError(f"Condition failed for {path}: Expected {A}, but got {outcome[0]}")
            
            if B is None:
                B = outcome[1]
            else:
                if outcome[1] != B:
                    raise ValueError(f"Condition failed for {path}: Expected {B}, but got {outcome[1]}")
            
            if store_outcomes["(S, S)"] is None:
                store_outcomes["(S, S)"] = outcome
            elif outcome != store_outcomes["(S, S)"]:
                raise ValueError(f"Condition failed for {path}: Expected {store_outcomes['(S, S)']}, but got {outcome}")

        elif path[0] == 'S' and path[2] == 'C':
            if W is None:
                W = outcome[0]
            else:
                if outcome[0] != W:
                    raise ValueError(f"Condition failed for {path}: Expected {W}, but got {outcome[0]}")
            
            if D is None:
                D = outcome[1]
            else:
                if outcome[1] != D:
                    raise ValueError(f"Condition failed for {path}: Expected {D}, but got {outcome[1]}")

            if store_outcomes["(S, C)"] is None:
                store_outcomes["(S, C)"] = outcome
            elif outcome != store_outcomes["(S, C)"]:
                raise ValueError(f"Condition failed for {path}: Expected {store_outcomes['(S, C)']}, but got {outcome}")

        elif path[0] == 'C' and path[2] == 'S':
            if E is None:
                E = outcome[0]
            else:
                if outcome[0] != E:
                    raise ValueError(f"Condition failed for {path}: Expected {E}, but got {outcome[0]}")
            if W is None:
                W = outcome[1]
            else:
                if outcome[1] != W:
                    raise ValueError(f"Condition failed for {path}: Expected {W}, but got {outcome[1]}")
            
            if store_outcomes["(C, S)"] is None:
                store_outcomes["(C, S)"] = outcome
            elif outcome != store_outcomes["(C, S)"]:
                raise ValueError(f"Condition failed for {path}: Expected {store_outcomes['(C, S)']}, but got {outcome}")

        elif path[0] == 'C' and path[2] == 'C':
            if F is None:
                F = outcome[0]
            else:
                if outcome[0] != F:
                    raise ValueError(f"Condition failed for {path}: Expected {F}, but got {outcome[0]}")
            
            if outcome[0] != outcome[1]:   
                raise ValueError(f"Condition failed for {path}: Expected equal payoffs, but got {outcome[0]} and {outcome[1]}")
            
            if store_outcomes["(C, C)"] is None:
                store_outcomes["(C, C)"] = outcome
            elif outcome != store_outcomes["(C, C)"]:
                raise ValueError(f"Condition failed for {path}: Expected {store_outcomes['(C, C)']}, but got {outcome}")

    print(f"Outcomes: E={E}, A={A}, F={F}, W={W}, B={B}, D={D}")

    if E > A > F > W > B > D:
        print("All path leads to the correct expected payoff logic.")
        return True
    else:
        raise ValueError(f"Condition failed: Expected E > A > F > W > B > D, but got E={E}, A={A}, F={F}, W={W}, B={B}, D={D}")

