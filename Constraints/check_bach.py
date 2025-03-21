def check_bach_game_outcomes(paths_with_outcomes):
    """
    Checks the following conditions:
    1. The outcomes for paths ['Stravinsky', 'Bach'] and ['Bach', 'Stravinsky'] should be [0, 0].
    2. The outcome for ['Bach', 'Bach'] should have player 1 receive more than player 2.
    3. The outcome for ['Stravinsky', 'Stravinsky'] should have player 2 receive more than player 1.

    Args:
        paths_with_outcomes (list): A list of tuples where each tuple contains:
                                    - A path (list of actions)
                                    - A corresponding outcome (list of payoffs for two players)
    
    Returns:
        bool: True if all conditions are met, False otherwise.
    """
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
