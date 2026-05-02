import pygambit as gbt

# Create the game with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian Roulette (alternating turns)")

# Add chance move at root: which chamber (1..6) contains the bullet
g.append_move(g.root, g.players.chance,
              [f"Bullet at chamber {i}" for i in range(1, 7)])
# Set equal probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Pre-create outcomes (payoffs ordered as [Player 1, Player 2])
# Player 1 quits: [0, 1]
out_p1_quit = g.add_outcome([0, 1], label="P1 quits, P2 wins")
# Player 2 quits: [1, 0]
out_p2_quit = g.add_outcome([1, 0], label="P2 quits, P1 wins")
# Player 1 dies (pulled loaded chamber): [-1, 1]
out_p1_die = g.add_outcome([-1, 1], label="P1 dies, P2 wins")
# Player 2 dies (pulled loaded chamber): [1, -1]
out_p2_die = g.add_outcome([1, -1], label="P2 dies, P1 wins")

# For each possible bullet position (chance child), build the turn sequence up to that position.
# Note: g.root.children has 6 nodes corresponding to "Bullet at chamber 1" .. "Bullet at chamber 6".
for b_index, chance_child in enumerate(g.root.children, start=1):
    # b_index is the bullet chamber number (1..6)
    current_node = chance_child
    # Build turns t = 1..b_index
    for t in range(1, b_index + 1):
        # Determine acting player for turn t: Player 1 on odd t, Player 2 on even t
        acting_player = "Player 1" if (t % 2 == 1) else "Player 2"
        # Append the move for the acting player at the current node
        g.append_move(current_node, acting_player, ["Pull the trigger", "Quit"])
        # children[0] corresponds to "Pull the trigger", children[1] to "Quit"
        pull_node = current_node.children[0]
        quit_node = current_node.children[1]

        # Set outcome for quitting: quitter gets 0, other gets 1
        if acting_player == "Player 1":
            # Player 1 quits -> [0, 1]
            g.set_outcome(quit_node, out_p1_quit)
        else:
            # Player 2 quits -> [1, 0]
            g.set_outcome(quit_node, out_p2_quit)

        # If this turn is the bullet turn, pulling leads to death (terminal).
        if t == b_index:
            if acting_player == "Player 1":
                # Player 1 pulls and dies
                g.set_outcome(pull_node, out_p1_die)
            else:
                # Player 2 pulls and dies
                g.set_outcome(pull_node, out_p2_die)
            # No further continuation for this chance branch
            break
        else:
            # Pull is safe this turn; continue from the pull_node to the next turn
            current_node = pull_node

# Save the EFG
g.to_efg("russian_roulette.efg")