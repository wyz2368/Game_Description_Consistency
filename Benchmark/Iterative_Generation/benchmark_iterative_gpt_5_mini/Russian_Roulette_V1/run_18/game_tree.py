import pygambit as gbt

# Create game with two players
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian roulette")

# Chance at root: which chamber contains the bullet (1..6)
g.append_move(g.root, g.players.chance, [f"Bullet {i}" for i in range(1, 7)])
# Set equal probabilities 1/6 for each bullet location
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Reusable outcomes (payoffs follow the player order ["Player 1", "Player 2"])
out_p1_quits = g.add_outcome([0, 1], label="Player1 quits")
out_p2_quits = g.add_outcome([1, 0], label="Player2 quits")
out_p1_dies = g.add_outcome([-1, 1], label="Player1 dies")
out_p2_dies = g.add_outcome([1, -1], label="Player2 dies")

# For each possible bullet position (each child of the chance node),
# build the alternating decision sequence until someone quits or the bullet fires.
for bullet_pos, chance_child in enumerate(g.root.children, start=1):
    current_node = chance_child
    current_chamber = 1  # chamber that will be fired on the next "Pull"
    # At most 6 pulls are needed; loop will break when bullet is encountered
    for turn in range(6):
        player_name = "Player 1" if (turn % 2 == 0) else "Player 2"
        # Append move for this specific node (one node at a time)
        g.append_move(current_node, player_name, ["Pull", "Quit"])
        # After append_move, children are created in the order of actions:
        # children[0] corresponds to "Pull", children[1] to "Quit"
        pull_child = current_node.children[0]
        quit_child = current_node.children[1]

        # Set outcome for quitting: quitter gets 0, other gets 1
        if player_name == "Player 1":
            g.set_outcome(quit_child, out_p1_quits)
        else:
            g.set_outcome(quit_child, out_p2_quits)

        # Handle pulling the trigger
        if current_chamber == bullet_pos:
            # The shooter dies on this pull
            if player_name == "Player 1":
                g.set_outcome(pull_child, out_p1_dies)
            else:
                g.set_outcome(pull_child, out_p2_dies)
            break  # terminal for this chance branch
        else:
            # Survivor: continue to the next turn from the pull_child node
            current_node = pull_child
            current_chamber = (current_chamber % 6) + 1

# Save the EFG file
g.to_efg("russian_roulette.efg")