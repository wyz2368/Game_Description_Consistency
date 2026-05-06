import pygambit as gbt

# Create the game with explicit player order
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Noisy-leader game")

# Player 1 moves first: choose C or S
g.append_move(g.root, "Player 1", ["C", "S"])

# Signal accuracy
epsilon = gbt.Rational(1, 100)
p_same = gbt.Rational(99, 100)

# For each Player 1 action node, add the chance node (signal) and then Player 2's move
for i, p1_node in enumerate(g.root.children):
    # Add chance move under this Player 1 node
    g.append_move(p1_node, g.players.chance, ["Signal C", "Signal S"])

    # Set chance probabilities conditional on Player 1's action
    # If Player 1 played C (i == 0): Prob(signal=C) = 99/100, Prob(signal=S) = 1/100
    # If Player 1 played S (i == 1): Prob(signal=C) = 1/100,  Prob(signal=S) = 99/100
    if i == 0:
        g.set_chance_probs(p1_node.infoset, [p_same, epsilon])
    else:
        g.set_chance_probs(p1_node.infoset, [epsilon, p_same])

    # For each signal node under this chance node, add Player 2's decision
    for sig_node in p1_node.children:
        g.append_move(sig_node, "Player 2", ["C", "S"])

# Define outcomes (ordering: [Player 1 payoff, Player 2 payoff])
out_CC = g.add_outcome([4, 6], label="(C,C)")
out_CS = g.add_outcome([6, 5], label="(C,S)")
out_SC = g.add_outcome([3, 3], label="(S,C)")
out_SS = g.add_outcome([5, 4], label="(S,S)")

# Assign outcomes to each terminal node.
# Structure: g.root.children[i] corresponds to Player1 action (i=0 -> C, i=1 -> S)
# Each p1_node has two signal children; under each signal child there are two terminal nodes
# for Player2 actions k=0 -> C, k=1 -> S. Outcome depends only on (i, k).
for i, p1_node in enumerate(g.root.children):
    for sig_node in p1_node.children:
        for k, terminal in enumerate(sig_node.children):
            if i == 0 and k == 0:   # Player1=C, Player2=C
                g.set_outcome(terminal, out_CC)
            elif i == 0 and k == 1: # Player1=C, Player2=S
                g.set_outcome(terminal, out_CS)
            elif i == 1 and k == 0: # Player1=S, Player2=C
                g.set_outcome(terminal, out_SC)
            elif i == 1 and k == 1: # Player1=S, Player2=S
                g.set_outcome(terminal, out_SS)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['S'].children['Signal C'], g.root.children['C'].children['Signal C'].infoset)
    g.set_infoset(g.root.children['S'].children['Signal S'], g.root.children['C'].children['Signal S'].infoset)

# Save the EFG
g.to_efg("noisy_leader.efg")