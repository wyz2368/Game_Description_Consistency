import pygambit as gbt

# Create the game with two players
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Sequential Russian Roulette with optional withdrawal")

# Reasoning (embedded as comments throughout):
# - The single initial uncertainty is which chamber (1..6) is loaded.
# - We model that by a chance move at the root with six equally likely branches.
# - Each root child corresponds to a fixed loaded chamber (1-based index).
# - Players alternate: Player 1 moves on pulls 1,3,5; Player 2 on pulls 2,4,6.
# - Decision nodes that occur after the same number of safe pulls are indistinguishable
#   to the acting player and therefore belong to the same information set.
# - Action labels at each decision are ["Quit", "Pull"] where Quit yields 0 to the quitter
#   and 1 to the other player; Pull either kills the pulling player (if it is the loaded
#   chamber) or passes play to the other player.

# Chance: choose loaded chamber 1..6
g.append_move(g.root, g.players.chance, ["Loaded1", "Loaded2", "Loaded3", "Loaded4", "Loaded5", "Loaded6"])
# Set uniform probabilities 1/6 for each loaded chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# ---------- Append all decision nodes (no loops, explicit calls) ----------
# Player 1 moves at the root children (turn 1 for each possible loaded chamber)
g.append_move(g.root.children[0], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[2], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5], "Player 1", ["Quit", "Pull"])

# Player 2 moves after one safe pull (for loaded chambers 2..6 -> root.children[1..5].children[1])
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[2].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1], "Player 2", ["Quit", "Pull"])

# Player 1 moves after two safe pulls (for loaded chambers 3..6)
g.append_move(g.root.children[2].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1], "Player 1", ["Quit", "Pull"])

# Player 2 moves after three safe pulls (for loaded chambers 4..6)
g.append_move(g.root.children[3].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# Player 1 moves after four safe pulls (for loaded chambers 5..6)
g.append_move(g.root.children[4].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])

# Player 2 moves after five safe pulls (for loaded chamber 6 only)
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# ---------- Create outcomes (reuse outcome objects) ----------
p1_quits = g.add_outcome([0, 1], label="P1 quits")
p2_quits = g.add_outcome([1, 0], label="P2 quits")
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_dies = g.add_outcome([1, -1], label="P2 dies")

# ---------- Set outcomes for every terminal branch ----------
# Loaded = 1 (root.children[0])
# - Quit by P1 (children[0]) -> P1 quits
g.set_outcome(g.root.children[0].children[0], p1_quits)
# - Pull by P1 (children[1]) -> chamber 1 is loaded -> P1 dies
g.set_outcome(g.root.children[0].children[1], p1_dies)

# Loaded = 2 (root.children[1])
# - Quit by P1
g.set_outcome(g.root.children[1].children[0], p1_quits)
# - At P2 node:
#   - Quit by P2 -> P2 quits
g.set_outcome(g.root.children[1].children[1].children[0], p2_quits)
#   - Pull by P2 -> second pull is loaded -> P2 dies
g.set_outcome(g.root.children[1].children[1].children[1], p2_dies)

# Loaded = 3 (root.children[2])
g.set_outcome(g.root.children[2].children[0], p1_quits)
# At P2 node after first pull
g.set_outcome(g.root.children[2].children[1].children[0], p2_quits)
# At P1 node after two safe pulls:
g.set_outcome(g.root.children[2].children[1].children[1].children[0], p1_quits)
# P1 pulls on third pull -> loaded -> P1 dies
g.set_outcome(g.root.children[2].children[1].children[1].children[1], p1_dies)

# Loaded = 4 (root.children[3])
g.set_outcome(g.root.children[3].children[0], p1_quits)
# P2 after one safe pull
g.set_outcome(g.root.children[3].children[1].children[0], p2_quits)
# P1 after two safe pulls
g.set_outcome(g.root.children[3].children[1].children[1].children[0], p1_quits)
# P2 after three safe pulls
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[0], p2_quits)
# P2 pulls on fourth pull -> loaded -> P2 dies
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[1], p2_dies)

# Loaded = 5 (root.children[4])
g.set_outcome(g.root.children[4].children[0], p1_quits)
# P2 after one safe pull
g.set_outcome(g.root.children[4].children[1].children[0], p2_quits)
# P1 after two safe pulls
g.set_outcome(g.root.children[4].children[1].children[1].children[0], p1_quits)
# P2 after three safe pulls
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[0], p2_quits)
# P1 after four safe pulls
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[0], p1_quits)
# P1 pulls on fifth pull -> loaded -> P1 dies
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[1], p1_dies)

# Loaded = 6 (root.children[5])
g.set_outcome(g.root.children[5].children[0], p1_quits)
# P2 after one safe pull
g.set_outcome(g.root.children[5].children[1].children[0], p2_quits)
# P1 after two safe pulls
g.set_outcome(g.root.children[5].children[1].children[1].children[0], p1_quits)
# P2 after three safe pulls
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[0], p2_quits)
# P1 after four safe pulls
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[0], p1_quits)
# P2 after five safe pulls
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[0], p2_quits)
# P2 pulls on sixth pull -> loaded -> P2 dies
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[1], p2_dies)

# ---------- Set information sets (group nodes by player and turn) ----------
# Player 1, turn 1: all six root children (loaded = 1..6)
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Player 2, turn 2: after exactly one safe pull (loaded in {2,3,4,5,6})
g.set_infoset(g.root.children[1].children[1], g.root.children[2].children[1].infoset)
g.set_infoset(g.root.children[3].children[1], g.root.children[2].children[1].infoset)
g.set_infoset(g.root.children[4].children[1], g.root.children[2].children[1].infoset)
g.set_infoset(g.root.children[5].children[1], g.root.children[2].children[1].infoset)

# Player 1, turn 3: after two safe pulls (loaded in {3,4,5,6})
g.set_infoset(g.root.children[2].children[1].children[1], g.root.children[3].children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1].children[1], g.root.children[3].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1], g.root.children[3].children[1].children[1].infoset)

# Player 2, turn 4: after three safe pulls (loaded in {4,5,6})
g.set_infoset(g.root.children[3].children[1].children[1].children[1], g.root.children[4].children[1].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1].children[1], g.root.children[4].children[1].children[1].children[1].infoset)

# Player 1, turn 5: after four safe pulls (loaded in {5,6})
g.set_infoset(g.root.children[4].children[1].children[1].children[1].children[1], g.root.children[5].children[1].children[1].children[1].children[1].infoset)

# Note: Player 2's turn 6 (after five safe pulls) is a singleton (loaded=6), no infoset grouping needed.

# ---------- Save the EFG ----------
g.to_efg("sequential_russian_roulette.efg")