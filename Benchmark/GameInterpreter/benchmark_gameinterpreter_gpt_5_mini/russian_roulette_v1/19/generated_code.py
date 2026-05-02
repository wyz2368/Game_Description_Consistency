import pygambit as gbt

# Build an extensive-form representation of a 2-player Russian Roulette
# with a six-chamber revolver. Chance chooses which chamber (0..5) is loaded
# with equal probability 1/6. Players alternate turns. On each turn the moving
# player can "Quit" (withdraw; gets 0, opponent gets 1) or "Pull" (point the
# gun to own head). If the current chamber is the loaded one, the pulling
# player dies (gets -1, opponent gets 1); otherwise the game continues.
#
# Important encoding detail (to match the provided infoset grouping code):
# - We make the action ordering on each decision node be ["Quit", "Pull"].
#   That way the "Pull" branch is .children[1], and successive pulls along a
#   path are accessed via repeated .children[1].
#
# The code avoids loops and recursion and does not use the '+' operator.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian Roulette")

# Chance: which chamber (1..6) is loaded. This creates g.root.children[0..5].
g.append_move(g.root, g.players.chance,
              ["Chamber 1", "Chamber 2", "Chamber 3",
               "Chamber 4", "Chamber 5", "Chamber 6"])

# Set equal probabilities 1/6 for each chamber.
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6),
                                    gbt.Rational(1, 6),
                                    gbt.Rational(1, 6),
                                    gbt.Rational(1, 6),
                                    gbt.Rational(1, 6),
                                    gbt.Rational(1, 6)])

# Add outcome objects to reuse.
p1_wins = g.add_outcome([1, -1], label="P1 wins")
p2_wins = g.add_outcome([-1, 1], label="P2 wins")
p1_quit = g.add_outcome([0, 1], label="P1 quits")
p2_quit = g.add_outcome([1, 0], label="P2 quits")

# --------------------
# Build the game tree
# For each possible loaded-chamber i (0..5), we create a chain of decision
# nodes at depths d = 0..i. At each node actions are ["Quit", "Pull"].
# The "Pull" branch (.children[1]) either goes to the next decision node (if
# d < i) or results in death (if d == i).
# --------------------

# i = 0 : only depth 0 (Player 1 moves). Pull -> death immediately.
g.append_move(g.root.children[0], "Player 1", ["Quit", "Pull"])

# i = 1 : depth 0 (P1), then depth 1 (P2)
g.append_move(g.root.children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])

# i = 2 : depth 0 (P1), depth 1 (P2), depth 2 (P1)
g.append_move(g.root.children[2], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[2].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[2].children[1].children[1], "Player 1", ["Quit", "Pull"])

# i = 3 : depths 0..3 (P1, P2, P1, P2)
g.append_move(g.root.children[3], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# i = 4 : depths 0..4 (P1, P2, P1, P2, P1)
g.append_move(g.root.children[4], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])

# i = 5 : depths 0..5 (P1, P2, P1, P2, P1, P2)
g.append_move(g.root.children[5], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# --------------------
# Set outcomes for Quit branches and for fatal Pulls.
# For any decision node, children[0] is "Quit" => quitter gets 0, other gets 1.
# For a final-depth node (d == i), children[1] is "Pull" => shooter dies.
# --------------------

# i = 0 (only depth 0)
g.set_outcome(g.root.children[0].children[0], p1_quit)       # P1 quits at d=0
g.set_outcome(g.root.children[0].children[1], p2_wins)       # P1 pulls and dies

# i = 1
# depth 0 (P1)
g.set_outcome(g.root.children[1].children[0], p1_quit)
# depth 1 (P2)
g.set_outcome(g.root.children[1].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[1].children[1].children[1], p1_wins)  # P2 pulls and dies

# i = 2
# depth 0 (P1)
g.set_outcome(g.root.children[2].children[0], p1_quit)
# depth 1 (P2)
g.set_outcome(g.root.children[2].children[1].children[0], p2_quit)
# depth 2 (P1)
g.set_outcome(g.root.children[2].children[1].children[1].children[0], p1_quit)
g.set_outcome(g.root.children[2].children[1].children[1].children[1], p2_wins)  # P1 pulls and dies

# i = 3
# depth 0 (P1)
g.set_outcome(g.root.children[3].children[0], p1_quit)
# depth 1 (P2)
g.set_outcome(g.root.children[3].children[1].children[0], p2_quit)
# depth 2 (P1)
g.set_outcome(g.root.children[3].children[1].children[1].children[0], p1_quit)
# depth 3 (P2)
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[1], p1_wins)  # P2 pulls and dies

# i = 4
# depth 0 (P1)
g.set_outcome(g.root.children[4].children[0], p1_quit)
# depth 1 (P2)
g.set_outcome(g.root.children[4].children[1].children[0], p2_quit)
# depth 2 (P1)
g.set_outcome(g.root.children[4].children[1].children[1].children[0], p1_quit)
# depth 3 (P2)
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[0], p2_quit)
# depth 4 (P1)
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[0], p1_quit)
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[1], p2_wins)  # P1 pulls and dies

# i = 5
# depth 0 (P1)
g.set_outcome(g.root.children[5].children[0], p1_quit)
# depth 1 (P2)
g.set_outcome(g.root.children[5].children[1].children[0], p2_quit)
# depth 2 (P1)
g.set_outcome(g.root.children[5].children[1].children[1].children[0], p1_quit)
# depth 3 (P2)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[0], p2_quit)
# depth 4 (P1)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[0], p1_quit)
# depth 5 (P2)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[1], p1_wins)  # P2 pulls and dies

# --------------------
# Set information sets to represent imperfect information:
# - At a given turn number (number of prior pulls), the player to move knows
#   how many pulls have occurred but not which chamber was initially loaded.
#   Therefore all nodes that occur at the same turn for the same player must
#   be grouped into a single information set.
#
# The following calls implement the grouping described in the problem statement.
# Each set_infoset call is executed only after the relevant append_move calls
# above have created the referenced nodes.
# --------------------

# Player 1, first decision (d = 0): group g.root.children[0..5]
g.set_infoset(g.root.children[1], g.root.children[0].infoset)
g.set_infoset(g.root.children[2], g.root.children[0].infoset)
g.set_infoset(g.root.children[3], g.root.children[0].infoset)
g.set_infoset(g.root.children[4], g.root.children[0].infoset)
g.set_infoset(g.root.children[5], g.root.children[0].infoset)

# Player 2, first decision (d = 1): group g.root.children[1..5].children[1]
g.set_infoset(g.root.children[2].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[3].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1], g.root.children[1].children[1].infoset)

# Player 1, second decision (d = 2): group g.root.children[2..5].children[1].children[1]
g.set_infoset(g.root.children[3].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1], g.root.children[2].children[1].children[1].infoset)

# Player 2, second decision (d = 3): group g.root.children[3..5].children[1].children[1].children[1]
g.set_infoset(g.root.children[4].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)

# Player 1, third decision (d = 4): group g.root.children[4..5].children[1]^4
g.set_infoset(g.root.children[5].children[1].children[1].children[1].children[1], g.root.children[4].children[1].children[1].children[1].children[1].infoset)

# Player 2, third decision (d = 5): only g.root.children[5] with 5 prior pulls -> single node, no grouping required.

# --------------------
# Save the EFG
# --------------------
g.to_efg("six_chamber_revolver.efg")