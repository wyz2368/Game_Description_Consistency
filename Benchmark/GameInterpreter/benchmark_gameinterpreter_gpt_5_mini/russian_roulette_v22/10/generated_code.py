import pygambit as gbt

# Build an extensive-form game for alternating Russian roulette with a six-chamber revolver.
# Reasoning (written step-by-step in comments as requested):
# - The only relevant public state is how many unpulled chambers remain (n = 6 down to 1).
# - Players alternate turns; Player 1 moves when n is even (starting at n=6), Player 2 when n is odd.
# - At each decision with n >= 2 the player can Quit (guaranteed survival: payoff 0 for quitter, 1 for opponent)
#   or Pull. If they Pull and the gun fires, that player dies (payoff -1) and the other gets 1.
#   If they Pull and the gun does not fire, play continues with n-1 chambers and the other player's turn.
# - When n == 1, Pull fires for certain (no chance node needed).
# - All trigger pulls and outcomes are common knowledge, so no nontrivial information sets are needed.
# - We explicitly unroll the tree for n = 6 down to 1 without using loops or recursion.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating Russian Roulette, 6 chambers")

# Pre-create commonly used outcome objects to reuse them.
# Player 1 dies: P1 = -1, P2 = 1
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
# Player 2 dies: P1 = 1, P2 = -1
p2_dies = g.add_outcome([1, -1], label="P2 dies")
# Player 1 quits: P1 = 0, P2 = 1
p1_quit = g.add_outcome([0, 1], label="P1 quits")
# Player 2 quits: P1 = 1, P2 = 0
p2_quit = g.add_outcome([1, 0], label="P2 quits")

# Root: n = 6, Player 1 to move.
g.append_move(g.root, "Player 1", ["Pull", "Quit"])
# If Player 1 quits immediately at n=6:
g.set_outcome(g.root.children[1], p1_quit)

# If Player 1 pulls at n=6 -> chance: fire with probability 1/6, not-fire with probability 5/6.
g.append_move(g.root.children[0], g.players.chance, ["Fire", "NoFire"])
g.set_chance_probs(g.root.children[0].infoset, [gbt.Rational(1, 6), gbt.Rational(5, 6)])
# Fire at n=6: Player 1 dies
g.set_outcome(g.root.children[0].children[0], p1_dies)
# NoFire at n=6 -> n = 5, Player 2 to move
g.append_move(g.root.children[0].children[1], "Player 2", ["Pull", "Quit"])
# If Player 2 quits at n=5:
g.set_outcome(g.root.children[0].children[1].children[1], p2_quit)

# Player 2 pulls at n=5 -> chance: fire with prob 1/5, not-fire with prob 4/5
g.append_move(g.root.children[0].children[1].children[0], g.players.chance, ["Fire", "NoFire"])
g.set_chance_probs(g.root.children[0].children[1].children[0].infoset, [gbt.Rational(1, 5), gbt.Rational(4, 5)])
# Fire at n=5: Player 2 dies
g.set_outcome(g.root.children[0].children[1].children[0].children[0], p2_dies)
# NoFire at n=5 -> n = 4, Player 1 to move
g.append_move(g.root.children[0].children[1].children[0].children[1], "Player 1", ["Pull", "Quit"])
# If Player 1 quits at n=4:
g.set_outcome(g.root.children[0].children[1].children[0].children[1].children[1], p1_quit)

# Player 1 pulls at n=4 -> chance: fire with prob 1/4, not-fire with prob 3/4
g.append_move(g.root.children[0].children[1].children[0].children[1].children[0], g.players.chance, ["Fire", "NoFire"])
g.set_chance_probs(g.root.children[0].children[1].children[0].children[1].children[0].infoset, [gbt.Rational(1, 4), gbt.Rational(3, 4)])
# Fire at n=4: Player 1 dies
g.set_outcome(g.root.children[0].children[1].children[0].children[1].children[0].children[0], p1_dies)
# NoFire at n=4 -> n = 3, Player 2 to move
g.append_move(g.root.children[0].children[1].children[0].children[1].children[0].children[1], "Player 2", ["Pull", "Quit"])
# If Player 2 quits at n=3:
g.set_outcome(g.root.children[0].children[1].children[0].children[1].children[0].children[1].children[1], p2_quit)

# Player 2 pulls at n=3 -> chance: fire with prob 1/3, not-fire with prob 2/3
g.append_move(g.root.children[0].children[1].children[0].children[1].children[0].children[1].children[0], g.players.chance, ["Fire", "NoFire"])
g.set_chance_probs(g.root.children[0].children[1].children[0].children[1].children[0].children[1].children[0].infoset, [gbt.Rational(1, 3), gbt.Rational(2, 3)])
# Fire at n=3: Player 2 dies
g.set_outcome(g.root.children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[0], p2_dies)
# NoFire at n=3 -> n = 2, Player 1 to move
g.append_move(g.root.children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[1], "Player 1", ["Pull", "Quit"])
# If Player 1 quits at n=2:
g.set_outcome(g.root.children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[1].children[1], p1_quit)

# Player 1 pulls at n=2 -> chance: fire with prob 1/2, not-fire with prob 1/2
g.append_move(g.root.children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[1].children[0], g.players.chance, ["Fire", "NoFire"])
g.set_chance_probs(g.root.children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[1].children[0].infoset, [gbt.Rational(1, 2), gbt.Rational(1, 2)])
# Fire at n=2: Player 1 dies
g.set_outcome(g.root.children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[0], p1_dies)
# NoFire at n=2 -> n = 1, Player 2 to move
g.append_move(g.root.children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[1], "Player 2", ["Pull", "Quit"])
# If Player 2 quits at n=1:
g.set_outcome(g.root.children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[1].children[1], p2_quit)

# At n=1, Pull fires for certain. If Player 2 pulls at n=1: Player 2 dies.
g.set_outcome(g.root.children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[1].children[0].children[1].children[0], p2_dies)

# Save the game to an EFG file
g.to_efg("russian_roulette_6_chambers.efg")