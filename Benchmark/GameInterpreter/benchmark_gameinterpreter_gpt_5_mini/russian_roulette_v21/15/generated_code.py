import pygambit as gbt

# Create the game with two players (chance node will be added at the root below).
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Sequential Russian Roulette (6 chambers)")

# Reasoning:
# - At the start, chance selects which chamber (1..6) is the loaded one.
# - Players alternate pulls. On a decision a player can Pull (first action) or Quit (second).
# - We order actions as ["Pull", "Quit"] so that continuation (if the pull is empty)
#   is always the child at index 0 (children[0]) and the Quit terminal is children[1].
# - This ordering makes the subsequent infoset grouping references consistent with the
#   mapping provided in the problem statement.

# Append the chance move (which chamber is loaded).
g.append_move(g.root, g.players.chance, ["Chamber 1", "Chamber 2", "Chamber 3", "Chamber 4", "Chamber 5", "Chamber 6"])
# Set equal probabilities 1/6 for each chamber using gbt.Rational
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# ---- Build the tree for each possible loaded chamber (no loops; explicit branches) ----

# Chamber 1 (root.children[0]):
# Player 1 moves first: Pull (children[0]) would fire (loaded=1) -> Player 1 dies.
# Quit (children[1]) -> Player 1 withdraws -> payoff [0,1].
g.append_move(g.root.children[0], "Player 1", ["Pull", "Quit"])
p1_self_shot = g.add_outcome([-1, 1], label="P1 shot (chamber1)")
p1_quit = g.add_outcome([0, 1], label="P1 quits")
g.set_outcome(g.root.children[0].children[0], p1_self_shot)
g.set_outcome(g.root.children[0].children[1], p1_quit)

# Chamber 2 (root.children[1]):
# Player 1: Pull -> empty (chamber1), continuation to Player 2 at children[0].
# Quit -> [0,1]
g.append_move(g.root.children[1], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[1].children[0], "Player 2", ["Pull", "Quit"])
# Outcomes:
# If P2 Pulls at this node (children[0]) and loaded=2 -> P2 dies -> [1, -1]
# If P2 Quits (children[1]) -> P2 withdraws -> P1 wins -> [1, 0]
p2_self_shot_ch2 = g.add_outcome([1, -1], label="P2 shot (chamber2)")
p2_quit_ch2 = g.add_outcome([1, 0], label="P2 quits (after one empty)")
g.set_outcome(g.root.children[1].children[0].children[0], p2_self_shot_ch2)
g.set_outcome(g.root.children[1].children[0].children[1], p2_quit_ch2)
# Also set P1 Quit outcome for this branch
g.set_outcome(g.root.children[1].children[1], p1_quit)

# Chamber 3 (root.children[2]):
# Sequence: P1 Pull (empty), P2 Pull (empty), P1's turn (children[0]) where Pull would be fatal.
g.append_move(g.root.children[2], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0].children[0], "Player 1", ["Pull", "Quit"])
# Outcomes:
# At deepest node:
# - P1 Pull (children[0]) fires if loaded=3 -> P1 dies -> [-1,1]
# - P1 Quit (children[1]) -> P1 withdraws -> [0,1]
p1_self_shot_ch3 = g.add_outcome([-1, 1], label="P1 shot (chamber3)")
p1_quit_ch3 = g.add_outcome([0, 1], label="P1 quits (after two empties)")
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_self_shot_ch3)
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quit_ch3)
# Middle node (Player 2):
# - P2 Pull (children[0]) -> continuation to P1 (handled above)
# - P2 Quit (children[1]) -> P2 withdraws -> P1 wins [1,0]
g.set_outcome(g.root.children[2].children[0].children[1], p2_quit_ch2)  # reuse [1,0]
# Top-level P1 Quit:
g.set_outcome(g.root.children[2].children[1], p1_quit)

# Chamber 4 (root.children[3]):
# Sequence: P1 Pull (empty), P2 Pull (empty), P1 Pull (empty), P2's turn where Pull would be fatal.
g.append_move(g.root.children[3], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
# Outcomes at deepest node (Player 2):
# - P2 Pull (children[0]) fires if loaded=4 -> P2 dies -> [1, -1]
# - P2 Quit (children[1]) -> P2 withdraws -> P1 wins -> [1,0]
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_self_shot_ch2)
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quit_ch2)
# One level up (Player 1):
# - P1 Quit -> P2 wins -> [0,1]
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quit_ch3)
# Middle (Player 2) Quit:
g.set_outcome(g.root.children[3].children[0].children[1], p2_quit_ch2)
# Top-level P1 Quit:
g.set_outcome(g.root.children[3].children[1], p1_quit)

# Chamber 5 (root.children[4]):
# Sequence: P1, P2, P1, P2, P1 where P1's Pull at depth 4 would be fatal.
g.append_move(g.root.children[4], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
# Deepest node (P1):
# - P1 Pull -> loaded=5 -> P1 dies -> [-1,1]
# - P1 Quit -> P1 withdraws -> [0,1]
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_self_shot_ch3)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quit_ch3)
# One level up (P2):
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quit_ch2)
# Up again (P1):
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quit_ch3)
# Middle (P2):
g.set_outcome(g.root.children[4].children[0].children[1], p2_quit_ch2)
# Top-level P1 Quit:
g.set_outcome(g.root.children[4].children[1], p1_quit)

# Chamber 6 (root.children[5]):
# Full depth: P1, P2, P1, P2, P1, P2 where final P2 Pull would be fatal if loaded=6.
g.append_move(g.root.children[5], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
# Deepest node (P2):
# - P2 Pull -> loaded=6 -> P2 dies -> [1,-1]
# - P2 Quit -> P2 withdraws -> P1 wins -> [1,0]
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_self_shot_ch2)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quit_ch2)
# One up (P1):
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quit_ch3)
# Up (P2):
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quit_ch2)
# Up (P1):
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quit_ch3)
# Up (P2):
g.set_outcome(g.root.children[5].children[0].children[1], p2_quit_ch2)
# Top-level P1 Quit:
g.set_outcome(g.root.children[5].children[1], p1_quit)

# ---- Set information sets for imperfect information (players know the number of prior empties but not which remaining chamber is loaded) ----
# The following groupings follow the mapping provided:
# - All Player 1 decision nodes before any pulls (t = 0) form one infoset.
g.set_infoset(g.root.children[1], g.root.children[0].infoset)
g.set_infoset(g.root.children[2], g.root.children[0].infoset)
g.set_infoset(g.root.children[3], g.root.children[0].infoset)
g.set_infoset(g.root.children[4], g.root.children[0].infoset)
g.set_infoset(g.root.children[5], g.root.children[0].infoset)

# - All Player 2 decision nodes after one survived pull (t = 1) form one infoset.
g.set_infoset(g.root.children[2].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[1].children[0].infoset)

# - All Player 1 decision nodes after two survived pulls (t = 2) form one infoset.
g.set_infoset(g.root.children[3].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[2].children[0].children[0].infoset)

# - All Player 2 decision nodes after three survived pulls (t = 3) form one infoset.
g.set_infoset(g.root.children[4].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)

# - All Player 1 decision nodes after four survived pulls (t = 4) form one infoset.
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].children[0].infoset)

# Save the constructed EFG to a file.
g.to_efg("sequential_russian_roulette.efg")