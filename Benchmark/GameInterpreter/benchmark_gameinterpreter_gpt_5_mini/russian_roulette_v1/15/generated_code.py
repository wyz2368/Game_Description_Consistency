import pygambit as gbt

# Build an extensive-form game for a 6-chamber alternating "Russian roulette" game.
# Two players alternate turns (Player1 starts). Chance first chooses which chamber (0..5)
# contains the bullet with equal probability 1/6. The chosen chamber is fixed but unobserved.
# On each turn a player chooses between "Pull" (first action) and "Quit" (second action).
# - If a player Quits, he gets 0 and the other gets 1.
# - If a player Pulls and the current chamber is the loaded one, he gets -1 and the other gets 1.
# - If a player Pulls and the chamber is empty, play continues to the other player.
#
# We explicitly construct the full tree without loops. We group decision nodes into information
# sets so that a player at turn t cannot distinguish which initial chamber (chance outcome)
# was selected, only that the game has reached that turn.

g = gbt.Game.new_tree(players=["Player1", "Player2"],
                      title="Six-chamber alternating revolver")

# 1) Chance chooses the loaded chamber among 6 equally likely options.
g.append_move(g.root, g.players.chance,
              ["Chamber 0", "Chamber 1", "Chamber 2", "Chamber 3", "Chamber 4", "Chamber 5"])
g.set_chance_probs(g.root.infoset,
                   [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                    gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Pre-create commonly used outcome objects to reuse across terminal nodes:
# Player1 dies, Player2 dies, Player1 quits, Player2 quits
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_dies = g.add_outcome([1, -1], label="P2 dies")
p1_quits = g.add_outcome([0, 1], label="P1 quits")
p2_quits = g.add_outcome([1, 0], label="P2 quits")

# 2) Turn 1 (Player1) nodes for each initial chamber j = 0..5.
# At each root.child[j] Player1 chooses Pull (children[0]) or Quit (children[1]).
g.append_move(g.root.children[0], "Player1", ["Pull", "Quit"])
g.append_move(g.root.children[1], "Player1", ["Pull", "Quit"])
g.append_move(g.root.children[2], "Player1", ["Pull", "Quit"])
g.append_move(g.root.children[3], "Player1", ["Pull", "Quit"])
g.append_move(g.root.children[4], "Player1", ["Pull", "Quit"])
g.append_move(g.root.children[5], "Player1", ["Pull", "Quit"])

# Outcomes for Turn1 quits (Player1 quitting at t=1 gives [0,1]) and pulls that immediately hit the bullet.
# For j=0, pulling at turn 1 hits the bullet -> Player1 dies.
g.set_outcome(g.root.children[0].children[1], p1_quits)   # P1 quits at chamber 0
g.set_outcome(g.root.children[0].children[0], p1_dies)    # P1 pulls and dies when bullet in chamber 0

# For j=1..5, if Player1 quits at turn1 it's terminal; if he pulls, the game continues to Player2 at turn2.
g.set_outcome(g.root.children[1].children[1], p1_quits)
g.set_outcome(g.root.children[2].children[1], p1_quits)
g.set_outcome(g.root.children[3].children[1], p1_quits)
g.set_outcome(g.root.children[4].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[1], p1_quits)

# 3) Turn 2 (Player2) nodes: reachable only when the bullet was not in chamber 0 => j = 1..5.
# These nodes are the result of one Pull (children[0]) from root.children[j].
g.append_move(g.root.children[1].children[0], "Player2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "Player2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "Player2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "Player2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "Player2", ["Pull", "Quit"])

# Outcomes for Turn2 quits (Player2 quits -> [1,0]) and pulls that immediately hit the bullet (j==1).
g.set_outcome(g.root.children[1].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[2].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[3].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[4].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[5].children[0].children[1], p2_quits)

# For j=1, Player2 pulling at turn2 hits the bullet -> P2 dies.
g.set_outcome(g.root.children[1].children[0].children[0], p2_dies)

# For j>=2, a Pull at turn2 continues to turn3 (Player1).
# 4) Turn 3 (Player1) nodes for j = 2..5.
g.append_move(g.root.children[2].children[0].children[0], "Player1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "Player1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "Player1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "Player1", ["Pull", "Quit"])

# Outcomes for Turn3 quits (Player1 quits -> [0,1]) and pulls that hit the bullet (j==2).
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quits)

g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_dies)

# For j>=3, a Pull at turn3 continues to turn4 (Player2).
# 5) Turn 4 (Player2) nodes for j = 3..5.
g.append_move(g.root.children[3].children[0].children[0].children[0], "Player2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "Player2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "Player2", ["Pull", "Quit"])

# Outcomes for Turn4 quits (Player2 quits -> [1,0]) and pulls that hit the bullet (j==3).
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quits)

g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_dies)

# For j>=4, a Pull at turn4 continues to turn5 (Player1).
# 6) Turn 5 (Player1) nodes for j = 4..5.
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "Player1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "Player1", ["Pull", "Quit"])

# Outcomes for Turn5 quits (Player1 quits -> [0,1]) and pulls that hit the bullet (j==4).
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quits)

g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_dies)

# For j=5, a Pull at turn5 continues to turn6 (Player2).
# 7) Turn 6 (Player2) node for j = 5 (singleton).
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "Player2", ["Pull", "Quit"])

# Outcomes for Turn6: Quit -> Player2 quits; Pull -> since j==5 this is the loaded chamber, Player2 dies.
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_dies)

# 8) Set information sets so players do not observe the initial chamber choice, only the turn.
# Turn 1 (Player1) all six starting nodes are in the same infoset.
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Turn 2 (Player2): nodes for j = 1..5 (the node after one successful Pull).
g.set_infoset(g.root.children[1].children[0], g.root.children[2].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[2].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[2].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[2].children[0].infoset)

# Turn 3 (Player1): nodes for j = 2..5 (after two successful Pulls).
g.set_infoset(g.root.children[2].children[0].children[0], g.root.children[3].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[3].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[3].children[0].children[0].infoset)

# Turn 4 (Player2): nodes for j = 3..5 (after three successful Pulls).
g.set_infoset(g.root.children[3].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].infoset)

# Turn 5 (Player1): nodes for j = 4..5 (after four successful Pulls).
g.set_infoset(g.root.children[4].children[0].children[0].children[0].children[0], g.root.children[5].children[0].children[0].children[0].children[0].infoset)

# Turn 6 (Player2) is a singleton (j=5) so no infoset grouping needed.

# Save the EFG to file
g.to_efg("six_chamber_revolver.efg")