import numpy as np
from itertools import product
from multiprocessing import Pool, cpu_count, Manager


def get_relationship(x, y):
    if x > y:
        return ">"
    elif x < y:
        return "<"
    else:
        return "="


def compare_strategy_pair(args):
    player, s_i, s_i_prime, payoff_matrix_g, payoff_matrix_g_prime = args
    num_opponents = len(payoff_matrix_g) - 1
    num_opponent_strategies = [payoff_matrix_g[player].shape[i + 1] for i in range(num_opponents)]
    opponent_strategy_profiles = product(*(range(n) for n in num_opponent_strategies))

    for s_minus_i in opponent_strategy_profiles:
        u_g = payoff_matrix_g[player][(s_i,) + s_minus_i]
        u_g_prime = payoff_matrix_g[player][(s_i_prime,) + s_minus_i]
        u_g_dash = payoff_matrix_g_prime[player][(s_i,) + s_minus_i]
        u_g_prime_dash = payoff_matrix_g_prime[player][(s_i_prime,) + s_minus_i]

        if get_relationship(u_g, u_g_prime) != get_relationship(u_g_dash, u_g_prime_dash):
            return False
    return True


def check_order_preserving_equivalence_multiprocessing(payoff_matrix_g, payoff_matrix_g_prime):
    num_players = len(payoff_matrix_g)
    args_list = []

    for player in range(num_players):
        num_strategies = payoff_matrix_g[player].shape[0]
        for s_i in range(num_strategies):
            for s_i_prime in range(s_i + 1, num_strategies):
                args_list.append((player, s_i, s_i_prime, payoff_matrix_g, payoff_matrix_g_prime))

    with Pool(processes=cpu_count()) as pool:
        for result in pool.imap_unordered(compare_strategy_pair, args_list, chunksize=1):
            if not result:
                pool.terminate()
                return False

    return True
