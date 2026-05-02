import pygambit as gbt

# Build an extensive-form game for alternating "Russian roulette" with 6 chambers.
# Reasoning (step-by-step in comments below):
# - Players: Player 1 and Player 2.
# - State at each decision: (player_to_move, number_of_remaining_chambers).
# - Every trigger-pull outcome (fire / no fire) is public, so this is a perfect-information tree.
# - At each decision node a player has two actions: "Quit" (guaranteed survival; other player wins)
#   or "Pull" (risk of immediate death; otherwise play continues with one fewer chamber).
# - If remaining_chambers > 1 and a player pulls, there is a chance node:
#     P(fire) = 1 / remaining_chambers
#     P(not fire) = (remaining_chambers - 1) / remaining_chambers
# - If remaining_chambers == 1 and a player pulls, the gun fires for certain (no chance node needed).
# - Payoffs (order: [Player 1, Player 2]):
#     - If a player quits: quitter 0, other player 1.
#     - If a player is shot: shooter -1, other player 1.
#
# We expand the tree explicitly without loops or recursion.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# Pre-create the four distinct outcomes we will reuse:
o_p1_quits = g.add_outcome([0, 1], label="P1 quits")
o_p2_quits = g.add_outcome([1, 0], label="P2 quits")
o_p1_dies = g.add_outcome([-1, 1], label="P1 dies")
o_p2_dies = g.add_outcome([1, -1], label="P2 dies")

# Root: Player 1 to move with 6 chambers remaining.
# Player 1 actions: "Quit" or "Pull"
g.append_move(g.root, "Player 1", ["Quit", "Pull"])
# If P1 quits immediately: P1 gets 0, P2 gets 1.
g.set_outcome(g.root.children[0], o_p1_quits)

# If P1 pulls (6 chambers), chance: fire with prob 1/6, not fire with prob 5/6.
g.append_move(g.root.children[1], g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(g.root.children[1].infoset, [gbt.Rational(1, 6), gbt.Rational(5, 6)])
# Fire => P1 dies.
g.set_outcome(g.root.children[1].children[0], o_p1_dies)

# No fire => now Player 2 to move with 5 chambers remaining.
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
# If P2 quits at 5: P2 gets 0, P1 gets 1.
g.set_outcome(g.root.children[1].children[1].children[0], o_p2_quits)

# If P2 pulls (5 chambers), chance: fire with prob 1/5, not fire with prob 4/5.
g.append_move(g.root.children[1].children[1].children[1], g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(g.root.children[1].children[1].children[1].infoset,
                   [gbt.Rational(1, 5), gbt.Rational(4, 5)])
# Fire => P2 dies.
g.set_outcome(g.root.children[1].children[1].children[1].children[0], o_p2_dies)

# No fire => Player 1 to move with 4 chambers remaining.
g.append_move(g.root.children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
# If P1 quits at 4: P1 gets 0, P2 gets 1.
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[0], o_p1_quits)

# If P1 pulls (4 chambers), chance: fire with prob 1/4, not fire with prob 3/4.
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1],
              g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(g.root.children[1].children[1].children[1].children[1].children[1].infoset,
                   [gbt.Rational(1, 4), gbt.Rational(3, 4)])
# Fire => P1 dies.
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[0],
              o_p1_dies)

# No fire => Player 2 to move with 3 chambers remaining.
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1],
              "Player 2", ["Quit", "Pull"])
# If P2 quits at 3: P2 gets 0, P1 gets 1.
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[0],
              o_p2_quits)

# If P2 pulls (3 chambers), chance: fire with prob 1/3, not fire with prob 2/3.
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1],
              g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].infoset,
                   [gbt.Rational(1, 3), gbt.Rational(2, 3)])
# Fire => P2 dies.
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0],
              o_p2_dies)

# No fire => Player 1 to move with 2 chambers remaining.
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1],
              "Player 1", ["Quit", "Pull"])
# If P1 quits at 2: P1 gets 0, P2 gets 1.
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0],
              o_p1_quits)

# If P1 pulls (2 chambers), chance: fire with prob 1/2, not fire with prob 1/2.
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1],
              g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].infoset,
                   [gbt.Rational(1, 2), gbt.Rational(1, 2)])
# Fire => P1 dies.
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0],
              o_p1_dies)

# No fire => Player 2 to move with 1 chamber remaining.
# When remaining == 1 and the player pulls, the gun fires for certain. So we only need a decision node
# for Player 2 with two terminal actions: Quit (safe) or Pull (certain death).
g.append_move(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1],
    "Player 2", ["Quit", "Pull"])
# If P2 quits at 1: P2 gets 0, P1 gets 1.
g.set_outcome(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0],
    o_p2_quits)
# If P2 pulls at 1: gun fires for certain => P2 dies.
g.set_outcome(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1],
    o_p2_dies)

# Save the EFG to a file.
g.to_efg("six_chamber_russian_roulette.efg")