import pygambit as gbt

# Build the extensive-form game for the alternating six-chamber "revolver" game.
# Reasoning (encoded as comments inline):
# - Nature (chance) first chooses which chamber 1..6 is loaded (uniformly).
# - Players alternate pulls starting with Player 1 at chamber 1.
# - At each decision node the player chooses "Pull" or "Quit".
# - If they Quit they get 0 and the other player gets 1.
# - If they Pull and that chamber is loaded, they die: payoff -1 for shooter, +1 for the opponent.
# - If they Pull and the chamber is empty, play continues to the other player at the next chamber.
# - Information: when a player faces chamber k, they only know that the loaded chamber is >= k;
#   we group the decision nodes across chance branches accordingly (infosets set below).
# Important implementation notes:
# - No loops or recursion are used: all nodes and moves are created explicitly.
# - gbt.Rational is used for chance probabilities.
# - All infoset grouping calls are made only after the referenced moves exist.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating six-chamber revolver")

# Nature chooses loaded chamber 1..6
g.append_move(g.root, g.players.chance, ["Loaded 1", "Loaded 2", "Loaded 3", "Loaded 4", "Loaded 5", "Loaded 6"])
# Set uniform probability 1/6 for each loaded-chamber branch
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Add outcomes we will reuse:
# Shooter dies (shooter gets -1, opponent gets +1)
p1_dies = g.add_outcome([-1, 1], label="Player 1 dies")
p2_dies = g.add_outcome([1, -1], label="Player 2 dies")
# Quit outcomes: quitter gets 0, other player gets 1
p1_quits = g.add_outcome([0, 1], label="Player 1 quits")
p2_quits = g.add_outcome([1, 0], label="Player 2 quits")

# 1) Append Player 1 moves at chamber 1 for all chance branches (root.children[0..5])
g.append_move(g.root.children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[1], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[2], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5], "Player 1", ["Pull", "Quit"])

# 2) Append Player 2 moves at chamber 2 for branches where a first pull occurred (children[1..5].children[0])
g.append_move(g.root.children[1].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "Player 2", ["Pull", "Quit"])

# 3) Append Player 1 moves at chamber 3 for branches where two pulls occurred (children[2..5].children[0].children[0])
g.append_move(g.root.children[2].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "Player 1", ["Pull", "Quit"])

# 4) Append Player 2 moves at chamber 4 for branches where three pulls occurred (children[3..5].children[0].children[0].children[0])
g.append_move(g.root.children[3].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# 5) Append Player 1 moves at chamber 5 for branches where four pulls occurred (children[4..5].children[0].children[0].children[0].children[0])
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])

# 6) Append Player 2 move at chamber 6 for the single remaining branch after five empty pulls (child index 5's depth-5 node)
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Now set terminal outcomes for every "Pull -> firing" case (the loaded chamber for each branch).
# The death occurs when the Pull action reaches the loaded chamber.
# For loaded chamber 1 (root.children[0]): Player 1 pulls and dies at the Pull child.
g.set_outcome(g.root.children[0].children[0], p1_dies)
# For loaded chamber 2
g.set_outcome(g.root.children[1].children[0].children[0], p2_dies)
# For loaded chamber 3
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_dies)
# For loaded chamber 4
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_dies)
# For loaded chamber 5
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_dies)
# For loaded chamber 6
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_dies)

# Set terminal outcomes for every Quit action (quitter gets 0, other gets 1).
# Quits by Player 1 at their first decision nodes (chamber 1)
g.set_outcome(g.root.children[0].children[1], p1_quits)
g.set_outcome(g.root.children[1].children[1], p1_quits)
g.set_outcome(g.root.children[2].children[1], p1_quits)
g.set_outcome(g.root.children[3].children[1], p1_quits)
g.set_outcome(g.root.children[4].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[1], p1_quits)

# Quits by Player 2 at chamber 2 (for branches 1..5)
g.set_outcome(g.root.children[1].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[2].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[3].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[4].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[5].children[0].children[1], p2_quits)

# Quits by Player 1 at chamber 3 (branches 2..5)
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quits)

# Quits by Player 2 at chamber 4 (branches 3..5)
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quits)

# Quits by Player 1 at chamber 5 (branches 4..5)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quits)

# Quit by Player 2 at chamber 6 (branch 5)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quits)

# Now set the information sets (imperfect information) as described:
# Chamber 1 (Player 1 at chamber 1): all 6 chance children are indistinguishable before any pull.
# Make children[0], [2], [3], [4], [5] share the infoset of children[1].
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Chamber 2 (Player 2 at chamber 2): nodes are at depth one after a "pull",
# i.e., g.root.children[i].children[0] for i = 1..5. Use children[1].children[0] as base.
g.set_infoset(g.root.children[2].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[1].children[0].infoset)

# Chamber 3 (Player 1 at chamber 3): nodes are at depth two after two pulls,
# i.e., g.root.children[i].children[0].children[0] for i = 2..5.
g.set_infoset(g.root.children[3].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[2].children[0].children[0].infoset)

# Chamber 4 (Player 2 at chamber 4): nodes are at depth three after three pulls,
# i.e., g.root.children[i].children[0].children[0].children[0] for i = 3..5.
g.set_infoset(g.root.children[4].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)

# Chamber 5 (Player 1 at chamber 5): nodes are at depth four after four pulls,
# i.e., g.root.children[i].children[0].children[0].children[0].children[0] for i = 4..5.
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].children[0].infoset)

# The chamber 6 decision node (Player 2) is singleton (only occurs under loaded chamber 6)
# and thus needs no grouping.

# Save the EFG
g.to_efg("alternating_revolver.efg")