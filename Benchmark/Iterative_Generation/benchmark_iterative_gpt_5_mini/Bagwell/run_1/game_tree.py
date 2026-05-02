import pygambit as gbt

# Parameters
epsilon = 0.01  # noise parameter

# Payoff assignments respecting E > A > F > W > B > D
E = 6
A = 5
F = 4
W = 3
B = 2
D = 1

# Create game
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Noisy-leader game")

# Player 1 chooses C or S
g.append_move(g.root, "Player 1", ["C", "S"])

# For each Player 1 action, add chance (signal) and then Player 2 decision
# Do not create information sets for Player 2 (we are not modeling imperfect information)
# Append chance moves one node at a time and set probabilities separately.
# Order of chance actions: ["Signal C", "Signal S"]
# For Player1 = C (root.children[0]): P(phi=C|C)=0.99, P(phi=S|C)=0.01
# For Player1 = S (root.children[1]): P(phi=C|S)=0.01, P(phi=S|S)=0.99

# Append chance moves at each Player 1 child
g.append_move(g.root.children[0], g.players.chance, ["Signal C", "Signal S"])
g.append_move(g.root.children[1], g.players.chance, ["Signal C", "Signal S"])

# Set chance probabilities using Rational
# For P1 = C
g.set_chance_probs(g.root.children[0].infoset,
                   [gbt.Rational(99, 100), gbt.Rational(1, 100)])
# For P1 = S
g.set_chance_probs(g.root.children[1].infoset,
                   [gbt.Rational(1, 100), gbt.Rational(99, 100)])

# Now for each chance outcome node, append Player 2's decision ["C", "S"]
# Iterate over the two Player1 branches and their two signal children
for p1_child in g.root.children:
    for signal_child in p1_child.children:
        g.append_move(signal_child, "Player 2", ["C", "S"])

# Add outcomes (Player1 payoff first, Player2 payoff second)
out_both_S = g.add_outcome([A, B], label="both S")
out_S_C = g.add_outcome([W, D], label="P1 S, P2 C")
out_C_S = g.add_outcome([E, W], label="P1 C, P2 S")
out_both_C = g.add_outcome([F, F], label="both C")

# Assign outcomes to terminal nodes.
# Structure of indices:
# g.root.children[0] -> Player1 = C
#   .children[0] -> Signal C
#       .children[0] -> P2 chooses C
#       .children[1] -> P2 chooses S
#   .children[1] -> Signal S
#       .children[0] -> P2 chooses C
#       .children[1] -> P2 chooses S
# g.root.children[1] -> Player1 = S (same structure for signals)

# Player1 = C branch
# If Player2 chooses C -> both C => (F, F)
g.set_outcome(g.root.children[0].children[0].children[0], out_both_C)
g.set_outcome(g.root.children[0].children[1].children[0], out_both_C)
# If Player2 chooses S -> P1=C, P2=S => (E, W)
g.set_outcome(g.root.children[0].children[0].children[1], out_C_S)
g.set_outcome(g.root.children[0].children[1].children[1], out_C_S)

# Player1 = S branch
# If Player2 chooses C -> P1=S, P2=C => (W, D)
g.set_outcome(g.root.children[1].children[0].children[0], out_S_C)
g.set_outcome(g.root.children[1].children[1].children[0], out_S_C)
# If Player2 chooses S -> both S => (A, B)
g.set_outcome(g.root.children[1].children[0].children[1], out_both_S)
g.set_outcome(g.root.children[1].children[1].children[1], out_both_S)

# Save the EFG
g.to_efg("noisy_leader_game.efg")