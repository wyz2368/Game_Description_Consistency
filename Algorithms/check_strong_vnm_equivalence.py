import numpy as np
import sympy as sp

def check_strong_vnm_equivalence(payoff_gen, payoff_ref):
    number_of_players = len(payoff_gen)

    for player in range(number_of_players):
        gen = np.asarray(payoff_gen[player]).flatten()
        ref = np.asarray(payoff_ref[player]).flatten()

        for i in range(len(ref)):
            x1 = ref[i]
            y1 = gen[i]

            # Avoid division by zero
            if x1 == 0:
                if y1 != 0:
                    return False
                continue

            # Try candidate linear transformation y = ax
            a = y1 / x1

            # Check if it works for all points
            if all(gen[k] == a * ref[k] for k in range(len(ref))):
                break  # Found valid linear mapping
            else:
                return False  # Unique a failed -> impossible overall
        else:
            return False  # No valid linear mapping found

    return True