import itertools
import numpy as np
from multiprocessing import Pool, cpu_count


def sample_beliefs(payoff_matrix, num_points=10):
    opponent_shape = payoff_matrix.shape[1:]
    num_opponent_strategies = int(np.prod(opponent_shape))

    linspace_values = np.linspace(0, 1, num_points)
    partitions = []

    for dividers in itertools.combinations_with_replacement(linspace_values, num_opponent_strategies - 1):
        scaled_dividers = [0] + list(dividers) + [1]
        partition = np.diff(scaled_dividers)
        partitions.append(partition)

    return np.array(partitions)


def compute_beliefs(payoff_matrix, strategy, available_strategies, belief_array):
    beliefs = set()

    for belief in belief_array:
        belief = np.array(belief)
        is_best_response = True

        for alternative_strategy in available_strategies:
            if alternative_strategy == strategy:
                continue

            payoff_diff = belief @ (
                payoff_matrix[strategy].flatten() - payoff_matrix[alternative_strategy].flatten()
            )

            if payoff_diff < 0:
                is_best_response = False
                break

        if is_best_response:
            beliefs.add(tuple(belief))

    return beliefs


def compare_strategy_beliefs(args):
    player, strategy, payoff_g, payoff_g_prime, belief_array = args
    strategies = range(payoff_g.shape[0])
    available_strategies = list(strategies)

    beliefs_g = compute_beliefs(payoff_g, strategy, available_strategies, belief_array)
    beliefs_g_prime = compute_beliefs(payoff_g_prime, strategy, available_strategies, belief_array)

    return beliefs_g == beliefs_g_prime


def check_best_response_equivalence_multiprocessing(payoff_matrix_g, payoff_matrix_g_prime, num_points=10):
    num_players = len(payoff_matrix_g)
    tasks = []

    for player in range(num_players):
        payoff_g = payoff_matrix_g[player]
        payoff_g_prime = payoff_matrix_g_prime[player]
        belief_array = sample_beliefs(payoff_g, num_points)

        for strategy in range(payoff_g.shape[0]):
            tasks.append((player, strategy, payoff_g, payoff_g_prime, belief_array))

    with Pool(processes=cpu_count()) as pool:
        for result in pool.imap_unordered(compare_strategy_beliefs, tasks, chunksize=1):
            if not result:
                pool.terminate()
                return False

    return True
