import pygambit as gbt

# Russian roulette with a 6-chamber revolver.
# Reasoning (encoded in comments as requested):
# - A single chance move at the root selects the loaded chamber L in {1..6}. Players do not observe L.
# - Players observe all past trigger pulls and their outcomes, so at any decision they know how many
#   pulls have already occurred but not L itself. Thus all decision nodes for the same player that
#   occur when the same number of pulls have already happened must be in the same information set.
# - We therefore build a separate root branch for each L (1..6). On each branch the sequence of
#   decision nodes alternates between Player 1 and Player 2 until the loaded chamber is reached.
# - We manually construct every branch to the maximum needed depth (6 pulls). We then group
#   information sets across branches according to the number of past safe pulls (as described
#   in the problem statement).
#
# Implementation notes:
# - No loops or recursion are used. Every append_move and set_outcome call is written explicitly.
# - We use gbt.Rational to set equal 1/6 probabilities at the chance node.
# - We reuse outcome objects where appropriate.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="6-chamber Russian roulette (alternating players)")

# Root chance: which chamber is loaded (L=1..6)
g.append_move(g.root, g.players.chance, ["L1", "L2", "L3", "L4", "L5", "L6"])
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6),
                                    gbt.Rational(1, 6),
                                    gbt.Rational(1, 6),
                                    gbt.Rational(1, 6),
                                    gbt.Rational(1, 6),
                                    gbt.Rational(1, 6)])

# Pre-create common outcomes to reuse
p1_quits = g.add_outcome([0, 1], label="P1 quits (other wins)")
p2_quits = g.add_outcome([1, 0], label="P2 quits (other wins)")
p1_shot = g.add_outcome([-1, 1], label="P1 shot (dies)")
p2_shot = g.add_outcome([1, -1], label="P2 shot (dies)")

# --------------------
# Branch for L = 1 (root.children[0])
# --------------------
# Player 1 initial decision at 0 pulls
g.append_move(g.root.children[0], "Player 1", ["Quit", "Pull"])
# If P1 quits immediately -> (0,1)
g.set_outcome(g.root.children[0].children[0], p1_quits)
# If P1 pulls and L=1 -> P1 is shot
g.set_outcome(g.root.children[0].children[1], p1_shot)

# --------------------
# Branch for L = 2 (root.children[1])
# --------------------
g.append_move(g.root.children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[1].children[0], p1_quits)
# If P1 pulls and safe (L>1), then Player 2 decides after 1 pull
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
# If P2 quits -> P1 wins
g.set_outcome(g.root.children[1].children[1].children[0], p2_quits)
# If P2 pulls and L=2 -> P2 is shot
g.set_outcome(g.root.children[1].children[1].children[1], p2_shot)

# --------------------
# Branch for L = 3 (root.children[2])
# --------------------
g.append_move(g.root.children[2], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[2].children[0], p1_quits)
g.append_move(g.root.children[2].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[2].children[1].children[0], p2_quits)
# After P2 pulls safely (for L>2), Player 1 decides after 2 pulls
g.append_move(g.root.children[2].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[2].children[1].children[1].children[0], p1_quits)
# If P1 pulls and L=3 -> P1 is shot
g.set_outcome(g.root.children[2].children[1].children[1].children[1], p1_shot)

# --------------------
# Branch for L = 4 (root.children[3])
# --------------------
g.append_move(g.root.children[3], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[3].children[0], p1_quits)
g.append_move(g.root.children[3].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[3].children[1].children[0], p2_quits)
g.append_move(g.root.children[3].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[3].children[1].children[1].children[0], p1_quits)
# After P1 pulls safely (when L>3), Player 2 moves after 3 pulls
g.append_move(g.root.children[3].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[0], p2_quits)
# If P2 pulls and L=4 -> P2 is shot
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[1], p2_shot)

# --------------------
# Branch for L = 5 (root.children[4])
# --------------------
g.append_move(g.root.children[4], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[0], p1_quits)
g.append_move(g.root.children[4].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[0], p2_quits)
g.append_move(g.root.children[4].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[1].children[0], p1_quits)
g.append_move(g.root.children[4].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[0], p2_quits)
# After P2 pulls safely when L>4, Player 1 moves after 4 pulls
g.append_move(g.root.children[4].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[0], p1_quits)
# If P1 pulls and L=5 -> P1 is shot
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[1], p1_shot)

# --------------------
# Branch for L = 6 (root.children[5])
# --------------------
g.append_move(g.root.children[5], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[0], p1_quits)
g.append_move(g.root.children[5].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[0], p2_quits)
g.append_move(g.root.children[5].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[0], p1_quits)
g.append_move(g.root.children[5].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[0], p2_quits)
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[0], p1_quits)
# If P1 pulls safely when L>5, it passes to Player 2 at the 6th pull; since L=6 here, P2 pulling dies.
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[0], p2_quits)
# If P2 pulls (the 6th pull) and L=6 -> P2 is shot
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[1], p2_shot)

# --------------------
# Set information sets (group nodes by number of past safe pulls)
# The following set_infoset calls follow the grouping described in the prompt.
# Make sure append_move has already been executed for every referenced node (done above).
# --------------------

# Group 1: Player 1's initial decision (0 pulls so far) -- g.root.children[0..5]
g.set_infoset(g.root.children[1], g.root.children[0].infoset)
g.set_infoset(g.root.children[2], g.root.children[0].infoset)
g.set_infoset(g.root.children[3], g.root.children[0].infoset)
g.set_infoset(g.root.children[4], g.root.children[0].infoset)
g.set_infoset(g.root.children[5], g.root.children[0].infoset)

# Group 2: Player 2's decision after exactly 1 safe pull (1 pull so far).
# Nodes are at g.root.children[L-1].children[1] for L=2..6; use L=2 (index 1) as representative.
g.set_infoset(g.root.children[2].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[3].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1], g.root.children[1].children[1].infoset)

# Group 3: Player 1's decision after exactly 2 safe pulls (2 pulls so far).
# Nodes are at g.root.children[L-1].children[1].children[1] for L=3..6; use L=3 (index 2) as representative.
g.set_infoset(g.root.children[3].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1], g.root.children[2].children[1].children[1].infoset)

# Group 4: Player 2's decision after exactly 3 safe pulls (3 pulls so far).
# Nodes are at g.root.children[L-1].children[1].children[1].children[1] for L=4..6; use L=4 (index 3) as representative.
g.set_infoset(g.root.children[4].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)

# Group 5: Player 1's decision after exactly 4 safe pulls (4 pulls so far).
# Nodes are at g.root.children[L-1].children[1].children[1].children[1].children[1] for L=5..6; use L=5 (index 4) as representative.
g.set_infoset(g.root.children[5].children[1].children[1].children[1].children[1], g.root.children[4].children[1].children[1].children[1].children[1].infoset)

# Save the EFG
g.to_efg("russian_roulette_6chamber.efg")