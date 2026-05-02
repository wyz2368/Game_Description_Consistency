# Alternating revolver game (explicit tree construction without loops)
# We follow the user's instructions and the provided imperfect-information coding.
# Step-by-step reasoning is embedded in the comments below.

import pygambit as gbt

# Create the game with two players: Player 1 moves on odd chambers, Player 2 on even.
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating six-chamber revolver")

# 1) Chance at root chooses the loaded chamber (1..6).
#    We label the chance actions "Loaded 1" .. "Loaded 6".
g.append_move(g.root, g.players.chance, ["Loaded 1", "Loaded 2", "Loaded 3", "Loaded 4", "Loaded 5", "Loaded 6"])
# Set equal probabilities 1/6 for each loaded chamber.
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Important convention for action order:
# We use actions ["Quit", "Pull"] at each decision node so that
# children[0] = Quit (immediate terminal) and children[1] = Pull (may lead to next decision or death).

# 2) At the start (chamber 1) Player 1 moves at each chance child.
#    We append a move for Player 1 on every loaded-chamber child (root.children[0] .. root.children[5]).
g.append_move(g.root.children[0], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[2], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5], "Player 1", ["Quit", "Pull"])

# Create commonly used outcome objects to reuse where appropriate.
# Outcome conventions:
# - If a player quits, the quitter gets 0 and the other player gets 1.
# - If a player pulls and the loaded chamber fires, the shooter gets -1 and the other gets 1.
p1_quits = g.add_outcome([0, 1], label="P1 quits (other wins)")
p2_quits = g.add_outcome([1, 0], label="P2 quits (other wins)")
p1_shot = g.add_outcome([-1, 1], label="P1 shot (dies)")
p2_shot = g.add_outcome([1, -1], label="P2 shot (dies)")

# Now expand each loaded-chamber branch explicitly (no loops).

# -------------------------
# Loaded = 1 branch (root.children[0])
# At chamber 1, Player 1 moves. If he quits -> terminal. If he pulls -> the loaded chamber is 1 -> he dies -> terminal.
# Note: children[0] = Quit, children[1] = Pull
g.set_outcome(g.root.children[0].children[0], p1_quits)         # P1 quits at chamber 1
g.set_outcome(g.root.children[0].children[1], p1_shot)          # P1 pulls and is shot immediately (loaded=1)

# -------------------------
# Loaded = 2 branch (root.children[1])
# Chamber 1: Player 1's choices. If Quit -> terminal. If Pull -> survive (since loaded=2) and it becomes Player 2's turn at chamber 2.
g.set_outcome(g.root.children[1].children[0], p1_quits)         # P1 quits at chamber 1 (loaded=2)
# Pull branch: append Player 2's decision at chamber 2.
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
# Player 2's Quit -> terminal; Pull -> the chamber is loaded=2 so Player 2 dies.
g.set_outcome(g.root.children[1].children[1].children[0], p2_quits)   # P2 quits at chamber 2
g.set_outcome(g.root.children[1].children[1].children[1], p2_shot)    # P2 pulls and is shot (loaded=2)

# -------------------------
# Loaded = 3 branch (root.children[2])
# Chamber 1: P1. If Quit -> terminal. If Pull -> go to P2 at chamber 2 (not loaded).
g.set_outcome(g.root.children[2].children[0], p1_quits)         # P1 quits at chamber 1 (loaded=3)
g.append_move(g.root.children[2].children[1], "Player 2", ["Quit", "Pull"])
# At chamber 2: P2 Quit -> terminal; P2 Pull -> survive (loaded=3) -> go to P1 at chamber 3.
g.set_outcome(g.root.children[2].children[1].children[0], p2_quits)   # P2 quits at chamber 2
g.append_move(g.root.children[2].children[1].children[1], "Player 1", ["Quit", "Pull"])
# At chamber 3: P1 Quit -> terminal; P1 Pull -> loaded=3 so P1 dies.
g.set_outcome(g.root.children[2].children[1].children[1].children[0], p1_quits)  # P1 quits at chamber 3
g.set_outcome(g.root.children[2].children[1].children[1].children[1], p1_shot)   # P1 pulls and is shot (loaded=3)

