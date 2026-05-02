import pygambit as gbt

# Build an extensive-form game for the alternating russian-roulette described.
# Reasoning and assumptions (also echoed in-line below):
# - We model the unknown loaded chamber by a single chance node at the root,
#   which selects one of the six chambers with equal probability 1/6.
# - For each realized chamber (root.children[0] .. root.children[5]) the
#   subsequent play proceeds deterministically: players alternate Pull/Quit
#   until either someone pulls the loaded chamber (they die) or someone quits.
# - Each decision is labeled with actions ["Pull", "Quit"] with "Pull" = children[0]
#   and "Quit" = children[1].
# - Players observe all past pulls and survivals but never the actual loaded chamber.
#   Therefore decision nodes that correspond to the same turn number (same current
#   chamber index) are in the same information set across the different root children.
# - We create all decision nodes first (with g.append_move), then create information
#   sets (with g.set_infoset), and finally set the terminal outcomes.
# - Use gbt.Rational to set equal chance probabilities.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating russian-roulette, 6 chambers")

# 1) Chance: which chamber (1..6) is the loaded one.
g.append_move(g.root, g.players.chance, ["Chamber 1", "Chamber 2", "Chamber 3", "Chamber 4", "Chamber 5", "Chamber 6"])
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# For readability, name references to each root child (loaded chamber = k).
c1 = g.root.children[0]  # loaded chamber 1
c2 = g.root.children[1]  # loaded chamber 2
c3 = g.root.children[2]  # loaded chamber 3
c4 = g.root.children[3]  # loaded chamber 4
c5 = g.root.children[4]  # loaded chamber 5
c6 = g.root.children[5]  # loaded chamber 6

# Append Player 1's first decision node (this exists for all six chamber realizations).
g.append_move(c1, "Player 1", ["Pull", "Quit"])
g.append_move(c2, "Player 1", ["Pull", "Quit"])
g.append_move(c3, "Player 1", ["Pull", "Quit"])
g.append_move(c4, "Player 1", ["Pull", "Quit"])
g.append_move(c5, "Player 1", ["Pull", "Quit"])
g.append_move(c6, "Player 1", ["Pull", "Quit"])

# Now append subsequent moves along each branch where "Pull" leads to the next player's decision,
# taking care to create parents before children (no loops used).

# Branch for loaded chamber 1 (k=1):
# - If Player 1 pulls, chamber1 is loaded => P1 dies. (terminal)
# - If Player 1 quits => terminal
# (No further moves needed; children created by the append_move above.)

# Branch for loaded chamber 2 (k=2):
# After P1 pulls and survives, Player 2 moves (chamber 2).
g.append_move(c2.children[0], "Player 2", ["Pull", "Quit"])

# Branch for loaded chamber 3 (k=3):
# After P1 pulls (chamber1), P2 pulls (chamber2), then P1 faces chamber3.
g.append_move(c3.children[0], "Player 2", ["Pull", "Quit"])
g.append_move(c3.children[0].children[0], "Player 1", ["Pull", "Quit"])

