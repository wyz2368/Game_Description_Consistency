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
    efg = gbt.Game.read_game(efg_file_path)
    nfg_str = efg.write(format='nfg')
    nfg = gbt.Game.parse_game(nfg_str)
    payoff_gambit = nfg.to_arrays()
    
    payoff = []
    number_of_players = len(payoff_gambit) 
    print("Totol number of players in this game:", number_of_players)
    for i in range(number_of_players):
        payoff.append(payoff_gambit[i].astype(np.float64))
    
    return payoff