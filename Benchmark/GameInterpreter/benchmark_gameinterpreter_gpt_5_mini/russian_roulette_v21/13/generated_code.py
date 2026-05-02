import pygambit as gbt

# Six-chamber alternating Russian roulette.
# Players alternate pulling a six-chamber revolver or quitting.
# The loaded chamber is chosen by chance at the root (1..6).
# If a player quits, he gets 0 and the other player gets 1.
# If a player pulls and the current chamber is the loaded one, he dies:
#   the shooter gets -1 and the other gets 1.
# Otherwise play continues to the other player on the next chamber.
#
# Reasoning (step-by-step) is written as comments alongside the construction.
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# 1) Chance at the root picks which chamber (1..6) is the loaded one.
#    Root will have six children corresponding to loaded chamber = 1..6.
g.append_move(g.root, g.players.chance, ["Load1", "Load2", "Load3", "Load4", "Load5", "Load6"])
# Set equal probability 1/6 to each loaded-chamber outcome.
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                                    gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# 2) Player 1 acts first at chamber 1 on every branch (these nodes will be grouped into one infoset).
#    For each possible loaded chamber (root.children[0]..root.children[5]) append P1's move.
g.append_move(g.root.children[0], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[2], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5], "Player 1", ["Quit", "Pull"])

# 3) For branches where P1 pulled and survived (i.e., loaded != 1), Player 2 faces chamber 2.
#    Those are the pull-branches of root.children[1..5] (their .children[1]).
#    Append P2 moves at those nodes.
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[2].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1], "Player 2", ["Quit", "Pull"])

# 4) If P2 pulls and survives (loaded > 2), Player 1 faces chamber 3.
#    These are the pull-branches of the above P2 nodes: .children[1] for root.children[2..5].
#    Append P1 moves there.
g.append_move(g.root.children[2].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1], "Player 1", ["Quit", "Pull"])

# 5) If that P1 pulls and survives (loaded > 3), Player 2 faces chamber 4.
#    These are the pull-branches of the above P1 nodes: .children[1] for root.children[3..5].
#    Append P2 moves there.
g.append_move(g.root.children[3].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# 6) If that P2 pulls and survives (loaded > 4), Player 1 faces chamber 5.
#    These are the pull-branches of the above P2 nodes: .children[1] for root.children[4..5].
#    Append P1 moves there.
g.append_move(g.root.children[4].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])

# 7) If that P1 pulls and survives (loaded > 5), Player 2 faces chamber 6 (final).
#    This is the pull-branch of the previous node for root.children[5].
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# 8) Now set up the imperfect information (infosets).
#    All P1 decision nodes for chamber 1 are indistinguishable to P1: group root.children[1..5] into root.children[0].infoset.
g.set_infoset(g.root.children[1], g.root.children[0].infoset)
g.set_infoset(g.root.children[2], g.root.children[0].infoset)
g.set_infoset(g.root.children[3], g.root.children[0].infoset)
g.set_infoset(g.root.children[4], g.root.children[0].infoset)
g.set_infoset(g.root.children[5], g.root.children[0].infoset)

#    All P2 decision nodes at chamber 2 (the nodes root.children[1].children[1] ... root.children[5].children[1])
#    are indistinguishable to P2; use root.children[1].children[1] as representative.
g.set_infoset(g.root.children[2].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[3].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1], g.root.children[1].children[1].infoset)

#    All P1 decision nodes at chamber 3 (root.children[2].children[1].children[1] ... root.children[5]...) are indistinguishable;
#    use root.children[2].children[1].children[1] as representative.
g.set_infoset(g.root.children[3].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1], g.root.children[2].children[1].children[1].infoset)

#    P2 at chamber 4 (root.children[3] representative) grouping for root.children[4..5].
g.set_infoset(g.root.children[4].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)

#    P1 at chamber 5: group the two remaining nodes (for initial loads 5 and 6).
g.set_infoset(g.root.children[5].children[1].children[1].children[1].children[1], g.root.children[4].children[1].children[1].children[1].children[1].infoset)

# 9) Define commonly occurring outcomes and assign them to terminal nodes.
#    Outcome conventions: [Player1 payoff, Player2 payoff]
p1_quit = g.add_outcome([0, 1], label="P1 quits -> P2 wins")
p2_quit = g.add_outcome([1, 0], label="P2 quits -> P1 wins")
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_dies = g.add_outcome([1, -1], label="P2 dies")

# 9a) P1's Quit at chamber 1 on any loaded-chamber branch: root.children[i].children[0] for i=0..5
g.set_outcome(g.root.children[0].children[0], p1_quit)
g.set_outcome(g.root.children[1].children[0], p1_quit)
g.set_outcome(g.root.children[2].children[0], p1_quit)
g.set_outcome(g.root.children[3].children[0], p1_quit)
g.set_outcome(g.root.children[4].children[0], p1_quit)
g.set_outcome(g.root.children[5].children[0], p1_quit)

# 9b) P1 pulls at chamber 1:
#     - If loaded == 1 (root.children[0]), P1 dies immediately on the Pull branch.
g.set_outcome(g.root.children[0].children[1], p1_dies)
#     - If loaded != 1 (root.children[1..5]), the Pull branch continues to P2 at chamber 2 (we appended those moves).

# 9c) P2's Quit at chamber 2: for nodes root.children[1..5].children[1].children[0]
g.set_outcome(g.root.children[1].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[2].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[3].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[4].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[5].children[1].children[0], p2_quit)

# 9d) P2 pulls at chamber 2:
#     - If loaded == 2 (root.children[1]) then P2 dies immediately on that Pull branch.
g.set_outcome(g.root.children[1].children[1].children[1], p2_dies)
#     - For root.children[2..5], the Pull branch continues to P1 at chamber 3.

# 9e) P1's Quit at chamber 3: root.children[2..5].children[1].children[1].children[0]
g.set_outcome(g.root.children[2].children[1].children[1].children[0], p1_quit)
g.set_outcome(g.root.children[3].children[1].children[1].children[0], p1_quit)
g.set_outcome(g.root.children[4].children[1].children[1].children[0], p1_quit)
g.set_outcome(g.root.children[5].children[1].children[1].children[0], p1_quit)

# 9f) P1 pulls at chamber 3:
#     - If loaded == 3 (root.children[2]) then P1 dies immediately on that Pull branch.
g.set_outcome(g.root.children[2].children[1].children[1].children[1], p1_dies)
#     - For root.children[3..5], the Pull branch continues to P2 at chamber 4.

# 9g) P2's Quit at chamber 4: root.children[3..5].children[1].children[1].children[1].children[0]
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[0], p2_quit)

# 9h) P2 pulls at chamber 4:
#     - If loaded == 4 (root.children[3]) then P2 dies on that Pull branch.
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[1], p2_dies)
#     - For root.children[4..5], the Pull branch continues to P1 at chamber 5.

# 9i) P1's Quit at chamber 5: root.children[4..5].children[1].children[1].children[1].children[1].children[0]
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[0], p1_quit)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[0], p1_quit)

# 9j) P1 pulls at chamber 5:
#     - If loaded == 5 (root.children[4]) then P1 dies on that Pull branch.
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[1], p1_dies)
#     - If loaded == 6 (root.children[5]) then P1's Pull leads to the final P2 decision at chamber 6 (we appended that node).

# 9k) Final P2 (chamber 6) outcomes for the only surviving initial load (6):
#     - Quit: P2 quits -> [1,0]
#     - Pull: P2 pulls and dies -> [1,-1]
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[1], p2_dies)

# 10) Save the EFG to a file.
g.to_efg("six_chamber_russian_roulette.efg")