import numpy as np
from fractions import Fraction
import shutil
import os
import subprocess

def convert_to_lp(payoff, game_name):
    print("Converting LP problem...")

    number_of_players = len(payoff)

    for player in range(number_of_players):
        player_shape = payoff[player].shape
        num_strategies = player_shape[player]
        opponent_shape = player_shape[:player] + player_shape[player+1:]
        num_opponent_profiles = int(np.prod(opponent_shape))
        payoff_axis_moved = np.moveaxis(payoff[player], player, 0)

        for strategy in range(num_strategies):
            selected_payoff = payoff_axis_moved[strategy].flatten()

            # 1. Strategy deviation constraints
            A_rows = []
            b_rows = []

            for alt in range(num_strategies):
                if alt == strategy:
                    continue
                alt_payoff = payoff_axis_moved[alt].flatten()
                constraint = selected_payoff - alt_payoff
                A_rows.append(constraint)
                b_rows.append(Fraction(0))

            # 2. xi ≥ 0 constraints
            A_rows.extend(np.eye(num_opponent_profiles))
            b_rows.extend([Fraction(0)] * num_opponent_profiles)

            # 3. xi ≤ 1 constraints (represented as -xi + 1 ≥ 0 → -xi ≤ 1)
            A_rows.extend(-np.eye(num_opponent_profiles))
            b_rows.extend([Fraction(1)] * num_opponent_profiles)

            # 4. Sum xi = 1 (equality constraint)
            sum_constraint = -np.ones(num_opponent_profiles)
            A_rows.append(sum_constraint)
            b_rows.append(Fraction(1))


            linear_index = len(A_rows)

            file_name = game_name + f"lp_solver_{player}_{strategy}.txt"
            with open(file_name, 'w') as f:
                f.write("H-representation\n")
                f.write(f"linearity 1 {linear_index}\n")
                f.write("begin\n")
                f.write(f"{len(A_rows)} {num_opponent_profiles + 1} rational\n")  # +1 for b

                for i in range(len(A_rows)):
                    b_str = str(b_rows[i])
                    row_strs = [str(Fraction(x)) for x in A_rows[i]]
                    f.write(f"{b_str} " + " ".join(row_strs) + "\n")

                f.write("end\n")

            print(f"Saved: {file_name} with {len(A_rows)} constraints")


def parse_lrs_vertices(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    vertices = []
    inside = False
    for line in lines:
        if line.strip() == "begin":
            inside = True
            continue
        if line.strip() == "end":
            break
        if inside:
            parts = line.strip().split()
            if parts and parts[0] == '1':  # Vertices start with 1
                vertex = tuple(Fraction(x) for x in parts[1:])
                vertices.append(vertex)
    return sorted(vertices)

def check_vertex_best_response(payoff_ref, payoff_gen, game_name):
    print("Checking vertex best response...")
    
    ref_dir = game_name + "_ref"
    gen_dir = game_name + "_gen"

    os.makedirs(ref_dir, exist_ok=True)
    os.makedirs(gen_dir, exist_ok=True)

    convert_to_lp(payoff_ref, os.path.join(game_name + "_ref", ""))
    convert_to_lp(payoff_gen, os.path.join(game_name + "_gen", ""))

    number_of_players = len(payoff_ref)
    try:
        for player in range(number_of_players):
            player_shape = payoff_ref[player].shape
            num_strategies = player_shape[player]

            for strategy in range(num_strategies):
                ref_lp = os.path.join(game_name + "_ref", f"lp_solver_{player}_{strategy}.txt")
                gen_lp = os.path.join(game_name + "_gen", f"lp_solver_{player}_{strategy}.txt")

                ref_output = ref_lp.replace(".txt", "_out.txt")
                gen_output = gen_lp.replace(".txt", "_out.txt")

                subprocess.run(["lrs", ref_lp, ref_output], check=True)
                subprocess.run(["lrs", gen_lp, gen_output], check=True)

                ref_vertices = parse_lrs_vertices(ref_output)
                gen_vertices = parse_lrs_vertices(gen_output)

                if ref_vertices != gen_vertices:
                    print(f"Mismatch in vertices for player {player}, strategy {strategy}")
                    return False
    finally:
        shutil.rmtree(ref_dir)
        shutil.rmtree(gen_dir)

    print("All vertices match.")
    return True

    
    