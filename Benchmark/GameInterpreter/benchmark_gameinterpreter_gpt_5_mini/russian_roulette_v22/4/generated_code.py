import pygambit as gbt

# Build a 6-chamber Russian roulette extensive-form game.
# Two players alternate turns, Player 1 moves first.
# The root chance node chooses the bullet position among 6 chambers uniformly.
# At each decision node a player chooses "Quit" or "Pull".
# Action ordering is chosen as ["Quit", "Pull"] so that children[0] is the Quit branch
# and children[1] is the Pull branch. This ordering matches the infoset indexing used below.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="6-chamber Russian roulette")

# Thought: initial chance at the root determines which chamber contains the bullet.
# There are 6 equally likely positions (0..5).
g.append_move(g.root, g.players.chance, ["Pos0", "Pos1", "Pos2", "Pos3", "Pos4", "Pos5"])
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                                     gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Prepare outcome objects for the four possible terminal payoff types:
# - Player 1 quits: P1 = 0, P2 = 1
# - Player 2 quits: P1 = 1, P2 = 0
# - Player 1 shot (pulls and bullet fires): P1 = -1, P2 = 1
# - Player 2 shot (pulls and bullet fires): P1 = 1, P2 = -1
p1_quit = g.add_outcome([0, 1], label="P1 quits")
p2_quit = g.add_outcome([1, 0], label="P2 quits")
p1_shot = g.add_outcome([-1, 1], label="P1 shot")
p2_shot = g.add_outcome([1, -1], label="P2 shot")

# ---------- Append first decision (Player 1) for each possible initial bullet position ----------
# For each chance child (each bullet position), Player 1 moves first.
g.append_move(g.root.children[0], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[2], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5], "Player 1", ["Quit", "Pull"])

# ---------- Append deeper moves along each possible initial position ----------
# We explicitly build the path of alternating decisions for each initial position.
# Action indexing: children[0] = Quit (terminal), children[1] = Pull (either terminal if bullet is in current chamber, or continues)

# Position 0: bullet is in the first chamber -> P1 pulling immediately causes death.
# Set outcomes for Quit and Pull at depth 0.
g.set_outcome(g.root.children[0].children[0], p1_quit)   # P1 quits
g.set_outcome(g.root.children[0].children[1], p1_shot)   # P1 pulls and is shot (bullet at pos0)

# Position 1: first pull safe, second pull (by Player 2) is fatal.
g.set_outcome(g.root.children[1].children[0], p1_quit)   # P1 quits at first move
# P1 Pull at pos1 is safe -> Player 2 decision node
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[1].children[1].children[0], p2_quit)  # P2 quits
g.set_outcome(g.root.children[1].children[1].children[1], p2_shot)  # P2 pulls and is shot (bullet at pos1)

# Position 2: safe on first two pulls, fatal on third (Player 1 pulls at depth 2)
g.set_outcome(g.root.children[2].children[0], p1_quit)   # P1 quits at first move
g.append_move(g.root.children[2].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[2].children[1].children[0], p2_quit)  # P2 quits at depth1
# P2 Pull at pos2 is safe -> Player 1 decision node at depth2
g.append_move(g.root.children[2].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[2].children[1].children[1].children[0], p1_quit)  # P1 quits at depth2
g.set_outcome(g.root.children[2].children[1].children[1].children[1], p1_shot)  # P1 pulls and is shot (bullet at pos2)

# Position 3: fatal on the 4th pull (Player 2 at depth3)
g.set_outcome(g.root.children[3].children[0], p1_quit)   # P1 quits at first move
g.append_move(g.root.children[3].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[3].children[1].children[0], p2_quit)  # P2 quits at depth1
g.append_move(g.root.children[3].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[3].children[1].children[1].children[0], p1_quit)  # P1 quits at depth2
g.append_move(g.root.children[3].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[0], p2_quit)  # P2 quits at depth3
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[1], p2_shot)  # P2 pulls and is shot (pos3)

# Position 4: fatal on the 5th pull (Player 1 at depth4)
g.set_outcome(g.root.children[4].children[0], p1_quit)   # P1 quits at first move
g.append_move(g.root.children[4].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[0], p2_quit)  # P2 quits at depth1
g.append_move(g.root.children[4].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[1].children[0], p1_quit)  # P1 quits at depth2
g.append_move(g.root.children[4].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[0], p2_quit)  # P2 quits at depth3
g.append_move(g.root.children[4].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[0], p1_quit)  # P1 quits at depth4
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[1], p1_shot)  # P1 pulls and is shot (pos4)

# Position 5: fatal on the 6th pull (Player 2 at depth5)
g.set_outcome(g.root.children[5].children[0], p1_quit)   # P1 quits at first move
g.append_move(g.root.children[5].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[0], p2_quit)  # P2 quits at depth1
g.append_move(g.root.children[5].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[0], p1_quit)  # P1 quits at depth2
g.append_move(g.root.children[5].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[0], p2_quit)  # P2 quits at depth3
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[0], p1_quit)  # P1 quits at depth4
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[0], p2_quit)  # P2 quits at depth5
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[1], p2_shot)  # P2 pulls and is shot (pos5)

# ---------- Set up imperfect information (infosets) ----------
# The players cannot tell which initial bullet position was selected, but they do know how many safe pulls have occurred.
# Group Player 1's initial decision nodes across all six chance outcomes.
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# After one safe pull, Player 2's decision nodes (for positions 1..5) are in one infoset.
g.set_infoset(g.root.children[2].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[3].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1], g.root.children[1].children[1].infoset)

# After two safe pulls, Player 1's decision nodes (for positions 2..5) are in one infoset.
g.set_infoset(g.root.children[3].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1], g.root.children[2].children[1].children[1].infoset)

# After three safe pulls, Player 2's decision nodes (for positions 3..5) are in one infoset.
g.set_infoset(g.root.children[4].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)

# After four safe pulls, Player 1's decision nodes (for positions 4..5) are in one infoset.
g.set_infoset(g.root.children[5].children[1].children[1].children[1].children[1], g.root.children[4].children[1].children[1].children[1].children[1].infoset)

# ---------- Save the EFG ----------
g.to_efg("russian_roulette_6.efg")