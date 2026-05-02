import pygambit as gbt

# Six-chamber Russian roulette with imperfect information about which chamber is loaded.
# Reasoning (encoded as comments alongside the construction):
# - Chance selects loaded chamber L in {1..6} with probability 1/6 each.
# - Players alternate pulls starting with Player 1 at chamber 1, Player 2 at chamber 2, ...
# - On a player's turn they choose Pull or Quit.
#   * Quit: quitting player gets 0, other player gets 1 (other wins).
#   * Pull: if current chamber equals L, shooter dies (shooter gets -1, other gets +1);
#           otherwise play passes to the other player for the next chamber.
# - Players observe the current chamber index (the turn) but NOT L. Thus for each chamber
#   all nodes (across different L) that correspond to the same player are in the same infoset.
# The tree is built explicitly (no loops, no recursion) and infosets are assigned after
# the relevant moves have been appended, as required.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian Roulette")

# 1) Chance selects the loaded chamber L in {1..6}.
g.append_move(g.root, g.players.chance, ["L1", "L2", "L3", "L4", "L5", "L6"])
# Set equal probabilities 1/6 for each chamber using gbt.Rational.
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Pre-create outcome objects for reuse.
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_dies = g.add_outcome([1, -1], label="P2 dies")
p1_quit = g.add_outcome([0, 1], label="P1 quits")
p2_quit = g.add_outcome([1, 0], label="P2 quits")

# 2) Append Player 1's first-turn moves (chamber 1) under each chance child.
g.append_move(g.root.children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[1], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[2], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5], "Player 1", ["Pull", "Quit"])

# Group Player 1's first-turn nodes (chamber 1) into a single infoset: use child 0 as reference.
g.set_infoset(g.root.children[1], g.root.children[0].infoset)
g.set_infoset(g.root.children[2], g.root.children[0].infoset)
g.set_infoset(g.root.children[3], g.root.children[0].infoset)
g.set_infoset(g.root.children[4], g.root.children[0].infoset)
g.set_infoset(g.root.children[5], g.root.children[0].infoset)

# 3) Handle consequences after Player 1's first action on each chance branch:
# For L=1 (chance child 0): Pull kills Player 1 immediately; Quit yields P1 quits.
g.set_outcome(g.root.children[0].children[0], p1_dies)
g.set_outcome(g.root.children[0].children[1], p1_quit)

# For L>=2 (chance children 1..5): if P1 pulls, game continues to Player 2 at chamber 2.
g.append_move(g.root.children[1].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "Player 2", ["Pull", "Quit"])

# Also set the immediate Quit outcomes for Player 1's first-turn Quit action on each branch.
g.set_outcome(g.root.children[1].children[1], p1_quit)
g.set_outcome(g.root.children[2].children[1], p1_quit)
g.set_outcome(g.root.children[3].children[1], p1_quit)
g.set_outcome(g.root.children[4].children[1], p1_quit)
g.set_outcome(g.root.children[5].children[1], p1_quit)

# Group Player 2's first-turn nodes (chamber 2) across relevant chance branches (L>=2).
# Use the node under chance child 1 as the infoset reference.
g.set_infoset(g.root.children[2].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[1].children[0].infoset)

# 4) Handle Player 2's first-turn actions on each chance branch:
# For L=2 (chance child 1): Pull kills Player 2; Quit yields Player 2 quits.
g.set_outcome(g.root.children[1].children[0].children[0], p2_dies)
g.set_outcome(g.root.children[1].children[0].children[1], p2_quit)

# For L>=3 (chance children 2..5): if P2 pulls at chamber 2, play continues to Player 1 at chamber 3.
g.append_move(g.root.children[2].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "Player 1", ["Pull", "Quit"])

# Set Quit outcomes for Player 2 at their first-turn Quit action on these branches.
g.set_outcome(g.root.children[2].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[3].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[4].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[5].children[0].children[1], p2_quit)

# Group Player 1's second-turn nodes (chamber 3): use the node under chance child 2 as reference.
g.set_infoset(g.root.children[3].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[2].children[0].children[0].infoset)

# 5) Handle Player 1's second-turn (chamber 3) actions:
# For L=3 (chance child 2): Pull kills Player 1; Quit yields Player 1 quits.
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_dies)
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quit)

# For L>=4 (chance children 3..5): if P1 pulls at chamber 3, play continues to Player 2 at chamber 4.
g.append_move(g.root.children[3].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Set Quit outcomes for Player 1 at their second-turn Quit action on these branches.
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quit)

# Group Player 2's second-turn nodes (chamber 4): use node under chance child 3 as reference.
g.set_infoset(g.root.children[4].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)

# 6) Handle Player 2's second-turn (chamber 4) actions:
# For L=4 (chance child 3): Pull kills Player 2; Quit yields Player 2 quits.
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_dies)
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quit)

# For L>=5 (chance children 4..5): if P2 pulls at chamber 4, play continues to Player 1 at chamber 5.
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])

# Set Quit outcomes for Player 2 at their second-turn Quit action on these branches.
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quit)

# Group Player 1's third-turn nodes (chamber 5): use node under chance child 4 as reference.
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].children[0].infoset)

# 7) Handle Player 1's third-turn (chamber 5) actions:
# For L=5 (chance child 4): Pull kills Player 1; Quit yields Player 1 quits.
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_dies)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quit)

# For L=6 (chance child 5): if P1 pulls at chamber 5, play continues to Player 2 at chamber 6.
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Set Quit outcome for Player 1 at their third-turn Quit action on chance child 5.
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quit)

# 8) Handle Player 2's third-turn (chamber 6) actions for chance child 5 only:
# For L=6 (chance child 5): Pull kills Player 2; Quit yields Player 2 quits.
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_dies)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quit)

# Save the EFG to a file.
g.to_efg("six_chamber_russian_roulette.efg")