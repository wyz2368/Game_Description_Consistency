import itertools
import numpy as np

def sample_beliefs(payoff_matrix, num_points=10):
    """_summary_

    Args:
        payoff_matrix (_type_): _description_
        num_points (int, optional): _description_. Defaults to 100.

    Returns:
        _type_: _description_
    """

    opponent_shape = payoff_matrix.shape[1:]
    num_opponent_strategies = int(np.prod(opponent_shape))
    
    linspace_values = np.linspace(0, 1, num_points)
    # print(linspace_values)
    partitions = []

    # Generate all possible ways to pick (n-1) breakpoints from linspace
    for dividers in itertools.combinations_with_replacement(linspace_values, num_opponent_strategies - 1):
        scaled_dividers = [0] + list(dividers) + [1]
        partition = np.diff(scaled_dividers)
        partitions.append(partition)

    return np.array(partitions)


def compute_beliefs(payoff_matrix, strategy, available_strategies, belief_array):
    """
    Compute the set of beliefs for a given player, strategy, and available strategies.

    Args:
        payoff_matrix: A numpy array representing the payoff matrix of the player.
        strategy: Index of the player's strategy (int).
        available_strategies: List of strategy indices to consider as alternatives.

    Returns:
        A set of beliefs (probability distributions) where the player weakly prefers the given strategy.
    """

    beliefs = set()

    for belief in belief_array:

        belief = np.array(belief)
        is_best_response = True
        
        for alternative_strategy in available_strategies:
            if alternative_strategy == strategy:
                continue

            payoff_diff = belief @ (payoff_matrix[strategy].flatten() - payoff_matrix[alternative_strategy].flatten())

            if payoff_diff < 0:  # Not weakly preferred
                is_best_response = False
                break

        if is_best_response:
            beliefs.add(tuple(belief))

    return beliefs


def check_best_response_equivalence(payoff_matrix_g, payoff_matrix_g_prime):
    """
    Check whether two games are best-response equivalent.

    Args:
        payoff_matrix_g: A list of numpy arrays representing the payoff matrices for each player in game G.
        payoff_matrix_g_prime: A list of numpy arrays representing the payoff matrices for each player in game G'.

    Returns:
        True if the games are best-response equivalent, False otherwise.
    """

    num_players = len(payoff_matrix_g)

    for player in range(num_players):
        strategies = range(payoff_matrix_g[player].shape[0])
        
        available_strategies = list(strategies)

        for strategy in strategies:

            belief_array = sample_beliefs(payoff_matrix_g[player])
            
            beliefs_g = compute_beliefs(payoff_matrix_g[player], strategy, available_strategies, belief_array)
            beliefs_g_prime = compute_beliefs(payoff_matrix_g_prime[player], strategy, available_strategies, belief_array)

            if beliefs_g != beliefs_g_prime:
                return False  # Found a discrepancy in beliefs

    return True