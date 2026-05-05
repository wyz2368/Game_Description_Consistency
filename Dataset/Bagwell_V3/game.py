import pygambit as gbt

# Parameters
epsilon = gbt.Rational(1, 100)  # 0.01
p_same = gbt.Rational(99, 100)  # 0.99

# Create game
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Noisy-leader game (epsilon=0.01)")

# Player 1 moves first: choose C or S
g.append_move(g.root, "Player 1", ["C", "S"])

# Define outcomes consistent with the described rankings and worst-payoff values:
# (C,C): [4,4]
# (C,S): [6,3]
# (S,C): [3,1]  <- worst for both as specified numeric values
# (S,S): [5,2]
out_CC = g.add_outcome([4, 4], label="C,C")
out_CS = g.add_outcome([6, 3], label="C,S")
out_SC = g.add_outcome([3, 1], label="S,C")
out_SS = g.add_outcome([5, 2], label="S,S")

# For each node after Player 1's action, append the chance (signal) move,
# set its signal probabilities, then append Player 2's decision for each signal.
# Do this separately for the node where Player 1 played C and where Player 1 played S.

# Node after Player 1 plays C
node_after_C = g.root.children[0]
g.append_move(node_after_C, g.players.chance, ["Signal C", "Signal S"])
# Set probabilities: Prob(signal=C | P1=C) = 0.99, Prob(signal=S | P1=C) = 0.01
g.set_chance_probs(node_after_C.infoset, [p_same, epsilon])

# For each realized signal under P1=C, append Player 2's move and set outcomes
for signal_node in node_after_C.children:
    g.append_move(signal_node, "Player 2", ["C", "S"])
    # signal_node.children[0] corresponds to Player 2 choosing C, children[1] to S
    # Both terminal nodes correspond to the action profile where P1 played C
    g.set_outcome(signal_node.children[0], out_CC)  # (C,C)
    g.set_outcome(signal_node.children[1], out_CS)  # (C,S)

# Node after Player 1 plays S
node_after_S = g.root.children[1]
g.append_move(node_after_S, g.players.chance, ["Signal C", "Signal S"])
# Set probabilities: Prob(signal=C | P1=S) = 0.01, Prob(signal=S | P1=S) = 0.99
g.set_chance_probs(node_after_S.infoset, [epsilon, p_same])

# For each realized signal under P1=S, append Player 2's move and set outcomes
for signal_node in node_after_S.children:
    g.append_move(signal_node, "Player 2", ["C", "S"])
    # Both terminal nodes correspond to the action profile where P1 played S
    g.set_outcome(signal_node.children[0], out_SC)  # (S,C)
    g.set_outcome(signal_node.children[1], out_SS)  # (S,S)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['S'].children['Signal C'], g.root.children['C'].children['Signal C'].infoset)
    g.set_infoset(g.root.children['S'].children['Signal S'], g.root.children['C'].children['Signal S'].infoset)

# Save the EFG
g.to_efg("noisy_leader_game.efg")