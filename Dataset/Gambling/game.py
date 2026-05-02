import pygambit as gbt

# Create the game tree with the specified player order
g = gbt.Game.new_tree(players=["Gambler", "Dealer"],
                      title="Gambler decides to enter then Matching Pennies")

# Gambler's initial decision: Enter or Stay out
g.append_move(g.root, "Gambler", ["Enter", "Stay out"])

# If Gambler stays out, terminal payoff [0, 0]
g.set_outcome(g.root.children[1], g.add_outcome([0, 0], label="Stay out"))

# If Gambler enters, he plays Matching Pennies: Gambler chooses Heads/Tails first
enter_node = g.root.children[0]
g.append_move(enter_node, "Gambler", ["Heads", "Tails"])

# For each Gambler Heads/Tails choice, Dealer chooses Heads/Tails
for gambler_choice_node in enter_node.children:
    g.append_move(gambler_choice_node, "Dealer", ["Heads", "Tails"])

# Add outcomes for the four possible action profiles after entering
# Payoffs: if actions match -> Gambler +1, Dealer -1; else Gambler -1, Dealer +1
gambler_wins = g.add_outcome([1, -1], label="Gambler wins (match)")
gambler_loses = g.add_outcome([-1, 1], label="Gambler loses (mismatch)")

# Map outcomes:
# Gambler chose Heads (enter_node.children[0]):
#   Dealer Heads -> match -> gambler wins
g.set_outcome(enter_node.children[0].children[0], gambler_wins)
#   Dealer Tails -> mismatch -> gambler loses
g.set_outcome(enter_node.children[0].children[1], gambler_loses)

# Gambler chose Tails (enter_node.children[1]):
#   Dealer Heads -> mismatch -> gambler loses
g.set_outcome(enter_node.children[1].children[0], gambler_loses)
#   Dealer Tails -> match -> gambler wins
g.set_outcome(enter_node.children[1].children[1], gambler_wins)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['Enter'].children['Tails'], g.root.children['Enter'].children['Heads'].infoset)

# Save the EFG
g.to_efg("gambler_matching_pennies.efg")