# -------------------------
# Loaded = 4 branch (root.children[3])
# Sequence: P1@1 -> P2@2 -> P1@3 -> P2@4 (death if pull).
g.set_outcome(g.root.children[3].children[0], p1_quits)         # P1 quits at chamber 1 (loaded=4)
g.append_move(g.root.children[3].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[3].children[1].children[0], p2_quits)   # P2 quits at chamber 2
g.append_move(g.root.children[3].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[3].children[1].children[1].children[0], p1_quits)  # P1 quits at chamber 3
g.append_move(g.root.children[3].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
# At chamber 4: P2 quits -> terminal; P2 pulls -> shot (loaded=4)
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[0], p2_quits)  # P2 quits at chamber 4
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[1], p2_shot)   # P2 pulls and is shot (loaded=4)

# -------------------------
# Loaded = 5 branch (root.children[4])
# Sequence: P1@1 -> P2@2 -> P1@3 -> P2@4 -> P1@5 (death if pull).
g.set_outcome(g.root.children[4].children[0], p1_quits)         # P1 quits at chamber 1 (loaded=5)
g.append_move(g.root.children[4].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[0], p2_quits)   # P2 quits at chamber 2
g.append_move(g.root.children[4].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[1].children[0], p1_quits)  # P1 quits at chamber 3
g.append_move(g.root.children[4].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[0], p2_quits)  # P2 quits at chamber 4
g.append_move(g.root.children[4].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
# At chamber 5: P1 quits -> terminal; P1 pulls -> shot (loaded=5)
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[0], p1_quits)  # P1 quits at chamber 5
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[1], p1_shot)   # P1 pulls and is shot (loaded=5)

# -------------------------
# Loaded = 6 branch (root.children[5])
# Sequence: P1@1 -> P2@2 -> P1@3 -> P2@4 -> P1@5 -> P2@6 (death if pull).
g.set_outcome(g.root.children[5].children[0], p1_quits)         # P1 quits at chamber 1 (loaded=6)
g.append_move(g.root.children[5].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[0], p2_quits)   # P2 quits at chamber 2
g.append_move(g.root.children[5].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[0], p1_quits)  # P1 quits at chamber 3
g.append_move(g.root.children[5].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[0], p2_quits)  # P2 quits at chamber 4
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[0], p1_quits)  # P1 quits at chamber 5
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
# At chamber 6: P2 quits -> terminal; P2 pulls -> shot (loaded=6)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[0], p2_quits)  # P2 quits at chamber 6
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[1], p2_shot)   # P2 pulls and is shot (loaded=6)

# -------------------------
# Now set the imperfect-information (infoset) groupings as specified.
# Group all Player 1's initial decision nodes (for loaded = 1..6) into one infoset.
g.set_infoset(g.root.children[1], g.root.children[0].infoset)
g.set_infoset(g.root.children[2], g.root.children[0].infoset)
g.set_infoset(g.root.children[3], g.root.children[0].infoset)
g.set_infoset(g.root.children[4], g.root.children[0].infoset)
g.set_infoset(g.root.children[5], g.root.children[0].infoset)

# After one click (one non-fatal pull), it is Player 2's turn at chamber 2.
# For all initial loaded positions 2..6 these Player 2 nodes are indistinguishable -> one infoset.
# These nodes are at: root.children[1].children[1], root.children[2].children[1], ..., root.children[5].children[1]
g.set_infoset(g.root.children[2].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[3].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1], g.root.children[1].children[1].infoset)

# After two clicks, it is Player 1's turn at chamber 3.
# For initial loaded positions 3..6 these Player 1 nodes are indistinguishable -> one infoset.
# Those nodes are root.children[2].children[1].children[1], root.children[3].children[1].children[1], ...
g.set_infoset(g.root.children[3].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1], g.root.children[2].children[1].children[1].infoset)

# After three clicks, it is Player 2's turn at chamber 4.
# For initial loaded positions 4..6 these Player 2 nodes are indistinguishable -> one infoset.
g.set_infoset(g.root.children[4].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)

# After four clicks, it is Player 1's turn at chamber 5.
# For initial loaded positions 5..6 these Player 1 nodes are indistinguishable -> one infoset.
g.set_infoset(g.root.children[5].children[1].children[1].children[1].children[1], g.root.children[4].children[1].children[1].children[1].children[1].infoset)

# Note: after five clicks only one remaining node (chamber 6) exists for the player to move,
# so no grouping is required for that stage.

# Save the EFG to a file.
g.to_efg("alternating_revolver.efg")