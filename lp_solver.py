import pulp
import numpy as np

from utils import get_payoff_matrix

def solve_lp_problem(payoff):
    print("Solving LP problem...")

    all_belief_list = []

    number_of_players = len(payoff)
    
    for player in range(number_of_players):
        
        opponent_shape = payoff[player].shape[1:]
        num_opponent_strategies = int(np.prod(opponent_shape))

        num_strategies = payoff[player].shape[0]

        # payoff_matrix = payoff[player].reshape(own_strategies, num_opponent_strategies)


        for strategy in range(num_strategies):
            # Create a linear programming problem
            prob = pulp.LpProblem("BestResponseCheck", sense=pulp.LpMaximize)

            variable_list = [
                pulp.LpVariable(f"opponent_strategy_{i}", lowBound=0, upBound=1, cat="Continuous")
                for i in range(num_opponent_strategies)
            ]
 
            # print(payoff[player][strategy].flatten())
            payoff_strategy = payoff[player][strategy].flatten()
            # Define objective using generated payoff
            objective = pulp.lpSum(
                variable_list[i] * payoff_strategy[i] for i in range(num_opponent_strategies)
            )
            # prob += objective  # set objective

            
            # Add better-response constraints
            for alt in range(num_strategies):
                if alt == strategy:
                    continue
                current_alt_payoff = payoff[player][alt].flatten()
                alt_expr = pulp.lpSum(
                    variable_list[i] * current_alt_payoff[i] for i in range(num_opponent_strategies)
                )
                # print(alt_expr)
                prob += objective >= alt_expr
            
            # Probability distribution constraint
            prob += pulp.lpSum(variable_list) == 1
            
            prob.solve()

            
            # print("Status:", pulp.LpStatus[prob.status]) 
            belief_list = []
            for v in prob.variables():
                # print(v.name, "=", v.varValue)
                belief_list.append(v.varValue)
            all_belief_list.append(belief_list)

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

                
gen_path = "Output/Imperfect_Information_Games/Bach_or_Stravinsky/5.efg"
ref_path = "Dataset/Imperfect_Information_Games/Bach_or_Stravinsky/Reference/ref.efg"

reference_game = get_payoff_matrix(ref_path)
print(reference_game)
generated_game = get_payoff_matrix(gen_path)
print(generated_game)

result = lp_comparison(generated_game, reference_game)

print("Result of LP comparison:", result)

