import numpy as np
from itertools import product

def get_relationship(x, y):
    """
    Determine the relationship R(x, y).

    Args:
        x: First value.
        y: Second value.

    Returns:
        A string representing the relationship: ">", "<", or "=".
    """
    if x > y:
        return ">"
    elif x < y:
        return "<"
    else:
        return "="


def check_order_preserving_equivalence(payoff_matrix_g, payoff_matrix_g_prime):
    """
    Check whether two games are order-preserving equivalent.

    Args:
        payoff_matrix_g: A list of numpy arrays representing the payoff matrices for each player in game G.
        payoff_matrix_g_prime: A list of numpy arrays representing the payoff matrices for each player in game G'.

    Returns:
        True if the games are order-preserving equivalent, False otherwise.
    """
    num_players = len(payoff_matrix_g)
    num_opponents = num_players - 1

    for player in range(num_players):
        # print("Player:", player)

        num_strategies = payoff_matrix_g[player].shape[0]
        # print("Number of strategies:", num_strategies)
        
        num_opponent_strategies = [payoff_matrix_g[player].shape[i+1] for i in range(num_opponents)]
        opponent_strategy_profiles = product(*(range(n) for n in num_opponent_strategies))
        # print("Number of opponents:", num_opponents)
        # print("Opponent strategy sizes:", num_opponent_strategies)

        for s_i in range(num_strategies):
            for s_i_prime in range(s_i + 1, num_strategies):

                # print("Strategy pair:", s_i, s_i_prime)

                for s_minus_i in opponent_strategy_profiles:
                    # Payoffs in game G
                    u_g = payoff_matrix_g[player][(s_i,) + s_minus_i]
                    # print("Payoffs in game G:", u_g)
                    u_g_prime = payoff_matrix_g[player][(s_i_prime,) + s_minus_i]
                    # print("Payoffs in game G:", u_g_prime)

                    # Payoffs in game G'
                    u_g_dash = payoff_matrix_g_prime[player][(s_i,) + s_minus_i]
                    # print("Payoffs in game G':", u_g_dash)
                    u_g_prime_dash = payoff_matrix_g_prime[player][(s_i_prime,) + s_minus_i]
                    # print("Payoffs in game G':", u_g_prime_dash)

                    # Compare relationships
                    relation_g = get_relationship(u_g, u_g_prime)
                    relation_g_prime = get_relationship(u_g_dash, u_g_prime_dash)

                    if relation_g != relation_g_prime:
                        return False  # Relation mismatch found

    return True