def check_all_zero_outcomes(paths_with_outcomes):
    conditions_met = False  # Assume no valid path found yet

    for path, outcome in paths_with_outcomes:
        if outcome != [0]:
            raise ValueError(f"Condition failed for {path}: Expected [0], but got {outcome}")
        conditions_met = True

    return conditions_met
