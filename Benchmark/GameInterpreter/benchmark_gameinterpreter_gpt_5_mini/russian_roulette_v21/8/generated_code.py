import pygambit as gbt

# Build an extensive-form game for alternating Russian Roulette with 6 chambers.
# Players: Player 1 (acts first) and Player 2.
# Nature (chance) chooses which chamber 1..6 is loaded at the start, uniformly.
# Then players alternate deciding to Quit or Pull. After each Pull the outcome
# (bang or click) is common knowledge, so the history uniquely identifies each
# decision node (no information sets across different histories are needed).
#
# We avoid loops and recursion by explicitly unrolling the tree for each possible
# loaded chamber. We also avoid using the '+' operator anywhere in the code.
#
# Payoffs:
# - If a player quits, that player gets 0 and the other player gets 1.
# - If a player pulls and the current chamber is loaded, that player gets -1
#   and the other player gets 1.
# - Play continues if the pull produces a click (i.e., the loaded chamber has
#   not yet been reached).

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating Russian Roulette (6 chambers)")

# Step 1: Nature chooses which chamber (1..6) is loaded.
g.append_move(g.root, g.players.chance,
              ["Chamber 1", "Chamber 2", "Chamber 3",
               "Chamber 4", "Chamber 5", "Chamber 6"])
# Set equal probabilities 1/6 for each chamber outcome using gbt.Rational.
g.set_chance_probs(g.root.infoset,
                   [gbt.Rational(1, 6),
                    gbt.Rational(1, 6),
                    gbt.Rational(1, 6),
                    gbt.Rational(1, 6),
                    gbt.Rational(1, 6),
                    gbt.Rational(1, 6)])

# Pre-create the outcome objects we will reuse.
p1_quits = g.add_outcome([0, 1], label="P1 quits")
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_quits = g.add_outcome([1, 0], label="P2 quits")
p2_dies = g.add_outcome([1, -1], label="P2 dies")

# For each possible loaded chamber (branches of the chance node), unroll the
# alternating sequence of decisions. The sequence of actors by pull index is:
# pull 1 -> Player 1
# pull 2 -> Player 2
# pull 3 -> Player 1
# pull 4 -> Player 2
# pull 5 -> Player 1
# pull 6 -> Player 2
#
# For each branch (loaded == k), a Pull that is on pull index k causes that
# pulling player to die (terminal). Any earlier Pull that is not the loaded
# index causes the game to continue to the next player.

# ------------- Loaded chamber = 1 -------------
# If loaded chamber is 1, the very first Pull (by Player 1) is lethal.
c1 = g.root.children[0]
# Player 1 decides first: Quit or Pull.
g.append_move(c1, "Player 1", ["Quit", "Pull"])
# Quit -> P1 gets 0, P2 gets 1.
g.set_outcome(c1.children[0], p1_quits)
# Pull -> since loaded==1, P1 dies immediately.
g.set_outcome(c1.children[1], p1_dies)

# ------------- Loaded chamber = 2 -------------
# If loaded chamber is 2, P1's first Pull is a click; the second Pull (by P2)
# would be lethal.
c2 = g.root.children[1]
g.append_move(c2, "Player 1", ["Quit", "Pull"])
g.set_outcome(c2.children[0], p1_quits)
# If P1 pulls (click), now Player 2 chooses.
g.append_move(c2.children[1], "Player 2", ["Quit", "Pull"])
# If P2 quits, P2 gets 0, P1 gets 1.
g.set_outcome(c2.children[1].children[0], p2_quits)
# If P2 pulls and loaded==2, P2 dies.
g.set_outcome(c2.children[1].children[1], p2_dies)

# ------------- Loaded chamber = 3 -------------
# Sequence: P1 (1) -> P2 (2) -> P1 (3 lethal)
c3 = g.root.children[2]
g.append_move(c3, "Player 1", ["Quit", "Pull"])
g.set_outcome(c3.children[0], p1_quits)
# After P1 Pull (click), P2 moves.
g.append_move(c3.children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(c3.children[1].children[0], p2_quits)
# After P2 Pull (click), P1 moves for the 3rd pull.
g.append_move(c3.children[1].children[1], "Player 1", ["Quit", "Pull"])
# If P1 quits at this stage, P1 gets 0 and P2 gets 1.
g.set_outcome(c3.children[1].children[1].children[0], p1_quits)
# If P1 pulls and loaded==3, P1 dies.
g.set_outcome(c3.children[1].children[1].children[1], p1_dies)

# ------------- Loaded chamber = 4 -------------
# Sequence: P1 (1) -> P2 (2) -> P1 (3) -> P2 (4 lethal)
c4 = g.root.children[3]
g.append_move(c4, "Player 1", ["Quit", "Pull"])
g.set_outcome(c4.children[0], p1_quits)
g.append_move(c4.children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(c4.children[1].children[0], p2_quits)
g.append_move(c4.children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(c4.children[1].children[1].children[0], p1_quits)
# After P1's 3rd pull (click), P2 faces the 4th pull.
g.append_move(c4.children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(c4.children[1].children[1].children[1].children[0], p2_quits)
# If P2 pulls on the 4th pull and loaded==4, P2 dies.
g.set_outcome(c4.children[1].children[1].children[1].children[1], p2_dies)

# ------------- Loaded chamber = 5 -------------
# Sequence: P1(1) -> P2(2) -> P1(3) -> P2(4) -> P1(5 lethal)
c5 = g.root.children[4]
g.append_move(c5, "Player 1", ["Quit", "Pull"])
g.set_outcome(c5.children[0], p1_quits)
g.append_move(c5.children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(c5.children[1].children[0], p2_quits)
g.append_move(c5.children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(c5.children[1].children[1].children[0], p1_quits)
g.append_move(c5.children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(c5.children[1].children[1].children[1].children[0], p2_quits)
# After P2's 4th pull (click), P1 faces the 5th pull.
g.append_move(c5.children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(c5.children[1].children[1].children[1].children[1].children[0], p1_quits)
# If P1 pulls on the 5th pull and loaded==5, P1 dies.
g.set_outcome(c5.children[1].children[1].children[1].children[1].children[1], p1_dies)

# ------------- Loaded chamber = 6 -------------
# Sequence: P1(1) -> P2(2) -> P1(3) -> P2(4) -> P1(5) -> P2(6 lethal)
c6 = g.root.children[5]
g.append_move(c6, "Player 1", ["Quit", "Pull"])
g.set_outcome(c6.children[0], p1_quits)
g.append_move(c6.children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(c6.children[1].children[0], p2_quits)
g.append_move(c6.children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(c6.children[1].children[1].children[0], p1_quits)
g.append_move(c6.children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(c6.children[1].children[1].children[1].children[0], p2_quits)
g.append_move(c6.children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(c6.children[1].children[1].children[1].children[1].children[0], p1_quits)
# After P1's 5th pull (click), P2 faces the 6th pull.
g.append_move(c6.children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(c6.children[1].children[1].children[1].children[1].children[1].children[0], p2_quits)
# If P2 pulls on the 6th pull and loaded==6, P2 dies.
g.set_outcome(c6.children[1].children[1].children[1].children[1].children[1].children[1], p2_dies)

# Save the EFG
g.to_efg("alternating_russian_roulette.efg")