import pygambit as gbt

# Six-chamber alternating Russian roulette
# Players alternate pulling a six-chamber revolver. Player 1 starts.
# Nature chooses the loaded chamber L in {1..6} at the root.
# On each turn t (1-based), the current player chooses Pull or Quit.
# - Quit: quitting player gets 0, other player gets 1 (game ends).
# - Pull: if the current chamber equals the loaded chamber L, the pulling player dies:
#         he gets -1, the other gets 1 (game ends).
#         otherwise play passes to the other player and the game continues to next turn.
#
# We build the full tree explicitly and group decision nodes that are indistinguishable
# for a player at the same turn into infosets as described in the problem statement.
#
# Comments explain the reasoning step-by-step alongside the explicit node calls.
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# 1) Chance at the root: Nature selects the loaded chamber L = 1..6 with equal probability.
g.append_move(g.root, g.players.chance,
              ["Chamber 1", "Chamber 2", "Chamber 3", "Chamber 4", "Chamber 5", "Chamber 6"])
g.set_chance_probs(g.root.infoset,
                   [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                    gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Prepare common outcomes to reuse
p1_dies = g.add_outcome([-1, 1], label="Player1 dies")
p2_dies = g.add_outcome([1, -1], label="Player2 dies")
p1_quit = g.add_outcome([0, 1], label="Player1 quits")
p2_quit = g.add_outcome([1, 0], label="Player2 quits")

# ---------------------------------------------------------------------
# TURN 1 (t = 1): Player 1 moves at all nodes root.children[0]..root.children[5]
# For each possible L = 1..6 there is a node at root.children[L-1].
# The player cannot distinguish which L it is, so these nodes form an infoset.
# Append Player 1's move at each of these six nodes: actions ["Pull","Quit"].
g.append_move(g.root.children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[1], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[2], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5], "Player 1", ["Pull", "Quit"])

# Set Turn 1 infoset: group all six nodes together (use children[1].infoset as representative)
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Outcomes for Turn 1:
# - If Player 1 quits at any of these nodes: Player1 gets 0, Player2 gets 1.
g.set_outcome(g.root.children[0].children[1], p1_quit)
g.set_outcome(g.root.children[1].children[1], p1_quit)
g.set_outcome(g.root.children[2].children[1], p1_quit)
g.set_outcome(g.root.children[3].children[1], p1_quit)
g.set_outcome(g.root.children[4].children[1], p1_quit)
g.set_outcome(g.root.children[5].children[1], p1_quit)

# - If L = 1 and Player 1 pulls at Turn 1: immediate death for Player 1.
g.set_outcome(g.root.children[0].children[0], p1_dies)
# For L >= 2 Pull at Turn 1 survives and passes play to Turn 2 nodes (we will append those moves next).

# ---------------------------------------------------------------------
# TURN 2 (t = 2): Player 2 moves when the gun has not yet fired and t = 2.
# These are the nodes reached after a successful Pull at Turn 1 for L = 2..6:
# root.children[1].children[0], root.children[2].children[0], ..., root.children[5].children[0].
g.append_move(g.root.children[1].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "Player 2", ["Pull", "Quit"])

# Group Turn 2 nodes into one infoset (representative is root.children[2].children[0].infoset)
g.set_infoset(g.root.children[1].children[0], g.root.children[2].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[2].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[2].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[2].children[0].infoset)

# Outcomes for Turn 2:
# - If Player 2 quits at Turn 2 nodes: Player2 gets 0, Player1 gets 1.
g.set_outcome(g.root.children[1].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[2].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[3].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[4].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[5].children[0].children[1], p2_quit)

# - If L = 2 and Player 2 pulls at Turn 2: immediate death for Player 2.
g.set_outcome(g.root.children[1].children[0].children[0], p2_dies)
# For L >= 3 Pull at Turn 2 survives and passes play to Turn 3 nodes.

# ---------------------------------------------------------------------
# TURN 3 (t = 3): Player 1 moves when L = 3..6.
# Nodes are after two successful pulls: root.children[2].children[0].children[0], ... root.children[5]...
g.append_move(g.root.children[2].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "Player 1", ["Pull", "Quit"])

# Group Turn 3 nodes (representative root.children[3].children[0].children[0].infoset)
g.set_infoset(g.root.children[2].children[0].children[0], g.root.children[3].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[3].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[3].children[0].children[0].infoset)

# Outcomes for Turn 3:
# - Quit by Player1 -> Player1 gets 0, Player2 gets 1.
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quit)

# - If L = 3 and Player1 pulls at Turn 3: Player1 dies.
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_dies)
# For L >= 4 Pull at Turn 3 survives and passes play to Turn 4 nodes.

# ---------------------------------------------------------------------
# TURN 4 (t = 4): Player 2 moves when L = 4..6.
# Nodes are after three successful pulls: root.children[3].children[0].children[0].children[0], ...
g.append_move(g.root.children[3].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Group Turn 4 nodes (representative root.children[4].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[3].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].infoset)

# Outcomes for Turn 4:
# - Quit by Player2 -> Player2 gets 0, Player1 gets 1.
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quit)

# - If L = 4 and Player2 pulls at Turn 4: Player2 dies.
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_dies)
# For L >= 5 Pull at Turn 4 survives and passes play to Turn 5 nodes.

# ---------------------------------------------------------------------
# TURN 5 (t = 5): Player 1 moves when L = 5..6.
# Nodes are after four successful pulls: root.children[4].children[0].children[0].children[0].children[0], ...
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])

# Group Turn 5 nodes (representative root.children[5].children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0].children[0].children[0], g.root.children[5].children[0].children[0].children[0].children[0].infoset)

# Outcomes for Turn 5:
# - Quit by Player1 -> Player1 gets 0, Player2 gets 1.
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quit)

# - If L = 5 and Player1 pulls at Turn 5: Player1 dies.
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_dies)
# For L = 6: Pull at Turn 5 survives and passes play to Turn 6 node (we will append Turn 6 next).

# ---------------------------------------------------------------------
# TURN 6 (t = 6): Player 2 moves when L = 6 only.
# The Turn 6 decision node for L = 6 is reached after five successful pulls:
# root.children[5] with five successive children[0] accesses.
# That node is the Pull-child of the Turn 5 node for L = 6:
turn6_node = g.root.children[5].children[0].children[0].children[0].children[0].children[0]
# Append Player 2's move at this Turn 6 node.
g.append_move(turn6_node, "Player 2", ["Pull", "Quit"])

# No infoset grouping needed for Turn 6 since it is a single node (L = 6 only).

# Outcomes for Turn 6:
# - Quit by Player2 -> Player2 gets 0, Player1 gets 1.
g.set_outcome(turn6_node.children[1], p2_quit)

# - If Player2 pulls at Turn 6 and L = 6: Player2 dies.
g.set_outcome(turn6_node.children[0], p2_dies)

# ---------------------------------------------------------------------
# Save the game to EFG
g.to_efg("six_chamber_russian_roulette.efg")