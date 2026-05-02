import pygambit as gbt

# Build a 2-player extensive form game for 6-chamber Russian roulette.
# Players alternate turns with Player 1 acting first.
# Nature (chance) initially chooses the loaded chamber (1..6) with equal probability.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# 1) Nature places the single loaded chamber in one of 6 positions.
#    We create 6 chance branches for the root.
g.append_move(g.root, g.players.chance,
              ["Loaded1", "Loaded2", "Loaded3", "Loaded4", "Loaded5", "Loaded6"])

# Set equal probabilities 1/6 for each initial loaded position.
g.set_chance_probs(g.root.infoset,
                   [gbt.Rational(1, 6),
                    gbt.Rational(1, 6),
                    gbt.Rational(1, 6),
                    gbt.Rational(1, 6),
                    gbt.Rational(1, 6),
                    gbt.Rational(1, 6)])

# 2) Define common outcomes to reuse.
#    Payoffs are [Player1, Player2]
p1_die = g.add_outcome([-1, 1], label="P1 dies (other wins)")
p2_die = g.add_outcome([1, -1], label="P2 dies (other wins)")
p1_quit = g.add_outcome([0, 1], label="P1 quits (other wins)")
p2_quit = g.add_outcome([1, 0], label="P2 quits (other wins)")

# For clarity, name root children for each loaded-chamber hypothesis.
# They correspond to the 6 possible initial chance outcomes.
rc0 = g.root.children[0]  # Loaded at chamber 1
rc1 = g.root.children[1]  # Loaded at chamber 2
rc2 = g.root.children[2]  # Loaded at chamber 3
rc3 = g.root.children[3]  # Loaded at chamber 4
rc4 = g.root.children[4]  # Loaded at chamber 5
rc5 = g.root.children[5]  # Loaded at chamber 6

# ---------------------------
# Branch for loaded at chamber 1 (rc0)
# ---------------------------
# Player 1 moves first: can Quit or Pull
g.append_move(rc0, "Player 1", ["Quit", "Pull"])
# If P1 quits immediately, he gets 0 and P2 wins (1)
g.set_outcome(rc0.children[0], p1_quit)
# If P1 pulls and the loaded chamber is 1, he dies immediately
g.set_outcome(rc0.children[1], p1_die)

# ---------------------------
# Branch for loaded at chamber 2 (rc1)
# ---------------------------
g.append_move(rc1, "Player 1", ["Quit", "Pull"])
g.set_outcome(rc1.children[0], p1_quit)
# If P1 pulls and chamber 1 is empty (since load at 2), play passes to Player 2
g.append_move(rc1.children[1], "Player 2", ["Quit", "Pull"])
# If P2 quits now, P2 gets 0 and P1 gets 1
g.set_outcome(rc1.children[1].children[0], p2_quit)
# If P2 pulls and loaded chamber is 2, P2 dies
g.set_outcome(rc1.children[1].children[1], p2_die)

# ---------------------------
# Branch for loaded at chamber 3 (rc2)
# ---------------------------
g.append_move(rc2, "Player 1", ["Quit", "Pull"])
g.set_outcome(rc2.children[0], p1_quit)
g.append_move(rc2.children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(rc2.children[1].children[0], p2_quit)
# P2 pulls -> chamber 2 was empty, now chamber 3 for P1
g.append_move(rc2.children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(rc2.children[1].children[1].children[0], p1_quit)
# If P1 pulls at chamber 3 and it's loaded, P1 dies
g.set_outcome(rc2.children[1].children[1].children[1], p1_die)

# ---------------------------
# Branch for loaded at chamber 4 (rc3)
# ---------------------------
g.append_move(rc3, "Player 1", ["Quit", "Pull"])
g.set_outcome(rc3.children[0], p1_quit)
g.append_move(rc3.children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(rc3.children[1].children[0], p2_quit)
g.append_move(rc3.children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(rc3.children[1].children[1].children[0], p1_quit)
g.append_move(rc3.children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(rc3.children[1].children[1].children[1].children[0], p2_quit)
# If P2 pulls at chamber 4 and it's loaded, P2 dies
g.set_outcome(rc3.children[1].children[1].children[1].children[1], p2_die)

# ---------------------------
# Branch for loaded at chamber 5 (rc4)
# ---------------------------
g.append_move(rc4, "Player 1", ["Quit", "Pull"])
g.set_outcome(rc4.children[0], p1_quit)
g.append_move(rc4.children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(rc4.children[1].children[0], p2_quit)
g.append_move(rc4.children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(rc4.children[1].children[1].children[0], p1_quit)
g.append_move(rc4.children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(rc4.children[1].children[1].children[1].children[0], p2_quit)
g.append_move(rc4.children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(rc4.children[1].children[1].children[1].children[1].children[0], p1_quit)
# If P1 pulls at chamber 5 and it's loaded, P1 dies
g.set_outcome(rc4.children[1].children[1].children[1].children[1].children[1], p1_die)

# ---------------------------
# Branch for loaded at chamber 6 (rc5)
# ---------------------------
g.append_move(rc5, "Player 1", ["Quit", "Pull"])
g.set_outcome(rc5.children[0], p1_quit)
g.append_move(rc5.children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(rc5.children[1].children[0], p2_quit)
g.append_move(rc5.children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(rc5.children[1].children[1].children[0], p1_quit)
g.append_move(rc5.children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(rc5.children[1].children[1].children[1].children[0], p2_quit)
g.append_move(rc5.children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(rc5.children[1].children[1].children[1].children[1].children[0], p1_quit)
g.append_move(rc5.children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
# If P2 pulls at the final (6th) chamber and it's loaded, P2 dies
g.set_outcome(rc5.children[1].children[1].children[1].children[1].children[1].children[1], p2_die)

# ---------------------------
# Set information sets to represent imperfect information:
# - Player 1's initial decision nodes (he does not know which chamber is loaded).
# - Player 2's decision nodes after one observed empty click (he knows the click but not the initial loaded position).
# - And similarly for later decision nodes: after two empties Player 1, after three empties Player 2, etc.
# The following g.set_infoset calls group the corresponding nodes.
# ---------------------------

# All initial Player 1 nodes (root children) are in the same infoset.
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Player 2 nodes after one empty click: exist for loaded positions 2..6.
g.set_infoset(rc2.children[1], rc1.children[1].infoset)
g.set_infoset(rc3.children[1], rc1.children[1].infoset)
g.set_infoset(rc4.children[1], rc1.children[1].infoset)
g.set_infoset(rc5.children[1], rc1.children[1].infoset)

# Player 1 nodes after two empty clicks: exist for loaded positions 3..6.
g.set_infoset(rc3.children[1].children[1], rc2.children[1].children[1].infoset)
g.set_infoset(rc4.children[1].children[1], rc2.children[1].children[1].infoset)
g.set_infoset(rc5.children[1].children[1], rc2.children[1].children[1].infoset)

# Player 2 nodes after three empty clicks: exist for loaded positions 4..6.
g.set_infoset(rc4.children[1].children[1].children[1], rc3.children[1].children[1].children[1].infoset)
g.set_infoset(rc5.children[1].children[1].children[1], rc3.children[1].children[1].children[1].infoset)

# Player 1 nodes after four empty clicks: exist for loaded positions 5..6.
g.set_infoset(rc5.children[1].children[1].children[1].children[1], rc4.children[1].children[1].children[1].children[1].infoset)

# Player 2 node after five empty clicks: only exists for loaded position 6 (rc5).
# (No need to set additional infosets because there is only one such node.)

# --------------
# Save the game to an EFG file
# --------------
g.to_efg("six_chamber_russian_roulette.efg")