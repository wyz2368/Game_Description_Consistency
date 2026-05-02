import pygambit as gbt

# Reasoning (step-by-step) in comments:
# Step 1: Two players alternate turns. Player 1 acts first.
# Step 2: Each decision node is fully informed (history known), so no nontrivial infosets are required.
# Step 3: There are 6 chambers initially. Each successful "no fire" consumes one chamber.
# Step 4: On a decision, a player can Quit (guaranteed survival, opponent wins) or Pull.
#         - If remaining chambers > 1: Pull leads to a chance node with probability 1/(remaining)
#           of firing (actor dies) and probability (remaining-1)/remaining of no fire (game continues
#           with remaining-1 chambers and the other player's decision).
#         - If remaining chambers == 1: Pull fires for certain (actor dies). No chance node needed.
# Step 5: Payoffs:
#         - If a player quits: quitting player gets 0, the other player gets 1.
#         - If a player dies by fire: the dead player gets -1, the other gets 1.
# Step 6: We explicitly construct the tree for remaining = 6 down to 1, alternating players,
#         without using loops or recursion.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating Russian roulette, 6-chamber")

# Root: Player 1 chooses Quit or Pull with 6 chambers remaining.
g.append_move(g.root, "Player 1", ["Quit", "Pull"])
p1_quit = g.root.children[0]
p1_pull = g.root.children[1]

# If Player 1 quits immediately, Player 1 gets 0 and Player 2 gets 1.
g.set_outcome(p1_quit, g.add_outcome([0, 1], label="P1 quits at 6"))

# Player 1 pulls with 6 chambers: chance with prob 1/6 fire, 5/6 no fire.
g.append_move(p1_pull, g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(p1_pull.infoset, [gbt.Rational(1, 6), gbt.Rational(5, 6)])
p1_fire_6 = p1_pull.children[0]
p1_survive_6 = p1_pull.children[1]

# If it fires, Player 1 dies: P1 gets -1, P2 gets 1.
g.set_outcome(p1_fire_6, g.add_outcome([-1, 1], label="P1 dies on pull at 6"))

# Now remaining = 5, Player 2's turn.
g.append_move(p1_survive_6, "Player 2", ["Quit", "Pull"])
p2_quit_5 = p1_survive_6.children[0]
p2_pull_5 = p1_survive_6.children[1]

# If Player 2 quits at this point, Player 2 gets 0 and Player 1 gets 1.
g.set_outcome(p2_quit_5, g.add_outcome([1, 0], label="P2 quits at 5"))

# Player 2 pulls with 5 chambers: chance with prob 1/5 fire, 4/5 no fire.
g.append_move(p2_pull_5, g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(p2_pull_5.infoset, [gbt.Rational(1, 5), gbt.Rational(4, 5)])
p2_fire_5 = p2_pull_5.children[0]
p2_survive_5 = p2_pull_5.children[1]

# If it fires, Player 2 dies: P2 gets -1, P1 gets 1.
g.set_outcome(p2_fire_5, g.add_outcome([1, -1], label="P2 dies on pull at 5"))

# Now remaining = 4, Player 1's turn.
g.append_move(p2_survive_5, "Player 1", ["Quit", "Pull"])
p1_quit_4 = p2_survive_5.children[0]
p1_pull_4 = p2_survive_5.children[1]

g.set_outcome(p1_quit_4, g.add_outcome([0, 1], label="P1 quits at 4"))

# Player 1 pulls with 4 chambers: chance with prob 1/4 fire, 3/4 no fire.
g.append_move(p1_pull_4, g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(p1_pull_4.infoset, [gbt.Rational(1, 4), gbt.Rational(3, 4)])
p1_fire_4 = p1_pull_4.children[0]
p1_survive_4 = p1_pull_4.children[1]

g.set_outcome(p1_fire_4, g.add_outcome([-1, 1], label="P1 dies on pull at 4"))

# Now remaining = 3, Player 2's turn.
g.append_move(p1_survive_4, "Player 2", ["Quit", "Pull"])
p2_quit_3 = p1_survive_4.children[0]
p2_pull_3 = p1_survive_4.children[1]

g.set_outcome(p2_quit_3, g.add_outcome([1, 0], label="P2 quits at 3"))

# Player 2 pulls with 3 chambers: chance with prob 1/3 fire, 2/3 no fire.
g.append_move(p2_pull_3, g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(p2_pull_3.infoset, [gbt.Rational(1, 3), gbt.Rational(2, 3)])
p2_fire_3 = p2_pull_3.children[0]
p2_survive_3 = p2_pull_3.children[1]

g.set_outcome(p2_fire_3, g.add_outcome([1, -1], label="P2 dies on pull at 3"))

# Now remaining = 2, Player 1's turn.
g.append_move(p2_survive_3, "Player 1", ["Quit", "Pull"])
p1_quit_2 = p2_survive_3.children[0]
p1_pull_2 = p2_survive_3.children[1]

g.set_outcome(p1_quit_2, g.add_outcome([0, 1], label="P1 quits at 2"))

# Player 1 pulls with 2 chambers: chance with prob 1/2 fire, 1/2 no fire.
g.append_move(p1_pull_2, g.players.chance, ["Fire", "No fire"])
g.set_chance_probs(p1_pull_2.infoset, [gbt.Rational(1, 2), gbt.Rational(1, 2)])
p1_fire_2 = p1_pull_2.children[0]
p1_survive_2 = p1_pull_2.children[1]

g.set_outcome(p1_fire_2, g.add_outcome([-1, 1], label="P1 dies on pull at 2"))

# Now remaining = 1, Player 2's turn. Pulling fires for certain (no chance node).
g.append_move(p1_survive_2, "Player 2", ["Quit", "Pull"])
p2_quit_1 = p1_survive_2.children[0]
p2_pull_1 = p1_survive_2.children[1]

# If Player 2 quits at last chamber, Player 1 wins.
g.set_outcome(p2_quit_1, g.add_outcome([1, 0], label="P2 quits at 1"))

# If Player 2 pulls at last chamber, it fires for certain: Player 2 dies.
g.set_outcome(p2_pull_1, g.add_outcome([1, -1], label="P2 dies on pull at 1"))

# Save the game to an EFG file.
g.to_efg("alternating_russian_roulette_6.efg")