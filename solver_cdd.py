from utils import get_payoff_matrix
import cdd
import numpy as np

def ext_points_mat_vec(A,b, lin_set):
    
    #set A to minus A and transorm it to np array, as c
    A = -np.array(A)
    
    #transorm b to np array, as required by pycddlib
    # b = np.array(b)
    b = np.array(b).reshape(-1, 1)
    
    #make them into one matrix, as required by pycddlib.
    #it means that the first column is vector b and the other columns are matrix A. 
    #for example, if M =  [[-1,-1],[1,0],[0,1]] and b = [[1],[0],[0]], then you get 
    #M = np.hstack((b,A)) = [[1,-1,-1],[0,1,0],[0,0,1]] 
    #No special logic why we do it exactly like that. It's just that pycddlib needs this format. 
    # print("A:", A)
    # print("b:", b)
    M = np.hstack((b,A))

    print("M:", M.shape)

    print("Starting solving polyhedron...")
    mat = cdd.matrix_from_array(M, rep_type=cdd.RepType.INEQUALITY, lin_set = lin_set)
    # print(mat)
    cdd.matrix_canonicalize(mat)
    print("Canonicalized matrix:", mat)
    poly = cdd.polyhedron_from_matrix(mat)
    print("hi")
    ext = cdd.copy_generators(poly)
    print("Finished solving polyhedron.")

    vertices = []
    # print(ext.array)

    for row in ext.array:
        if row[0] == 1:  # vertex, not ray
            belief = [float(x) for x in row[1:]]
            vertices.append(belief)
    print("Vertices:", vertices)
    
    return vertices

def solve_lp_problem(payoff):
    print("Solving LP problem...")

    all_belief_list = []
    number_of_players = len(payoff)

    for player in range(number_of_players):
        opponent_shape = payoff[player].shape[1:]
        num_opponent_strategies = int(np.prod(opponent_shape))
        num_strategies = payoff[player].shape[0]

        for strategy in range(num_strategies):
            # Payoff vector for the selected strategy
            selected_payoff = payoff[player][strategy].flatten()
            A = []
            b = []

            
            for alt in range(num_strategies):
                if alt == strategy:
                    continue
                
                # Add inequalities for the selected strategy
                alt_payoff = payoff[player][alt].flatten()
                # print("alt_payoff:", alt_payoff)
                # print("selected_payoff:", selected_payoff)
                constraint = alt_payoff - selected_payoff
                A.append(constraint)
                b.append(0)
            
            # Add inequalities for the probability distribution
            for i in range(num_opponent_strategies):
                xi_non_negative = np.zeros(num_opponent_strategies)
                xi_non_negative[i] = -1  # -xi <= 0  (means xi >= 0)
                A.append(xi_non_negative)
                b.append(0)

                xi_at_most_one = np.zeros(num_opponent_strategies)
                xi_at_most_one[i] = 1  # xi <= 1
                A.append(xi_at_most_one)
                b.append(1)

            
            # Add equality constraint for the probability distribution
            sum_constraint = np.ones(num_opponent_strategies)
            A.append(sum_constraint)
            b.append(1)
            lin_set = [len(A) - 1]

            # Solve the LP problem
            ver = ext_points_mat_vec(A, b, lin_set)
            all_belief_list.append(ver)

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

                
# gen_path = "Output/Imperfect_Information_Games/Bach_or_Stravinsky/3.efg"
# ref_path = "Dataset/Imperfect_Information_Games/Bach_or_Stravinsky/Reference/ref.efg"
gen_path = "Output_temp/Kuhn_Poker/1.efg"
ref_path = "Dataset/Imperfect_Information_Games/Kuhn_Poker/Reference/ref.efg"

# gen_path = "Output/Imperfect_Information_Games/Bagwell/5.efg"
# ref_path = "Dataset/Imperfect_Information_Games/Bagwell/Reference/ref.efg"

reference_game = get_payoff_matrix(ref_path)
print(reference_game)
generated_game = get_payoff_matrix(gen_path)
print(generated_game)

result = lp_comparison(generated_game, reference_game)

print("Result of LP comparison:", result)

