import itertools
import numpy as np
from multiprocessing import Pool, cpu_count

def generate_partition(dividers, num_opponent_strategies):
    scaled_dividers = [0] + list(dividers) + [1]
    return np.diff(scaled_dividers)

def sample_beliefs_parallel(payoff_matrix, num_points=5):
    opponent_shape = payoff_matrix.shape[1:]
    num_opponent_strategies = int(np.prod(opponent_shape))

    linspace_values = np.linspace(0, 1, num_points)
    divider_combinations = list(
        itertools.combinations_with_replacement(linspace_values, num_opponent_strategies - 1)
    )
    print(cpu_count())
    with Pool(processes=cpu_count()) as pool:
        partitions = pool.starmap(
            generate_partition,
            [(dividers, num_opponent_strategies) for dividers in divider_combinations],
        )

    return np.array(partitions)


def compute_better_response_beliefs(payoff_matrix, strategy, alternative_strategy, belief_array):
    beliefs = set()
    for belief in belief_array:
        belief = np.array(belief)
        payoff_diff = belief @ (payoff_matrix[strategy].flatten() - payoff_matrix[alternative_strategy].flatten())
        if payoff_diff > 0:
            beliefs.add(tuple(belief))
    return beliefs


def compare_better_response_beliefs(args):
    player, strategy, alt_strategy, payoff_g, payoff_g_prime, belief_array = args

    beliefs_g = compute_better_response_beliefs(payoff_g, strategy, alt_strategy, belief_array)
    beliefs_g_prime = compute_better_response_beliefs(payoff_g_prime, strategy, alt_strategy, belief_array)

    return beliefs_g == beliefs_g_prime


def check_better_response_equivalence_multiprocessing(payoff_matrix_g, payoff_matrix_g_prime, num_points=10):
    num_players = len(payoff_matrix_g)
    tasks = []

    for player in range(num_players):
        num_strategies = payoff_matrix_g[player].shape[0]
        belief_array = sample_beliefs_parallel(payoff_matrix_g[player], num_points)

        for strategy in range(num_strategies):
            for alt_strategy in range(strategy + 1, num_strategies):
                tasks.append((
                    player,
                    strategy,
                    alt_strategy,
                    payoff_matrix_g[player],
                    payoff_matrix_g_prime[player],
                    belief_array
                ))
    print(cpu_count())
    with Pool(processes=cpu_count()) as pool:
        for result in pool.imap_unordered(compare_better_response_beliefs, tasks, chunksize=1):
            if not result:
                pool.terminate()
                return False

    return True
