def check_bach_game_outcomes(paths_with_outcomes):
    
    conditions_met = True

    for path, outcome in paths_with_outcomes:
        if path == ['Stravinsky', 'Bach'] or path == ['Bach', 'Stravinsky']:
            if outcome != [0, 0]:
                raise ValueError(f"Condition failed for {path}: Expected [0, 0], but got {outcome}")

        elif path == ['Bach', 'Bach']:
            if outcome[0] <= outcome[1]:  # Player 1 should get more than Player 2
                raise ValueError(f"Condition failed for {path}: Expected Player 1 > Player 2, but got {outcome}")

        elif path == ['Stravinsky', 'Stravinsky']:
            if outcome[1] <= outcome[0]:  # Player 2 should get more than Player 1
                raise ValueError(f"Condition failed for {path}: Expected Player 2 > Player 1, but got {outcome}")

    return conditions_met
