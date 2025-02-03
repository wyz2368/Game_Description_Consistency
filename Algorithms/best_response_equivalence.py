import itertools
import numpy as np

def compute_beliefs(payoff_matrix, strategy, available_strategies):
    """
    Compute the set of beliefs for a given player, strategy, and available strategies.

    Args:
        payoff_matrix: A numpy array representing the payoff matrix of the player.
        strategy: Index of the player's strategy (int).
        available_strategies: List of strategy indices to consider as alternatives.

    Returns:
        A set of beliefs (probability distributions) where the player weakly prefers the given strategy.
    """
    num_opponent_strategies = payoff_matrix.shape[1]
    beliefs = []

    for belief in itertools.product(np.linspace(0, 1, 100), repeat=num_opponent_strategies):
        if not np.isclose(sum(belief), 1):
            continue  # Skip invalid probability distributions
        belief = np.array(belief)
        is_best_response = True

        for alternative_strategy in available_strategies:
            if alternative_strategy == strategy:
                continue
            payoff_diff = (
                belief @ (payoff_matrix[strategy, :] - payoff_matrix[alternative_strategy, :])
            )
            if payoff_diff < 0:  # Not weakly preferred
                is_best_response = False
                break

        if is_best_response:
            beliefs.append(tuple(belief))

    return set(beliefs)

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

        for strategy in strategies:
            available_strategies = list(strategies)

            beliefs_g = compute_beliefs(payoff_matrix_g[player], strategy, available_strategies)
            beliefs_g_prime = compute_beliefs(payoff_matrix_g_prime[player], strategy, available_strategies)

            if beliefs_g != beliefs_g_prime:
                return False  # Found a discrepancy in beliefs

    return True

# Example usage
if __name__ == "__main__":
    # Payoff matrices for a 2-player game (row player and column player)
    # Each player has 2 strategies
    payoff_matrix_g = [
        np.array([[3, 0], [5, 1]]),  # Payoffs for player 1
        np.array([[2, 4], [0, 6]])   # Payoffs for player 2
    ]

    payoff_matrix_g_prime = [
        np.array([[3, 0], [5, 1]]),  # Payoffs for player 1 (same as G)
        np.array([[2, 4], [0, 6]])   # Payoffs for player 2 (same as G)
    ]

    print("Are the games best-response equivalent?")
    print(check_best_response_equivalence(payoff_matrix_g, payoff_matrix_g_prime))
