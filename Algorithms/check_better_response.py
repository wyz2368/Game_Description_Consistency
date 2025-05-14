import numpy as np
import sympy as sp

def check_better_response(payoff_gen, payoff_ref):
    number_of_players = len(payoff_gen)

    for player in range(number_of_players):
        gen = np.asarray(payoff_gen[player]).flatten()
        ref = np.asarray(payoff_ref[player]).flatten()

        for i in range(len(ref)):
            for j in range(i + 1, len(ref)):
                x1, x2 = ref[i], ref[j]
                y1, y2 = gen[i], gen[j]

                # Avoid division by zero
                if x1 == x2:
                    if y1 != y2:
                        return False
                    continue

                # Try candidate affine transformation
                
                a = (y2 - y1) / (x2 - x1)
                b = y1 - a * x1

                # Check if it works for all points
                if all(gen[k] == a * ref[k] + b for k in range(len(ref))):
                    break  # Found valid affine mapping
            else:
                continue  # No break, try next i
            break  # Found valid mapping, skip remaining i
        else:
            return False  # No valid affine mapping found

    return True





