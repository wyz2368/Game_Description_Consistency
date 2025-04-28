import pulp
import numpy as np

from utils import get_payoff_matrix

import numpy as np
from scipy.optimize import linprog
from utils import get_payoff_matrix

import cdd
import numpy as np

def enumerate_vertices(A_ub, b_ub, A_eq, b_eq):
    rows = []

    # Determine number of variables
    if A_ub is not None:
        n_vars = A_ub.shape[1]
    elif A_eq is not None:
        n_vars = A_eq.shape[1]
    else:
        raise ValueError("At least one of A_ub or A_eq must be provided")
    
    if A_ub is not None:
        for i in range(len(A_ub)):
            rows.append([b_ub[i]] + [-x for x in A_ub[i]])

    if A_eq is not None:
        for i in range(len(A_eq)):
            # A_eq x = b_eq ⇔ A_eq x ≤ b_eq and A_eq x ≥ b_eq
            rows.append([b_eq[i]] + [-x for x in A_eq[i]])
            rows.append([-b_eq[i]] + [x for x in A_eq[i]])
    
    for i in range(n_vars):
        row_lb = [0] + [0] * n_vars
        row_lb[i + 1] = 1  # -x_i <= 0 → x_i >= 0
        rows.append(row_lb)

        row_ub = [1] + [0] * n_vars
        row_ub[i + 1] = -1  # x_i <= 1
        rows.append(row_ub)
    
    # print(rows)

    print("Starting solving polyhedron...")
    mat = cdd.matrix_from_array(rows, rep_type=cdd.RepType.INEQUALITY)
    # print(mat)
    poly = cdd.polyhedron_from_matrix(mat)
    ext = cdd.copy_generators(poly)
    print("Finished solving polyhedron.")

    print(ext.array)
    vertices = []

    for row in ext.array:
        if row[0] == 1:  # vertex, not ray
            belief = [float(x) for x in row[1:]]
            vertices.append(belief)
    
    return vertices



def solve_lp_problem(payoff):
    print("Solving LP problem using scipy.optimize.linprog...")

    all_belief_list = []
    number_of_players = len(payoff)

    for player in range(number_of_players):
        opponent_shape = payoff[player].shape[1:]
        num_opponent_strategies = int(np.prod(opponent_shape))
        num_strategies = payoff[player].shape[0]

        for strategy in range(num_strategies):
            # Payoff vector for the selected strategy
            selected_payoff = payoff[player][strategy].flatten()

            # # Objective: minimize zero vector (feasibility problem)
            # c = np.zeros(num_opponent_strategies)

            # Inequality constraints: selected >= alt → selected - alt >= 0
            A_ub = []
            b_ub = []

            for alt in range(num_strategies):
                if alt == strategy:
                    continue
                alt_payoff = payoff[player][alt].flatten()
                constraint = alt_payoff - selected_payoff
                A_ub.append(constraint)
                b_ub.append(0)

            A_ub = np.array(A_ub) if A_ub else None
            b_ub = np.array(b_ub) if b_ub else None

            # Equality constraint: sum of probabilities = 1
            A_eq = np.ones((1, num_opponent_strategies))
            b_eq = np.array([1])

            # # Bounds: [0, 1] for all variables
            # bounds = [(0, 1)] * num_opponent_strategies

            ver = enumerate_vertices(A_ub, b_ub, A_eq, b_eq)
            all_belief_list.append(ver)

            # res = linprog(c, A_ub=A_ub, b_ub=b_ub,
            #               A_eq=A_eq, b_eq=b_eq,
            #               bounds=bounds, method='highs')

            # if res.success:
            #     print(f"Player {player}, Strategy {strategy} — feasible belief found")
            #     print("Belief:", res.x)
            #     all_belief_list.append(np.round(res.x, 6).tolist())
            # else:
            #     print(f"Player {player}, Strategy {strategy} — infeasible")
            #     all_belief_list.append(None)

    print("Belief list:", all_belief_list)
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

                
gen_path = "Output/Imperfect_Information_Games/Bach_or_Stravinsky/3.efg"
ref_path = "Dataset/Imperfect_Information_Games/Bach_or_Stravinsky/Reference/ref.efg"

# gen_path = "Output_temp/Kuhn_Poker/1.efg"
# ref_path = "Dataset/Imperfect_Information_Games/Kuhn_Poker/Reference/ref.efg"

reference_game = get_payoff_matrix(ref_path)
print(reference_game)
generated_game = get_payoff_matrix(gen_path)
print(generated_game)

result = lp_comparison(generated_game, reference_game)

print("Result of LP comparison:", result)



