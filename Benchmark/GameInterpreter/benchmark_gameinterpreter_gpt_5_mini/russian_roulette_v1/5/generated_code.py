import pygambit as gbt

# Six-chamber Russian roulette with two players alternating turns.
# Reasoning (in comments):
# - Chance (at g.root) selects the loaded chamber L in {1..6}.
# - The current chamber starts at 1 on the first pull and advances by 1 on each pull.
# - On each player's turn they choose Pull or Quit.
# - If they Quit they get 0 and the other player gets 1.
# - If they Pull and the current chamber is the loaded chamber they die (-1) and the other gets 1.
# - Otherwise play continues to the other player on the next chamber.
#
# We construct the full tree (no loops) up to six pulls. We explicitly create every required node
# and then group decision nodes into information sets so that nodes at the same turn number
# are indistinguishable to the acting player (they do not observe the loaded chamber).
#
# We follow the infoset grouping specified in the problem statement.
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian Roulette")

# Chance chooses loaded chamber L = 1..6 (each with probability 1/6).
g.append_move(g.root, g.players.chance, ["L1", "L2", "L3", "L4", "L5", "L6"])
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                                    gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Stage 1: Player 1's initial decision (before any pulls).
# For each chance outcome create the same decision for Player 1.
g.append_move(g.root.children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[1], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[2], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5], "Player 1", ["Pull", "Quit"])

# Group all Player 1 initial nodes into the same infoset.
g.set_infoset(g.root.children[1], g.root.children[0].infoset)
g.set_infoset(g.root.children[2], g.root.children[0].infoset)
g.set_infoset(g.root.children[3], g.root.children[0].infoset)
g.set_infoset(g.root.children[4], g.root.children[0].infoset)
g.set_infoset(g.root.children[5], g.root.children[0].infoset)

# Stage 2: Player 2's first decision occurs if Player 1 pulled and survived.
# That is possible for L = 2..6 (root.children[1]..root.children[5] on the Pull branch).
g.append_move(g.root.children[1].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "Player 2", ["Pull", "Quit"])

# Group Player 2 first-decision nodes (they do not know L).
g.set_infoset(g.root.children[2].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[1].children[0].infoset)

# Stage 3: Player 1's second decision (after two safe pulls) possible for L = 3..6.
g.append_move(g.root.children[2].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "Player 1", ["Pull", "Quit"])

# Group Player 1 second-decision nodes.
g.set_infoset(g.root.children[3].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[2].children[0].children[0].infoset)

# Stage 4: Player 2's second decision (after three safe pulls) possible for L = 4..6.
g.append_move(g.root.children[3].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Group Player 2 second-decision nodes.
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[3].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[3].children[0].children[0].infoset)

# Stage 5: Player 1's third decision (after four safe pulls) possible for L = 5..6.
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])

# Group Player 1 third-decision nodes.
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].children[0].infoset)

# Stage 6: Player 2's third decision (on chamber 6) occurs only when L = 6.
# This is the Pull branch of the last P1 node for L = 6.
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Note: The infoset for this final node is a singleton (only occurs when L = 6), so no grouping needed.

# Define outcomes to reuse:
p1_dies = g.add_outcome([-1, 1], label="Player1 dies")
p2_dies = g.add_outcome([1, -1], label="Player2 dies")
p1_quit = g.add_outcome([0, 1], label="Player1 quits")
p2_quit = g.add_outcome([1, 0], label="Player2 quits")

# Now set outcomes at all terminal nodes.
# Quit branches (children[1]) for all decision nodes:

# Player 1 initial quits:
g.set_outcome(g.root.children[0].children[1], p1_quit)
g.set_outcome(g.root.children[1].children[1], p1_quit)
g.set_outcome(g.root.children[2].children[1], p1_quit)
g.set_outcome(g.root.children[3].children[1], p1_quit)
g.set_outcome(g.root.children[4].children[1], p1_quit)
g.set_outcome(g.root.children[5].children[1], p1_quit)

# Player 2 first-decision quits:
g.set_outcome(g.root.children[1].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[2].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[3].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[4].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[5].children[0].children[1], p2_quit)

# Player 1 second-decision quits:
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quit)

# Player 2 second-decision quits:
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quit)

# Player 1 third-decision quits:
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quit)

# Player 2 third-decision quits (final node for L=6):
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quit)

# Death branches (Pull on the loaded chamber):
# L = 1: Player 1 dies on first pull
g.set_outcome(g.root.children[0].children[0], p1_dies)

# L = 2: Player 2 dies on second pull
g.set_outcome(g.root.children[1].children[0].children[0], p2_dies)

# L = 3: Player 1 dies on third pull
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_dies)

# L = 4: Player 2 dies on fourth pull
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_dies)

# L = 5: Player 1 dies on fifth pull
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_dies)

# L = 6: Player 2 dies on sixth pull
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_dies)

# Save the EFG
g.to_efg("six_chamber_russian_roulette.efg")