from utils import get_payoff_matrix
import cdd
import numpy as np

def ext_points_worker(args):
    A, b, lin_set = args
    A = np.array(A, dtype='float')
    b = np.array(b, dtype='float').reshape(-1, 1)
    M = np.hstack((b, A))

    mat = cdd.matrix_from_array(M, rep_type=cdd.RepType.INEQUALITY, lin_set=lin_set)
    cdd.matrix_canonicalize(mat)

    poly = cdd.polyhedron_from_matrix(mat)
    ext = cdd.copy_generators(poly)

    vertices = []
    for row in ext.array:
        if row[0] == 1:  # vertex
            vertices.append([float(x) for x in row[1:]])
    return vertices

import multiprocessing as mp

def solve_lp_problem(payoff):
    print("Solving LP problem in parallel...")
    all_tasks = []
    number_of_players = len(payoff)

    for player in range(number_of_players):
        player_shape = payoff[player].shape
        num_strategies = player_shape[player]
        opponent_shape = player_shape[:player] + player_shape[player+1:]
        num_opponent_profiles = int(np.prod(opponent_shape))

        for strategy in range(num_strategies):
            selected_payoff = np.moveaxis(payoff[player], player, 0)[strategy].flatten()
            A, b = [], []

            for alt in range(num_strategies):
                if alt == strategy:
                    continue
                alt_payoff = np.moveaxis(payoff[player], player, 0)[alt].flatten()
                A.append(selected_payoff - alt_payoff)
                b.append(0)

            for i in range(num_opponent_profiles):
                xi_non_negative = np.zeros(num_opponent_profiles)
                xi_non_negative[i] = 1
                A.append(xi_non_negative)
                b.append(0)

                xi_at_most_one = np.zeros(num_opponent_profiles)
                xi_at_most_one[i] = -1
                A.append(xi_at_most_one)
                b.append(1)

            sum_constraint = -np.ones(num_opponent_profiles)
            A.append(sum_constraint)
            b.append(1)
            lin_set = [len(A) - 1]

            all_tasks.append((A, b, lin_set))

    print("Number of tasks:", len(all_tasks))
    print("cpu_count:", mp.cpu_count())
    with mp.Pool(processes=mp.cpu_count()) as pool:
        all_belief_list = pool.map(ext_points_worker, all_tasks)
    
    print("Finished solving LP problem.")
    print(all_belief_list)
    return all_belief_list

def lp_comparison(gen_payoff, ref_payoff):
    # Solve LP problem for generated game
    gen_beliefs = solve_lp_problem(gen_payoff)

    # Solve LP problem for reference game
    ref_beliefs = solve_lp_problem(ref_payoff)

    # Compare the beliefs
    if gen_beliefs == ref_beliefs:
        print("The games are equivalent.")
        return True
    else:
        print("The games are not equivalent.")
        return False


if __name__ == '__main__':
    # gen_path = "Output/Imperfect_Information_Games/Bach_or_Stravinsky/1.efg"
    # ref_path = "Dataset/Imperfect_Information_Games/Bach_or_Stravinsky/Reference/ref.efg"

    gen_path = "Output_temp/Kuhn_Poker/1.efg"
    ref_path = "Dataset/Imperfect_Information_Games/Kuhn_Poker/Reference/ref.efg"

    # gen_path = "Output/Imperfect_Information_Games/Bagwell/1.efg"
    # ref_path = "Dataset/Imperfect_Information_Games/Bagwell/Reference/ref.efg"

    # gen_path = "Output/Imperfect_Information_Games/A_Three_Player_Game/1.efg"
    # ref_path = "Dataset/Imperfect_Information_Games/A_Three_Player_Game/Reference/ref.efg"
    reference_game = get_payoff_matrix(ref_path)
    print(reference_game)
    generated_game = get_payoff_matrix(gen_path)
    print(generated_game)

    result = lp_comparison(generated_game, reference_game)

    print("Result of LP comparison:", result)