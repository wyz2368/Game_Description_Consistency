import pygambit as gbt

# Create game: Player 1 acts first (assumption stated in reasoning)
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver alternating game")

# Chance decides which chamber (1..6) is loaded
chambers = [f"Chamber {i}" for i in range(1, 7)]
g.append_move(g.root, g.players.chance, chambers)
# Set equal probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# For each possible loaded chamber, build the alternating sequence of decisions
for i, chance_child in enumerate(g.root.children):  # i = 0..5 corresponds to loaded chamber L = i+1
    L = i + 1
    curr_node = chance_child
    # Simulate turns t = 1..L (the bullet will occur on turn t == L if pulled)
    for t in range(1, L + 1):
        player_index = (t - 1) % 2  # 0 -> Player 1, 1 -> Player 2
        player = g.players[player_index]
        # Each decision: actions ["Quit", "Pull"]
        g.append_move(curr_node, player, ["Quit", "Pull"])

        # Quit branch: quitting player gets 0, other gets 1
        quit_payoffs = [0, 0]
        quit_payoffs[player_index] = 0
        quit_payoffs[1 - player_index] = 1
        g.set_outcome(curr_node.children[0], g.add_outcome(quit_payoffs,
                                                           label=f"Quit on turn {t}, L={L}"))

        # Pull branch:
        if t == L:
            # Bullet fires: shooter dies -> shooter -1, other +1
            death_payoffs = [0, 0]
            death_payoffs[player_index] = -1
            death_payoffs[1 - player_index] = 1
            g.set_outcome(curr_node.children[1], g.add_outcome(death_payoffs,
                                                               label=f"Death on turn {t}, L={L}"))
            # Terminal after death; no further nodes on this branch
            break
        else:
            # Safe pull: continue to the next turn node (switch player)
            curr_node = curr_node.children[1]

# Save the EFG
g.to_efg("revolver_game.efg")