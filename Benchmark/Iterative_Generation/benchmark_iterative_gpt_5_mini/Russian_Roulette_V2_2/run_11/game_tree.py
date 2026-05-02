import pygambit as gbt

# Create game: Player 1 starts
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# Pre-create and reuse outcome objects (payoffs in order [Player 1, Player 2])
p1_quits = g.add_outcome([0, 1], label="Player 1 quits")
p2_quits = g.add_outcome([1, 0], label="Player 2 quits")
p1_shoots = g.add_outcome([-1, 1], label="Player 1 shot")
p2_shoots = g.add_outcome([1, -1], label="Player 2 shot")

def expand(node, current_player_index, remaining_chambers):
    """
    Expand the game tree at `node` for the current player (index) with
    `remaining_chambers` unpulled chambers.
    """
    current_player = g.players[current_player_index]  # e.g., "Player 1" or "Player 2"
    other_player_index = 1 - current_player_index

    # Add the player's decision: Quit or Pull trigger
    g.append_move(node, current_player, ["Quit", "Pull trigger"])

    # Child 0: Quit -> terminal: quitting player gets 0, other gets +1
    quit_child = node.children[0]
    if current_player_index == 0:
        g.set_outcome(quit_child, p1_quits)
    else:
        g.set_outcome(quit_child, p2_quits)

    # Child 1: Pull trigger
    pull_child = node.children[1]

    if remaining_chambers == 1:
        # Certain fire: acting player dies immediately
        if current_player_index == 0:
            g.set_outcome(pull_child, p1_shoots)
        else:
            g.set_outcome(pull_child, p2_shoots)
    else:
        # Chance determines Fire (1/k) or Safe ((k-1)/k)
        k = remaining_chambers
        g.append_move(pull_child, g.players.chance, ["Fire", "Safe"])
        # Set probabilities for this specific chance infoset
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, k), gbt.Rational(k - 1, k)])

        # Fire child (index 0): acting player dies
        fire_child = pull_child.children[0]
        if current_player_index == 0:
            g.set_outcome(fire_child, p1_shoots)
        else:
            g.set_outcome(fire_child, p2_shoots)

        # Safe child (index 1): proceed with other player's turn and k-1 chambers remaining
        safe_child = pull_child.children[1]
        expand(safe_child, other_player_index, remaining_chambers - 1)

# Start expansion from the root with Player 1 and 6 chambers
expand(g.root, current_player_index=0, remaining_chambers=6)

# Save the EFG
g.to_efg("russian_roulette.efg")