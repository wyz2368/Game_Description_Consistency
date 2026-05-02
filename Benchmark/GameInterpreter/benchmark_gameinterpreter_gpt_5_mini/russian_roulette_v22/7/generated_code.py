import pygambit as gbt

# Build an extensive-form game for a 6-chamber "revolver" (Russian roulette style)
# Players alternate turns, Player 1 starts.
# On a turn, a player chooses "Quit" (guaranteed survival, the other player wins)
# or "Pull" (pull the trigger). If the gun fires the acting player dies (payoff -1),
# the other player gets +1. If it doesn't fire, play continues with one fewer chamber.
# Chance outcomes (fire / no fire) are observed by both players, so this is
# a game of perfect information except for the chance moves.

# Reasoning (step-by-step), encoded as comments:
# - There are 6 chambers initially. Player 1 acts at states with 6,4,2 chambers.
# - Player 2 acts at states with 5,3,1 chambers.
# - For a pull when n>1 chambers remain, chance fires with probability 1/n and
#   not-fire with probability (n-1)/n.
# - For a pull when n==1, the pull fires with certainty (we model as a chance
#   node with a single "Fire" action with probability 1).
# - No information sets need to be merged because all previous outcomes are
#   common knowledge before each decision.
# - We explicitly construct the tree without loops or recursion, naming nodes
#   for clarity.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating revolver with 6 chambers")

# Root: Player 1 with 6 chambers remaining
node_p1_n6 = g.root
g.append_move(node_p1_n6, "Player 1", ["Quit", "Pull"])

# If Player 1 quits immediately: P1 gets 0, P2 gets 1
g.set_outcome(node_p1_n6.children[0], g.add_outcome([0, 1], label="P1 quits at 6"))

# If Player 1 pulls at 6, chance determines Fire (1/6) or No fire (5/6)
node_after_p1_pull_n6 = node_p1_n6.children[1]
g.append_move(node_after_p1_pull_n6, g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(node_after_p1_pull_n6.infoset, [gbt.Rational(1, 6), gbt.Rational(5, 6)])

# Fire at 6: P1 dies -> P1 = -1, P2 = +1
g.set_outcome(node_after_p1_pull_n6.children[0], g.add_outcome([-1, 1], label="P1 shot at 6"))

# No fire at 6 -> Player 2 with 5 chambers remaining
node_p2_n5 = node_after_p1_pull_n6.children[1]
g.append_move(node_p2_n5, "Player 2", ["Quit", "Pull"])

# If Player 2 quits at 5: P2 = 0, P1 = +1 (other wins)
g.set_outcome(node_p2_n5.children[0], g.add_outcome([1, 0], label="P2 quits at 5"))

# If Player 2 pulls at 5: chance Fire (1/5) or No fire (4/5)
node_after_p2_pull_n5 = node_p2_n5.children[1]
g.append_move(node_after_p2_pull_n5, g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(node_after_p2_pull_n5.infoset, [gbt.Rational(1, 5), gbt.Rational(4, 5)])

# Fire at 5: P2 dies -> P1 = +1, P2 = -1
g.set_outcome(node_after_p2_pull_n5.children[0], g.add_outcome([1, -1], label="P2 shot at 5"))

# No fire at 5 -> Player 1 with 4 chambers remaining
node_p1_n4 = node_after_p2_pull_n5.children[1]
g.append_move(node_p1_n4, "Player 1", ["Quit", "Pull"])

# If Player 1 quits at 4: P1 = 0, P2 = +1
g.set_outcome(node_p1_n4.children[0], g.add_outcome([0, 1], label="P1 quits at 4"))

# If Player 1 pulls at 4: chance Fire (1/4) or No fire (3/4)
node_after_p1_pull_n4 = node_p1_n4.children[1]
g.append_move(node_after_p1_pull_n4, g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(node_after_p1_pull_n4.infoset, [gbt.Rational(1, 4), gbt.Rational(3, 4)])

# Fire at 4: P1 dies -> P1 = -1, P2 = +1
g.set_outcome(node_after_p1_pull_n4.children[0], g.add_outcome([-1, 1], label="P1 shot at 4"))

# No fire at 4 -> Player 2 with 3 chambers remaining
node_p2_n3 = node_after_p1_pull_n4.children[1]
g.append_move(node_p2_n3, "Player 2", ["Quit", "Pull"])

# If Player 2 quits at 3: P2 = 0, P1 = +1
g.set_outcome(node_p2_n3.children[0], g.add_outcome([1, 0], label="P2 quits at 3"))

# If Player 2 pulls at 3: chance Fire (1/3) or No fire (2/3)
node_after_p2_pull_n3 = node_p2_n3.children[1]
g.append_move(node_after_p2_pull_n3, g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(node_after_p2_pull_n3.infoset, [gbt.Rational(1, 3), gbt.Rational(2, 3)])

# Fire at 3: P2 dies -> P1 = +1, P2 = -1
g.set_outcome(node_after_p2_pull_n3.children[0], g.add_outcome([1, -1], label="P2 shot at 3"))

# No fire at 3 -> Player 1 with 2 chambers remaining
node_p1_n2 = node_after_p2_pull_n3.children[1]
g.append_move(node_p1_n2, "Player 1", ["Quit", "Pull"])

# If Player 1 quits at 2: P1 = 0, P2 = +1
g.set_outcome(node_p1_n2.children[0], g.add_outcome([0, 1], label="P1 quits at 2"))

# If Player 1 pulls at 2: chance Fire (1/2) or No fire (1/2)
node_after_p1_pull_n2 = node_p1_n2.children[1]
g.append_move(node_after_p1_pull_n2, g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(node_after_p1_pull_n2.infoset, [gbt.Rational(1, 2), gbt.Rational(1, 2)])

# Fire at 2: P1 dies -> P1 = -1, P2 = +1
g.set_outcome(node_after_p1_pull_n2.children[0], g.add_outcome([-1, 1], label="P1 shot at 2"))

# No fire at 2 -> Player 2 with 1 chamber remaining
node_p2_n1 = node_after_p1_pull_n2.children[1]
g.append_move(node_p2_n1, "Player 2", ["Quit", "Pull"])

# If Player 2 quits at 1: P2 = 0, P1 = +1
g.set_outcome(node_p2_n1.children[0], g.add_outcome([1, 0], label="P2 quits at 1"))

# If Player 2 pulls at 1: the trigger fires for certain.
node_after_p2_pull_n1 = node_p2_n1.children[1]
g.append_move(node_after_p2_pull_n1, g.players.chance, ["Fire"])
g.set_chance_probs(node_after_p2_pull_n1.infoset, [gbt.Rational(1, 1)])

# Fire at 1: P2 dies -> P1 = +1, P2 = -1
g.set_outcome(node_after_p2_pull_n1.children[0], g.add_outcome([1, -1], label="P2 shot at 1 (certain)"))

# Save the EFG to file
g.to_efg("revolver_6chambers.efg")