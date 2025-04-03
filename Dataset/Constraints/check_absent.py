def check_exit_game_outcomes(paths_with_outcomes):
    conditions_met = False  # Assume no valid path found yet

    for path, outcome in paths_with_outcomes:
        if path == ['EXIT']:
            if outcome != [0]:
                raise ValueError(f"Condition failed for {path}: Expected [0], but got {outcome}")
            conditions_met = True

        elif path == ['CONTINUE', 'EXIT']:
            if outcome != [4]:
                raise ValueError(f"Condition failed for {path}: Expected [4], but got {outcome}")
            conditions_met = True

        elif path == ['CONTINUE', 'CONTINUE']:
            if outcome != [1]:
                raise ValueError(f"Condition failed for {path}: Expected [1], but got {outcome}")
            conditions_met = True

    return conditions_met
