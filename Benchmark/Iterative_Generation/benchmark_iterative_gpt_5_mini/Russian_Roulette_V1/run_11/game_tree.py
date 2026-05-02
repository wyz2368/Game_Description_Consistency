import pygambit as gbt

# Create the game with Player 1 acting first
players = ["Player 1", "Player 2"]
g = gbt.Game.new_tree(players=players, title="Six-chamber alternate Russian roulette")

# Chance move: which chamber (1..6) contains the bullet
chance_actions = [f"Bullet in chamber {i}" for i in range(1, 7)]
g.append_move(g.root, g.players.chance, chance_actions)

# Set equal probabilities 1/6 for each chance outcome
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Pre-create outcomes to reuse (order matches players = ["Player 1", "Player 2"])
p1_dies = g.add_outcome([-1, 1], label="Player 1 dies")
p2_dies = g.add_outcome([1, -1], label="Player 2 dies")
p1_quits = g.add_outcome([0, 1], label="Player 1 quits")
p2_quits = g.add_outcome([1, 0], label="Player 2 quits")

# For each possible bullet location (each child of the chance node), build the alternating decision nodes
# The i-th child corresponds to bullet in chamber (i+1)
for bullet_pos, chance_child in enumerate(g.root.children, start=1):
    current_node = chance_child
    current_player_idx = 0  # 0 -> Player 1, 1 -> Player 2
    current_chamber = 1     # first pull corresponds to chamber 1

    # Continue until the play ends (either a Quit or a Pull that hits the bullet)
    while True:
        # Append a decision for the current player at this node
        g.append_move(current_node, players[current_player_idx], ["Pull trigger", "Quit"])

        pull_child = current_node.children[0]  # child for "Pull trigger"
        quit_child = current_node.children[1]  # child for "Quit"

        # Set outcome for quitting immediately: quitter gets 0, other gets 1
        if current_player_idx == 0:
            # Player 1 quits
            g.set_outcome(quit_child, p1_quits)
        else:
            # Player 2 quits
            g.set_outcome(quit_child, p2_quits)

        # Handle pulling the trigger
        if current_chamber == bullet_pos:
            # Bullet is in the current chamber -> shooter dies -> terminal
            if current_player_idx == 0:
                # Player 1 pulled and dies
                g.set_outcome(pull_child, p1_dies)
            else:
                # Player 2 pulled and dies
                g.set_outcome(pull_child, p2_dies)
            # Game ends for this chance branch
            break
        else:
            # Survived this pull: play continues from the pull_child node,
            # with the other player to act and chamber advanced by 1
            current_node = pull_child
            current_player_idx = 1 - current_player_idx
            current_chamber = current_chamber + 1
            # Wrap chamber after 6 -> but since bullet_pos is in 1..6 and will be reached
            # before infinite loop, wrapping logic is not strictly necessary; keep it correct anyway
            if current_chamber > 6:
                current_chamber = 1

# Save the game to an EFG file
g.to_efg("revolver_game.efg")