import pygambit as gbt

# Reasoning and construction notes (step by step encoded as comments):
# - The game has two players: Player 1 and Player 2. Player 1 moves first.
# - State at each decision is determined by (current player, number of remaining chambers).
# - After each pull that does not fire, the number of remaining chambers decreases by one
#   and the other player makes the next decision.
# - If a player quits, the quitter gets 0 and the other player gets 1.
# - If the gun fires, the shooter gets -1 and the other player gets 1.
# - For remaining > 1, a pull leads to a chance node with probabilities:
#     fire: 1 / remaining
#     misfire: (remaining - 1) / remaining
# - For remaining == 1, a pull fires for certain (no chance node needed).
# - Players always observe the outcome of each pull and the current remaining chamber count,
#   so there are no nontrivial information sets to set manually.
# - The tree is constructed explicitly without loops or recursion.

# Create the game
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Russian roulette with a six-chamber revolver")

# Pre-create outcome objects for reuse:
# When a player quits: quitter 0, other player 1.
p1_quits = g.add_outcome([0, 1], label="P1 quits")
p2_quits = g.add_outcome([1, 0], label="P2 quits")
# When a player is shot: shooter -1, other +1.
p1_shot = g.add_outcome([-1, 1], label="P1 shot (P2 wins)")
p2_shot = g.add_outcome([1, -1], label="P2 shot (P1 wins)")

# Root: Player 1 with 6 chambers remaining
g.append_move(g.root, "Player 1", ["Quit", "Pull"])
# If Player 1 quits immediately
g.set_outcome(g.root.children[0], p1_quits)

# If Player 1 pulls with 6 chambers -> chance node with fire prob 1/6
g.append_move(g.root.children[1], g.players.chance, ["Fire", "Misfire"])
g.set_chance_probs(g.root.children[1].infoset,
                   [gbt.Rational(1, 6), gbt.Rational(5, 6)])
# Fire at this stage: Player 1 shot
g.set_outcome(g.root.children[1].children[0], p1_shot)

# Misfire -> Player 2 with 5 chambers remaining
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
g.set_outcome(g.root.children[1].children[1].children[0], p2_quits)

# Player 2 pulls with 5 chambers -> chance node 1/5
g.append_move(g.root.children[1].children[1].children[1], g.players.chance,
              ["Fire", "Misfire"])
g.set_chance_probs(g.root.children[1].children[1].children[1].infoset,
                   [gbt.Rational(1, 5), gbt.Rational(4, 5)])
# Fire: Player 2 shot
g.set_outcome(g.root.children[1].children[1].children[1].children[0], p2_shot)

# Misfire -> Player 1 with 4 chambers remaining
g.append_move(g.root.children[1].children[1].children[1].children[1],
              "Player 1", ["Quit", "Pull"])
g.set_outcome(g.root.children[1].children[1].children[1].children[1].children[0],
              p1_quits)

# Player 1 pulls with 4 chambers -> chance node 1/4
g.append_move(g.root.children[1].children[1].children[1].children[1].children[1],
              g.players.chance, ["Fire", "Misfire"])
g.set_chance_probs(
    g.root.children[1].children[1].children[1].children[1].children[1].infoset,
    [gbt.Rational(1, 4), gbt.Rational(3, 4)])
# Fire: Player 1 shot
g.set_outcome(
    g.root.children[1].children[1].children[1].children[1].children[1].children[0],
    p1_shot)

# Misfire -> Player 2 with 3 chambers remaining
g.append_move(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1],
    "Player 2", ["Quit", "Pull"])
g.set_outcome(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[0],
    p2_quits)

# Player 2 pulls with 3 chambers -> chance node 1/3
g.append_move(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1],
    g.players.chance, ["Fire", "Misfire"])
g.set_chance_probs(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].infoset,
    [gbt.Rational(1, 3), gbt.Rational(2, 3)])
# Fire: Player 2 shot
g.set_outcome(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0],
    p2_shot)

# Misfire -> Player 1 with 2 chambers remaining
g.append_move(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1],
    "Player 1", ["Quit", "Pull"])
g.set_outcome(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0],
    p1_quits)

# Player 1 pulls with 2 chambers -> chance node 1/2
g.append_move(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1],
    g.players.chance, ["Fire", "Misfire"])
g.set_chance_probs(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].infoset,
    [gbt.Rational(1, 2), gbt.Rational(1, 2)])
# Fire: Player 1 shot
g.set_outcome(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0],
    p1_shot)

# Misfire -> Player 2 with 1 chamber remaining
g.append_move(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1],
    "Player 2", ["Quit", "Pull"])
g.set_outcome(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[0],
    p2_quits)

# With 1 chamber left, a pull fires for certain: Pull is a terminal firing outcome
# Set the Pull outcome for Player 2 at remaining == 1 to be P2 shot
g.set_outcome(
    g.root.children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1].children[1],
    p2_shot)

# Save to EFG file
g.to_efg("russian_roulette_6chambers.efg")