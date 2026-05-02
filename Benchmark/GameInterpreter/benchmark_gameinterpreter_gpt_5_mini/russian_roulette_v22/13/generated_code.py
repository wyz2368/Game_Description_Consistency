import pygambit as gbt

# Build the extensive-form game for alternating Russian roulette with 6 chambers.
# Players: Player 1 acts first, then Player 2, etc.
# Reasoning in comments:
# - The state is fully observed: the number of remaining unpulled chambers is common knowledge.
# - Therefore each decision node is a singleton information set (no g.set_infoset calls).
# - On a "Pull" action when more than one chamber remains, a chance node realizes "Fire" with
#   probability 1/remaining and "No fire" with the complementary probability.
# - When only one chamber remains, a "Pull" results in certain fire; we model that by making the
#   Pull action lead directly to the terminal outcome (no chance node needed).
# - Payoffs: shooter who dies gets -1, the winner gets 1, quitter gets 0, the other gets 1.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating Russian roulette, 6 chambers")

# Root: Player 1 with remaining = 6
g.append_move(g.root, "Player 1", ["Quit", "Pull"])
# If Player 1 quits immediately, he gets 0 and Player 2 wins (1).
g.set_outcome(g.root.children[0], g.add_outcome([0, 1], label="P1 quits (remaining=6)"))

# If Player 1 pulls with 6 remaining: chance (1/6 fire, 5/6 no fire)
g.append_move(g.root.children[1], g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(g.root.children[1].infoset, [gbt.Rational(1, 6), gbt.Rational(5, 6)])
# Fire on P1's pull: P1 dies -> (-1, 1)
g.set_outcome(g.root.children[1].children[0], g.add_outcome([-1, 1], label="P1 dies (fire, remaining=6)"))

# No fire -> Player 2 with remaining = 5
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
# If Player 2 quits at remaining=5, P1 wins (1), P2 gets 0
g.set_outcome(g.root.children[1].children[1].children[0], g.add_outcome([1, 0], label="P2 quits (remaining=5)"))

# If Player 2 pulls with 5 remaining: chance (1/5 fire, 4/5 no fire)
g.append_move(g.root.children[1].children[1].children[1], g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(g.root.children[1].children[1].children[1].infoset, [gbt.Rational(1, 5), gbt.Rational(4, 5)])
# Fire on P2's pull: P2 dies -> (1, -1)
g.set_outcome(g.root.children[1].children[1].children[1].children[0], g.add_outcome([1, -1], label="P2 dies (fire, remaining=5)"))

# No fire -> Player 1 with remaining = 4
g.append_move(g.root.children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
# If Player 1 quits at remaining=4, he gets 0 and P2 wins
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[0],
              g.add_outcome([0, 1], label="P1 quits (remaining=4)"))

# If Player 1 pulls with 4 remaining: chance (1/4 fire, 3/4 no fire)
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1], g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(g.root.children[1].children[1].children[1].children[1].children[1].infoset,
                   [gbt.Rational(1, 4), gbt.Rational(3, 4)])
# Fire on P1's pull: P1 dies -> (-1, 1)
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[0],
              g.add_outcome([-1, 1], label="P1 dies (fire, remaining=4)"))

# No fire -> Player 2 with remaining = 3
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
# If Player 2 quits at remaining=3, P1 wins (1)
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[0],
              g.add_outcome([1, 0], label="P2 quits (remaining=3)"))

# If Player 2 pulls with 3 remaining: chance (1/3 fire, 2/3 no fire)
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1],
              g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].infoset,
                   [gbt.Rational(1, 3), gbt.Rational(2, 3)])
# Fire on P2's pull: P2 dies -> (1, -1)
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0],
              g.add_outcome([1, -1], label="P2 dies (fire, remaining=3)"))

# No fire -> Player 1 with remaining = 2
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1],
              "Player 1", ["Quit", "Pull"])
# If Player 1 quits at remaining=2, he gets 0 and P2 wins
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0],
              g.add_outcome([0, 1], label="P1 quits (remaining=2)"))

# If Player 1 pulls with 2 remaining: chance (1/2 fire, 1/2 no fire)
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1],
              g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].infoset,
                   [gbt.Rational(1, 2), gbt.Rational(1, 2)])
# Fire on P1's pull: P1 dies -> (-1, 1)
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0],
              g.add_outcome([-1, 1], label="P1 dies (fire, remaining=2)"))

# No fire -> Player 2 with remaining = 1
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1],
              "Player 2", ["Quit", "Pull"])
# If Player 2 quits at remaining=1, P1 wins (1)
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0],
              g.add_outcome([1, 0], label="P2 quits (remaining=1)"))

# If Player 2 pulls at remaining=1, it fires for certain and P2 dies -> (1, -1)
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1],
              g.add_outcome([1, -1], label="P2 dies (certain fire, remaining=1)"))

# Save the game to an EFG file
g.to_efg("alternating_russian_roulette_6chambers.efg")