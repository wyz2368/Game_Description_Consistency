import pygambit as gbt

# Create the game with the specified player order
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternation (Russian roulette)")

# Add chance move at the root to choose the loaded chamber (1..6)
chamber_actions = [f"Chamber {i}" for i in range(1, 7)]
g.append_move(g.root, g.players.chance, chamber_actions)

# Set equal probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in chamber_actions])

# Helper recursive builder: builds the alternating decision nodes under a given node
def build_subtree(node, loaded_pos, chamber_idx, current_player_index):
    """
    node: the current node where current_player chooses
    loaded_pos: integer 1..6 specifying which chamber is loaded for this chance branch
    chamber_idx: current chamber index (1..6)
    current_player_index: 0 for Player 1, 1 for Player 2
    """
    # Append the player's decision: Pull or Quit
    player = g.players[current_player_index]
    g.append_move(node, player, ["Pull", "Quit"])
    # children: index 0 -> "Pull", index 1 -> "Quit"
    pull_node = node.children[0]
    quit_node = node.children[1]

    # Set outcome for quitting: quitting player gets 0, other gets 1
    if current_player_index == 0:
        quit_outcome = g.add_outcome([0, 1], label=f"P1 quits at chamber {chamber_idx}")
    else:
        quit_outcome = g.add_outcome([1, 0], label=f"P2 quits at chamber {chamber_idx}")
    g.set_outcome(quit_node, quit_outcome)

    # Handle pulling:
    # If the current chamber is the loaded one, shooter dies (terminal).
    if chamber_idx == loaded_pos:
        if current_player_index == 0:
            shoot_outcome = g.add_outcome([-1, 1], label=f"P1 shot at chamber {chamber_idx}")
        else:
            shoot_outcome = g.add_outcome([1, -1], label=f"P2 shot at chamber {chamber_idx}")
        g.set_outcome(pull_node, shoot_outcome)
    else:
        # Safe pull: continue to next chamber and the other player's turn
        # Only continue if chamber_idx < 6 (should normally be <=5 here if safe)
        if chamber_idx < 6:
            build_subtree(pull_node, loaded_pos, chamber_idx + 1, 1 - current_player_index)
        else:
            # This branch should not happen because loaded_pos is in 1..6,
            # but include a fallback just in case: treat as no-shot (draw -> both 0)
            draw_outcome = g.add_outcome([0, 0], label=f"No shot after chamber {chamber_idx}")
            g.set_outcome(pull_node, draw_outcome)

# Build subtree separately for each chance child (each loaded chamber position)
for i, chance_child in enumerate(g.root.children, start=1):
    # For loaded chamber position i, start at chamber index 1 and Player 1 to move
    build_subtree(chance_child, loaded_pos=i, chamber_idx=1, current_player_index=0)

# Save the EFG
g.to_efg("russian_roulette.efg")