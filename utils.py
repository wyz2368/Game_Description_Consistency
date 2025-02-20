import pygambit as gbt
import numpy as np

# Convert EFG to NFG to payoff matrix
def get_payoff_matrix(efg_file_path):
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