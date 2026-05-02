import pygambit as gbt

# Thought process (written step by step as comments):
# - This is a sequential game with perfect information (all histories observed).
# - Two players alternate turns pulling from a six-chamber revolver.
# - Player 1 starts. On each turn the acting player chooses Quit or Pull.
# - Quit ends the game: quitter gets 0, the other player gets 1.
# - Pull when n > 1 chambers remain leads to a chance node:
#     Fire with probability 1/n -> acting player dies -> payoff -1 for actor, +1 for other.
#     Survive with probability (n-1)/n -> play continues with other player and n-1 chambers.
# - Pull when n == 1 fires for certain (no chance node needed): acting player dies immediately.
# - All information sets are singletons (players observe all previous outcomes), so we do not
#   set any nontrivial infosets.
# - We explicitly construct the full tree without loops or recursion by expanding each branch.
# - We use gbt.Rational for chance probabilities as required.

# Create the game with two players: Player 1 and Player 2
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# Predefine outcomes to reuse
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_dies = g.add_outcome([1, -1], label="P2 dies")
p1_quits = g.add_outcome([0, 1], label="P1 quits")
p2_quits = g.add_outcome([1, 0], label="P2 quits")

# Root: Player 1 decision with 6 chambers remaining
g.append_move(g.root, "Player 1", ["Quit", "Pull"])

# If Player 1 quits immediately
g.set_outcome(g.root.children[0], p1_quits)

# If Player 1 pulls with 6 chambers remaining -> chance (fire 1/6, survive 5/6)
g.append_move(g.root.children[1], g.players.chance, ["Fire", "Survive"])
g.set_chance_probs(g.root.children[1].infoset,
                   [gbt.Rational(1, 6), gbt.Rational(5, 6)])

# Chance branch: Fire -> Player 1 dies
g.set_outcome(g.root.children[1].children[0], p1_dies)

# Chance branch: Survive -> Player 2 decision with 5 chambers remaining
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[1].children[1].children[0], p2_quits)

# Player 2 pulls with 5 chambers -> chance (fire 1/5, survive 4/5)
g.append_move(g.root.children[1].children[1].children[1], g.players.chance, ["Fire", "Survive"])
g.set_chance_probs(g.root.children[1].children[1].children[1].infoset,
                   [gbt.Rational(1, 5), gbt.Rational(4, 5)])

# Fire -> Player 2 dies
g.set_outcome(g.root.children[1].children[1].children[1].children[0], p2_dies)

# Survive -> Player 1 decision with 4 chambers remaining
g.append_move(g.root.children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[0], p1_quits)

# Player 1 pulls with 4 chambers -> chance (fire 1/4, survive 3/4)
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1], g.players.chance, ["Fire", "Survive"])
g.set_chance_probs(g.root.children[1].children[1].children[1].children[1].children[1].infoset,
                   [gbt.Rational(1, 4), gbt.Rational(3, 4)])

# Fire -> Player 1 dies
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[0], p1_dies)

# Survive -> Player 2 decision with 3 chambers remaining
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[0], p2_quits)

# Player 2 pulls with 3 chambers -> chance (fire 1/3, survive 2/3)
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1], g.players.chance, ["Fire", "Survive"])
g.set_chance_probs(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].infoset,
                   [gbt.Rational(1, 3), gbt.Rational(2, 3)])

# Fire -> Player 2 dies
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0], p2_dies)

# Survive -> Player 1 decision with 2 chambers remaining
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0], p1_quits)

# Player 1 pulls with 2 chambers -> chance (fire 1/2, survive 1/2)
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1], g.players.chance, ["Fire", "Survive"])
g.set_chance_probs(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].infoset,
                   [gbt.Rational(1, 2), gbt.Rational(1, 2)])

# Fire -> Player 1 dies
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0], p1_dies)

# Survive -> Player 2 decision with 1 chamber remaining
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0], p2_quits)

# When 1 chamber remains, Pull fires certainly -> immediate death for acting player (Player 2)
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1], p2_dies)

# Save the EFG
g.to_efg("six_chamber_russian_roulette.efg")