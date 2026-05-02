import pygambit as gbt

# Create game with two players
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver (Russian roulette)")

# Chance picks which chamber (1..6) contains the bullet
g.append_move(g.root, g.players.chance, [f"Chamber {i+1}" for i in range(6)])
# Set equal probability 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Pre-create outcome objects (payoffs ordered as [Player 1, Player 2])
p1_shot = g.add_outcome([-1, 1], label="Player 1 shot himself")
p2_shot = g.add_outcome([1, -1], label="Player 2 shot himself")
p1_quit = g.add_outcome([0, 1], label="Player 1 quit (Player 2 wins)")
p2_quit = g.add_outcome([1, 0], label="Player 2 quit (Player 1 wins)")

# For each possible bullet position (0..5), build the continuation tree
for bullet_pos in range(6):
    node = g.root.children[bullet_pos]  # the node after chance chooses this chamber
    turn = 0  # turn counter; current chamber index = turn % 6
    while True:
        current_player_idx = turn % 2
        current_player_name = g.players[current_player_idx]
        # Append decision node for the current player with actions "Quit" and "Pull"
        g.append_move(node, current_player_name, ["Quit", "Pull"])

        # Quit branch: immediate terminal. Assign outcome depending on who quit.
        quit_child = node.children[0]
        if current_player_idx == 0:  # Player 1 quit
            g.set_outcome(quit_child, p1_quit)
        else:  # Player 2 quit
            g.set_outcome(quit_child, p2_quit)

        # Pull branch: either shooter dies (if current chamber == bullet_pos) or continue
        pull_child = node.children[1]
        if (turn % 6) == bullet_pos:
            # Shooter dies on this pull
            if current_player_idx == 0:
                g.set_outcome(pull_child, p1_shot)
            else:
                g.set_outcome(pull_child, p2_shot)
            break  # this branch terminates; move to next chance branch
        else:
            # Safe pull: continue from pull_child for the next turn
            node = pull_child
            turn += 1
            # continue loop until we hit the bullet and set an outcome

# Save the EFG
g.to_efg("six_chamber_revolver.efg")