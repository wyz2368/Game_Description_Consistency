import pygambit as gbt

# Create the game with the correct player order
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# Pre-create outcomes to reuse
out_p1_quit = g.add_outcome([0, 1], label="P1 quits (P2 wins)")
out_p2_quit = g.add_outcome([1, 0], label="P2 quits (P1 wins)")
out_p1_dies = g.add_outcome([-1, 1], label="P1 dies (P2 wins)")
out_p2_dies = g.add_outcome([1, -1], label="P2 dies (P1 wins)")

player_names = ["Player 1", "Player 2"]
MAX_CHAMBERS = 6

def build_node(node, current_player_idx, pulls_done):
    """
    Recursively build the game tree from `node` where it's
    player `current_player_idx`'s turn and `pulls_done` pulls
    have already occurred.
    """
    # Append the player's decision move at this node (one node at a time).
    g.append_move(node, player_names[current_player_idx], ["Pull trigger", "Quit"])

    # Children: [0] -> "Pull trigger" branch, [1] -> "Quit" branch
    pull_node = node.children[0]
    quit_node = node.children[1]

    # Set the outcome for quitting: quitting player gets 0, other gets 1
    if current_player_idx == 0:  # Player 1 quits
        g.set_outcome(quit_node, out_p1_quit)
    else:  # Player 2 quits
        g.set_outcome(quit_node, out_p2_quit)

    # Handle the pull trigger branch: chance determines Loaded vs Empty
    remaining = MAX_CHAMBERS - pulls_done
    # remaining should be at least 1
    if remaining <= 0:
        # Defensive: shouldn't happen, but treat as immediate loaded (shooter dies)
        if current_player_idx == 0:
            g.set_outcome(pull_node, out_p1_dies)
        else:
            g.set_outcome(pull_node, out_p2_dies)
        return

    if remaining == 1:
        # Only "Loaded" action (probability 1). Do NOT include an "Empty" branch with 0 probability.
        g.append_move(pull_node, g.players.chance, ["Loaded"])
        # Set chance probability to 1
        g.set_chance_probs(pull_node.infoset, [gbt.Rational(1, 1)])
        # The single child corresponds to the loaded outcome: shooter dies
        loaded_child = pull_node.children[0]
        if current_player_idx == 0:
            g.set_outcome(loaded_child, out_p1_dies)
        else:
            g.set_outcome(loaded_child, out_p2_dies)
    else:
        # Two chance actions: "Loaded" and "Empty"
        g.append_move(pull_node, g.players.chance, ["Loaded", "Empty"])
        total = remaining
        # Probabilities: Loaded = 1/total, Empty = (total-1)/total
        g.set_chance_probs(pull_node.infoset,
                           [gbt.Rational(1, total), gbt.Rational(total - 1, total)])
        # Set outcome for Loaded branch (child 0): shooter dies
        loaded_child = pull_node.children[0]
        if current_player_idx == 0:
            g.set_outcome(loaded_child, out_p1_dies)
        else:
            g.set_outcome(loaded_child, out_p2_dies)
        # Empty branch (child 1): continue with the other player and pulls_done+1
        empty_child = pull_node.children[1]
        next_player_idx = 1 - current_player_idx
        build_node(empty_child, next_player_idx, pulls_done + 1)

# Start building from the root: Player 1 acts first, 0 pulls done
build_node(g.root, current_player_idx=0, pulls_done=0)

# Save to EFG file
g.to_efg("russian_roulette_six_chamber.efg")