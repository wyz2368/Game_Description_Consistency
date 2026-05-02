import pygambit as gbt

# Six-chamber alternating Russian roulette
# Players: P1 (player 1) and P2 (player 2)
# Reasoning:
# - Root is a chance node selecting which chamber (1..6) contains the bullet.
# - The cylinder is fixed; if the bullet is in position k, then the k-th pull (counting from 1)
#   will be lethal. Players alternate: P1 pulls on turns 1,3,5; P2 on turns 2,4,6.
# - On any decision a player has two actions: "Pull" (index 0) and "Quit" (index 1).
#   We choose the action order so that children[0] corresponds to the Pull continuation
#   and children[1] corresponds to Quit (an immediate terminal outcome).
# - Information structure: a player on a given turn knows how many safe pulls have occurred
#   but not the original chamber. Thus all decision nodes for the same player that occur
#   at the same turn are in the same information set. The mapping below follows that logic.
# - We build the entire tree explicitly without loops or recursion and then set infosets.

g = gbt.Game.new_tree(players=["P1", "P2"],
                      title="Six-chamber alternating Russian roulette")

# Chance at root: six equally likely bullet positions
g.append_move(g.root, g.players.chance, ["Pos1", "Pos2", "Pos3", "Pos4", "Pos5", "Pos6"])
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                                    gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# First moves (turn 1) by P1 at each possible bullet position
g.append_move(g.root.children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[1], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[2], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[3], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[4], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[5], "P1", ["Pull", "Quit"])

# Second moves (turn 2) by P2 after one safe pull.
# These exist for bullet positions 2..6 (i.e., root.children[1..5].children[0])
g.append_move(g.root.children[1].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "P2", ["Pull", "Quit"])

# Third moves (turn 3) by P1 after two safe pulls.
# These exist for bullet positions 3..6 (root.children[2..5].children[0].children[0])
g.append_move(g.root.children[2].children[0].children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "P1", ["Pull", "Quit"])

# Fourth moves (turn 4) by P2 after three safe pulls.
# These exist for bullet positions 4..6 (root.children[3..5].children[0].children[0].children[0])
g.append_move(g.root.children[3].children[0].children[0].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "P2", ["Pull", "Quit"])

# Fifth moves (turn 5) by P1 after four safe pulls.
# These exist for bullet positions 5..6 (root.children[4..5].children[0].children[0].children[0].children[0])
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "P1", ["Pull", "Quit"])

# Sixth move (turn 6) by P2 after five safe pulls.
# This exists only for bullet position 6 (deepest single node)
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "P2", ["Pull", "Quit"])

# Outcomes:
# - If a player pulls and hits the loaded chamber, that player gets -1 and the other gets 1.
# - If a player quits, that player gets 0 and the other gets 1.
p1_quit = g.add_outcome([0, 1], label="P1 quits")
p2_quit = g.add_outcome([1, 0], label="P2 quits")
p1_shot = g.add_outcome([-1, 1], label="P1 shot")
p2_shot = g.add_outcome([1, -1], label="P2 shot")

# Set outcomes for bullet position 1 (pos1):
# - P1's Pull at turn 1 is deadly
g.set_outcome(g.root.children[0].children[0], p1_shot)
# - P1's Quit at turn 1
g.set_outcome(g.root.children[0].children[1], p1_quit)

# Bullet position 2 (pos2):
# - P1 quit at turn 1
g.set_outcome(g.root.children[1].children[1], p1_quit)
# - At P2 node (turn 2): Pull is deadly, Quit yields P2 quits
g.set_outcome(g.root.children[1].children[0].children[0], p2_shot)
g.set_outcome(g.root.children[1].children[0].children[1], p2_quit)

# Bullet position 3 (pos3):
# - P1 quit at turn 1
g.set_outcome(g.root.children[2].children[1], p1_quit)
# - At P2 node after one safe pull: P2 quit
g.set_outcome(g.root.children[2].children[0].children[1], p2_quit)
# - At P1 node (turn 3): Pull is deadly, Quit yields P1 quits
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_shot)
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quit)

# Bullet position 4 (pos4):
# - P1 quit at turn 1
g.set_outcome(g.root.children[3].children[1], p1_quit)
# - P2 node after one safe pull: P2 quit
g.set_outcome(g.root.children[3].children[0].children[1], p2_quit)
# - P1 node after two safe pulls: P1 quit
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quit)
# - P2 node at turn 4: Pull is deadly, Quit yields P2 quits
g.set_outcome(g.root.children[3].children[0].children[0].children[0], p2_shot)
# Note: the node indices above follow the convention Children[0] = Pull, Children[1] = Quit

# Bullet position 5 (pos5):
# - P1 quit at turn 1
g.set_outcome(g.root.children[4].children[1], p1_quit)
# - P2 after one safe pull: P2 quit
g.set_outcome(g.root.children[4].children[0].children[1], p2_quit)
# - P1 after two safe pulls: P1 quit
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quit)
# - P2 after three safe pulls: P2 quit
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quit)
# - P1 at turn 5: Pull is deadly, Quit yields P1 quits
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_shot)
# The above path: children[0] at each level corresponds to continuing pulls; final children[0] is the deadly pull.

# Bullet position 6 (pos6):
# - P1 quit at turn 1
g.set_outcome(g.root.children[5].children[1], p1_quit)
# - P2 after one safe pull: P2 quit
g.set_outcome(g.root.children[5].children[0].children[1], p2_quit)
# - P1 after two safe pulls: P1 quit
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quit)
# - P2 after three safe pulls: P2 quit
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quit)
# - P1 after four safe pulls: P1 quit
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quit)
# - P2 at turn 6: Pull is deadly, Quit yields P2 quits
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_shot)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quit)

# Set information sets to reflect that players know only the turn number, not the initial chamber.
# P1's initial infoset (turn 1): all six starting decision nodes belong to same infoset.
g.set_infoset(g.root.children[1], g.root.children[0].infoset)
g.set_infoset(g.root.children[2], g.root.children[0].infoset)
g.set_infoset(g.root.children[3], g.root.children[0].infoset)
g.set_infoset(g.root.children[4], g.root.children[0].infoset)
g.set_infoset(g.root.children[5], g.root.children[0].infoset)

# P2's first-turn infoset (turn 2): nodes after one safe pull for bullet positions 2..6
g.set_infoset(g.root.children[2].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[1].children[0].infoset)

# P1's second-turn infoset (turn 3): nodes after two safe pulls for bullet positions 3..6
g.set_infoset(g.root.children[3].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[2].children[0].children[0].infoset)

# P2's second-turn infoset (turn 4): nodes after three safe pulls for bullet positions 4..6
g.set_infoset(g.root.children[4].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)

# P1's third-turn infoset (turn 5): nodes after four safe pulls for bullet positions 5..6
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].children[0].infoset)

# Save the EFG
g.to_efg("six_chamber_russian_roulette.efg")