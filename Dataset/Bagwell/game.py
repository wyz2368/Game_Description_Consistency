import pygambit as gbt

# Parameters
epsilon = gbt.Rational(1, 100)  # 0.01

# Create game with Player 1 first, Player 2 second
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Noisy leader game")

# Player 1 chooses C or S at the root
g.append_move(g.root, "Player 1", ["C", "S"])

# Define outcomes (payoff vectors are [Player 1, Player 2])
out_C_C = g.add_outcome([1, 3], label="(C,C)")
out_C_S = g.add_outcome([3, 2], label="(C,S)")
out_S_S = g.add_outcome([2, 1], label="(S,S)")
out_S_C = g.add_outcome([0, 0], label="(S,C)")

# For each Player 1 action node, append a chance node (signal),
# set its probabilities, then append Player 2's decision and set outcomes.
for i, p1_node in enumerate(g.root.children):
    # Append chance (nature) producing the observed signal
    g.append_move(p1_node, g.players.chance, ["Signal C", "Signal S"])

    # Set chance probabilities depending on which action Player 1 chose
    # If Player 1 chose "C" (i == 0): Prob(signal=C)=1-epsilon, signal=S=epsilon
    # If Player 1 chose "S" (i == 1): Prob(signal=C)=epsilon,    signal=S=1-epsilon
    if i == 0:  # Player 1 played C
        probs = [gbt.Rational(1, 1) - epsilon, epsilon]
    else:       # Player 1 played S
        probs = [epsilon, gbt.Rational(1, 1) - epsilon]
    # Set probabilities on the chance infoset (the infoset is on p1_node)
    g.set_chance_probs(p1_node.infoset, probs)

    # For each chance outcome node (signal C and signal S), append Player 2's move
    for signal_child in p1_node.children:
        g.append_move(signal_child, "Player 2", ["C", "S"])

        # Set outcomes for Player 2 actions; payoffs depend only on actual actions:
        # Determine which Player 1 action we are under (C if i==0 else S)
        if i == 0:  # Player 1 played C
            # Player 2 chooses C -> (C, C)
            g.set_outcome(signal_child.children[0], out_C_C)
            # Player 2 chooses S -> (C, S)
            g.set_outcome(signal_child.children[1], out_C_S)
        else:       # Player 1 played S
            # Player 2 chooses C -> (S, C)
            g.set_outcome(signal_child.children[0], out_S_C)
            # Player 2 chooses S -> (S, S)
            g.set_outcome(signal_child.children[1], out_S_S)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['S'].children['Signal C'], g.root.children['C'].children['Signal C'].infoset)
    g.set_infoset(g.root.children['S'].children['Signal S'], g.root.children['C'].children['Signal S'].infoset)

# Save the EFG
g.to_efg("noisy_leader.efg")