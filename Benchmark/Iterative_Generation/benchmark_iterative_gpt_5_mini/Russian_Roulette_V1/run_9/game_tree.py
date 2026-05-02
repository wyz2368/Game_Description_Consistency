import pygambit as gbt

# Create the game tree with two players; Player 1 acts first (assumption).
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver (Russian roulette)")

# Add chance move at the root: which chamber contains the bullet (1..6)
chance_actions = [f"Bullet at {i}" for i in range(1, 7)]
g.append_move(g.root, g.players.chance, chance_actions)

# Set equal probabilities 1/6 for each chance outcome
probabilities = [gbt.Rational(1, 6) for _ in range(6)]
g.set_chance_probs(g.root.infoset, probabilities)

# Pre-create outcome objects for reuse (payoffs follow player order [Player 1, Player 2])
out_quit_p1 = g.add_outcome([0, 1], label="Player 1 quits")
out_quit_p2 = g.add_outcome([1, 0], label="Player 2 quits")
out_p1_dies  = g.add_outcome([-1, 1], label="Player 1 dies")
out_p2_dies  = g.add_outcome([1, -1], label="Player 2 dies")

# For each possible bullet position, build the deterministic subtree.
# Root's children correspond to the chance actions in order.
for bullet_pos in range(1, 7):
    # The child node corresponding to "Bullet at bullet_pos"
    current_node = g.root.children[bullet_pos - 1]
    # Player 1 starts
    current_player_idx = 0  # 0 for Player 1, 1 for Player 2

    # There will be at most 6 pulls; iterate pull_number = 1..6
    for pull_number in range(1, 7):
        player_name = "Player 1" if current_player_idx == 0 else "Player 2"

        # Add the decision node for the current player with actions Quit or Pull
        g.append_move(current_node, player_name, ["Quit", "Pull"])

        # The children are created in the order of actions: 0 -> Quit, 1 -> Pull
        quit_child = current_node.children[0]
        pull_child = current_node.children[1]

        # Set outcome for quitting: quitter gets 0, opponent gets 1
        if current_player_idx == 0:
            g.set_outcome(quit_child, out_quit_p1)
        else:
            g.set_outcome(quit_child, out_quit_p2)

        # If pulling would hit the bullet at this pull_number, shooter dies and branch ends
        if pull_number == bullet_pos:
            if current_player_idx == 0:
                # Player 1 pulls and dies
                g.set_outcome(pull_child, out_p1_dies)
            else:
                # Player 2 pulls and dies
                g.set_outcome(pull_child, out_p2_dies)
            # This branch ends; break out of the pull loop for this chance outcome
            break
        else:
            # Pull was safe; continue from the pull_child as the next decision node for the other player
            current_node = pull_child
            current_player_idx = 1 - current_player_idx

# Save the EFG
g.to_efg("revolver_game.efg")