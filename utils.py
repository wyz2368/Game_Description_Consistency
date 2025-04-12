import pygambit as gbt
import numpy as np

# Convert EFG to NFG to payoff matrix
def get_payoff_matrix(efg_file_path):
    """Get the payoff matrix from a given extensive-form game (EFG) file.
    
    This function reads an EFG file, converts it to a normal-form game (NFG), 
    and extracts the payoff matrix for each player in the game.
    
    Args:
        efg_file_path (str): The file path to the EFG file.
    
    Returns:
        list: A list of numpy arrays representing the payoff matrices for each player, 
        where each array contains the payoffs corresponding to the player's strategies.
    
    Raises:
        FileNotFoundError: If the specified EFG file does not exist.
        ValueError: If the EFG file is not in a valid format.
    """
    efg = gbt.read_efg(efg_file_path)
    payoff_gambit = efg.to_arrays()
    
    print("Payoff Gambit:", payoff_gambit)
    
    payoff = []
    number_of_players = len(payoff_gambit) 
    print("Totol number of players in this game:", number_of_players)
    for i in range(number_of_players):
        payoff.append(payoff_gambit[i].astype(np.float64))
    
    return payoff

def check_strategy_counts(reference_game, generated_game):
    """
    Compares the number of strategies per player in the reference and generated games.
    
    Args:
        reference_game (list of np.ndarray): Payoff matrices for the reference game.
        generated_game (list of np.ndarray): Payoff matrices for the generated game.
    
    Returns:
        bool: True if each player has the same number of strategies in both games, False otherwise.
    """
    num_players_ref = len(reference_game)
    num_players_gen = len(generated_game)

    if num_players_ref != num_players_gen:
        print(f"Different number of players: reference ({num_players_ref}), generated ({num_players_gen})")
        return False

    for player in range(num_players_ref):
        ref_strat_count = reference_game[player].shape[0]
        gen_strat_count = generated_game[player].shape[0]
        if ref_strat_count != gen_strat_count:
            print(f"Mismatch in strategies for player {player}: reference ({ref_strat_count}), generated ({gen_strat_count})")
            return False

    print("Number of strategies per player match between reference and generated games.")
    return True