# Branch for loaded chamber 4 (k=4):
# Sequence: P1 (ch1), P2 (ch2), P1 (ch3), then P2 (ch4)
g.append_move(c4.children[0], "Player 2", ["Pull", "Quit"])
g.append_move(c4.children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(c4.children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Branch for loaded chamber 5 (k=5):
# Sequence: P1, P2, P1, P2, then P1 at chamber5
g.append_move(c5.children[0], "Player 2", ["Pull", "Quit"])
g.append_move(c5.children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(c5.children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(c5.children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])

# Branch for loaded chamber 6 (k=6):
# Sequence: P1, P2, P1, P2, P1, then P2 at chamber6
g.append_move(c6.children[0], "Player 2", ["Pull", "Quit"])
g.append_move(c6.children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(c6.children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(c6.children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(c6.children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# All decision nodes have now been created. Next we set information sets so that
# a player cannot distinguish which root child (loaded chamber) was realized,
# only the current turn number (how many pulls/survivals have happened).

# 1) Player 1's first move (chamber 1): all c1..c6 Player1 nodes are in the same infoset.
g.set_infoset(c2, c1.infoset)
g.set_infoset(c3, c1.infoset)
g.set_infoset(c4, c1.infoset)
g.set_infoset(c5, c1.infoset)
g.set_infoset(c6, c1.infoset)

# 2) Player 2's first move (chamber 2): nodes reached after P1 pulls and survives:
#    these are c2.children[0], c3.children[0], c4.children[0], c5.children[0], c6.children[0]
g.set_infoset(c3.children[0], c2.children[0].infoset)
g.set_infoset(c4.children[0], c2.children[0].infoset)
g.set_infoset(c5.children[0], c2.children[0].infoset)
g.set_infoset(c6.children[0], c2.children[0].infoset)

# 3) Player 1's second move (chamber 3): nodes after two surviving pulls (P1 then P2):
#    these are c3.children[0].children[0], c4.children[0].children[0], c5.children[0].children[0], c6.children[0].children[0]
g.set_infoset(c4.children[0].children[0], c3.children[0].children[0].infoset)
g.set_infoset(c5.children[0].children[0], c3.children[0].children[0].infoset)
g.set_infoset(c6.children[0].children[0], c3.children[0].children[0].infoset)

# 4) Player 2's second move (chamber 4): nodes after three surviving pulls (P1,P2,P1):
#    these are c4.children[0].children[0].children[0], c5.children[0].children[0].children[0], c6.children[0].children[0].children[0]
g.set_infoset(c5.children[0].children[0].children[0], c4.children[0].children[0].children[0].infoset)
g.set_infoset(c6.children[0].children[0].children[0], c4.children[0].children[0].children[0].infoset)

# 5) Player 1's third move (chamber 5): nodes after four surviving pulls (P1,P2,P1,P2):
#    these are c5.children[0].children[0].children[0].children[0], c6.children[0].children[0].children[0].children[0]
g.set_infoset(c6.children[0].children[0].children[0].children[0], c5.children[0].children[0].children[0].children[0].infoset)

# Now add terminal outcomes and attach them to the terminal nodes.
# Outcomes:
# - P1 dies => [-1, 1]
# - P2 dies => [1, -1]
# - If a player quits, the quitter gets 0 and the other gets 1:
#   - P1 quits => [0, 1]
#   - P2 quits => [1, 0]

p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_dies = g.add_outcome([1, -1], label="P2 dies")
p1_quits = g.add_outcome([0, 1], label="P1 quits")
p2_quits = g.add_outcome([1, 0], label="P2 quits")

# Attach outcomes for k=1 (loaded chamber 1)
g.set_outcome(c1.children[0], p1_dies)   # P1 pulls and dies immediately
g.set_outcome(c1.children[1], p1_quits)  # P1 quits

# Attach outcomes for k=2
g.set_outcome(c2.children[1], p1_quits)  # P1 quits at first move
g.set_outcome(c2.children[0].children[0], p2_dies)  # P2 pulls and dies (chamber 2)
g.set_outcome(c2.children[0].children[1], p2_quits) # P2 quits

# Attach outcomes for k=3
g.set_outcome(c3.children[1], p1_quits)  # P1 quits at first move
g.set_outcome(c3.children[0].children[1], p2_quits) # P2 quits at second move
g.set_outcome(c3.children[0].children[0].children[0], p1_dies) # P1 pulls on chamber3 and dies
g.set_outcome(c3.children[0].children[0].children[1], p1_quits) # P1 quits at his second decision

# Attach outcomes for k=4
g.set_outcome(c4.children[1], p1_quits)  # P1 quits at first move
g.set_outcome(c4.children[0].children[1], p2_quits) # P2 quits at second move
g.set_outcome(c4.children[0].children[0].children[1], p1_quits) # P1 quits at third move
g.set_outcome(c4.children[0].children[0].children[0].children[0], p2_dies) # P2 pulls on chamber4 and dies
g.set_outcome(c4.children[0].children[0].children[0].children[1], p2_quits) # P2 quits at his second decision

# Attach outcomes for k=5
g.set_outcome(c5.children[1], p1_quits)  # P1 quits at first move
g.set_outcome(c5.children[0].children[1], p2_quits) # P2 quits at second move
g.set_outcome(c5.children[0].children[0].children[1], p1_quits) # P1 quits at third move
g.set_outcome(c5.children[0].children[0].children[0].children[1], p2_quits) # P2 quits at fourth move
g.set_outcome(c5.children[0].children[0].children[0].children[0].children[0], p1_dies) # P1 pulls chamber5 and dies
g.set_outcome(c5.children[0].children[0].children[0].children[0].children[1], p1_quits) # P1 quits at his third decision

# Attach outcomes for k=6
g.set_outcome(c6.children[1], p1_quits)  # P1 quits at first move
g.set_outcome(c6.children[0].children[1], p2_quits) # P2 quits at second move
g.set_outcome(c6.children[0].children[0].children[1], p1_quits) # P1 quits at third move
g.set_outcome(c6.children[0].children[0].children[0].children[1], p2_quits) # P2 quits at fourth move
g.set_outcome(c6.children[0].children[0].children[0].children[0].children[1], p1_quits) # P1 quits at fifth move
g.set_outcome(c6.children[0].children[0].children[0].children[0].children[0].children[0], p2_dies) # P2 pulls chamber6 and dies
g.set_outcome(c6.children[0].children[0].children[0].children[0].children[0].children[1], p2_quits) # P2 quits at his third decision

# Save the EFG to a file
g.to_efg("alternating_russian_roulette_6chambers.efg")