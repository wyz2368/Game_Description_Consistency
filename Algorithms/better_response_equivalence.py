import itertools
import numpy as np

def sample_beliefs(payoff_matrix, num_points=100):
    """_summary_

    Args:
        payoff_matrix (_type_): _description_
        num_points (int, optional): _description_. Defaults to 100.

    Returns:
        _type_: _description_
    """
    opponent_shape = payoff_matrix.shape[1:]
    num_opponent_strategies = np.prod(opponent_shape)
    print(num_opponent_strategies)
    
    linspace_values = np.linspace(0, 1, num_points)
    # print(linspace_values)
    partitions = []

    # Generate all possible ways to pick (n-1) breakpoints from linspace
    for dividers in itertools.combinations_with_replacement(linspace_values, num_opponent_strategies - 1):
        scaled_dividers = [0] + list(dividers) + [1]
        partition = np.diff(scaled_dividers)
        partitions.append(partition)

    return np.array(partitions)

def compute_better_response_beliefs(payoff_matrix, strategy, alternative_strategy, belief_array):
    """
    Compute the set of beliefs for a given player, a strategy, and an alternative strategy.

    Args:
        payoff_matrix: A numpy array representing the payoff matrix of the player.
        strategy: Index of the player's strategy (int).
        alternative_strategy: Index of the alternative strategy (int).

    Returns:
        A set of beliefs (probability distributions) where the player strictly prefers the given strategy over the alternative.
    """


    beliefs = set()
    for belief in belief_array:

        belief = np.array(belief)

        payoff_diff = belief @ (payoff_matrix[strategy].flatten() - payoff_matrix[alternative_strategy].flatten())
        # print(payoff_diff)

        if payoff_diff > 0:  # Strictly prefers strategy to the alternative
            beliefs.add(tuple(belief))
    return beliefs

def check_better_response_equivalence(payoff_matrix_g, payoff_matrix_g_prime):
    """
    Check whether two games are better-response equivalent.

    Args:
        payoff_matrix_g: A list of numpy arrays representing the payoff matrices for each player in game G.
        payoff_matrix_g_prime: A list of numpy arrays representing the payoff matrices for each player in game G'.

    Returns:
        True if the games are better-response equivalent, False otherwise.
    """
    num_players = len(payoff_matrix_g)
    for player in range(num_players):
        num_strategies = payoff_matrix_g[player].shape[0]

        for strategy in range(num_strategies):
            for alternative_strategy in range(strategy + 1, num_strategies):

                belief_array = sample_beliefs(payoff_matrix_g[player])

                beliefs_g = compute_better_response_beliefs(
                    payoff_matrix_g[player], strategy, alternative_strategy, belief_array
                )
                beliefs_g_prime = compute_better_response_beliefs(
                    payoff_matrix_g_prime[player], strategy, alternative_strategy, belief_array
                )

                if beliefs_g != beliefs_g_prime:
                    return False  # Found a discrepancy in beliefs

    return True