def check_bagwell_outcomes(paths_with_outcomes):
    condition_met = False  
    E, A, F, W, B, D = None, None, None, None, None, None  # Initialize variables

    store_outcomes = {"(S, S)": None, "(S, C)": None, "(C, S)": None, "(C, C)": None}

    for path, outcome in paths_with_outcomes:
        if path[0] == 'S' and path[2] == 'S':
            A = outcome[0]
            B = outcome[1]
            if store_outcomes["(S, S)"] is None:
                store_outcomes["(S, S)"] = outcome
            else:
                if outcome != store_outcomes["(S, S)"]:
                    raise ValueError(f"Condition failed for {path}: Expected {store_outcomes['(S, S)']}, but got {outcome}")
        if path[0] == 'S' and path[2] == 'C':
            W = outcome[0]
            D = outcome[1]
            if store_outcomes["(S, C)"] is None:
                store_outcomes["(S, C)"] = outcome
            else:
                if outcome != store_outcomes["(S, C)"]:
                    raise ValueError(f"Condition failed for {path}: Expected {store_outcomes['(S, C)']}, but got {outcome}")
        if path[0] == 'C' and path[2] == 'S':
            E = outcome[0]
            W = outcome[1]
            if store_outcomes["(C, S)"] is None:
                store_outcomes["(C, S)"] = outcome
            else:
                if outcome != store_outcomes["(C, S)"]:
                    raise ValueError(f"Condition failed for {path}: Expected {store_outcomes['(C, S)']}, but got {outcome}")
        if path[0] == 'C' and path[2] == 'C':
            F = outcome[0]
            F = outcome[1]
            if store_outcomes["(C, C)"] is None:
                store_outcomes["(C, C)"] = outcome
            else:
                if outcome != store_outcomes["(C, C)"]:
                    raise ValueError(f"Condition failed for {path}: Expected {store_outcomes['(C, C)']}, but got {outcome}")
    
    # Check the conditions
    print(f"Outcomes: E={E}, A={A}, F={F}, W={W}, B={B}, D={D}")
    if E>A>F>W>B>D:
        condition_met = True
    else:
        raise ValueError(f"Condition failed for {path}: Expected E>A>F>W>B>D, but got {outcome}")
    
    return condition_met