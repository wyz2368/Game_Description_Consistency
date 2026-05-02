import pygambit as gbt

# Create the game with Player 1 going first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Russian roulette (6-chamber), alternating turns")

def build_node(node, current_player_index, chambers_remaining):
    """
    Build the decision node for the current player with chambers_remaining chambers left.
    node: a Node in the pygambit tree
    current_player_index: 0 for Player 1, 1 for Player 2
    chambers_remaining: integer >= 1
    """
    player_name = g.players[current_player_index]
    # Add the player's decision: Quit or Pull
    g.append_move(node, player_name, ["Quit", "Pull"])

    # Child 0: Quit -> terminal, quitting player gets 0, other gets +1
    quit_child = node.children[0]
    if current_player_index == 0:
        # Player 1 quits -> [0, 1]
        quit_outcome = g.add_outcome([0, 1], label=f"P1 quits (r={chambers_remaining})")
    else:
        # Player 2 quits -> [1, 0]
        quit_outcome = g.add_outcome([1, 0], label=f"P2 quits (r={chambers_remaining})")
    g.set_outcome(quit_child, quit_outcome)

    # Child 1: Pull
    pull_child = node.children[1]
    # If only one chamber remains, pulling fires for certain -> acting player shot
    if chambers_remaining == 1:
        if current_player_index == 0:
            shot_outcome = g.add_outcome([-1, 1], label="P1 shot (r=1)")
        else:
            shot_outcome = g.add_outcome([1, -1], label="P2 shot (r=1)")
        g.set_outcome(pull_child, shot_outcome)
    else:
        # Add a chance node for the pull: Fire with prob 1/r, No fire with prob (r-1)/r
        g.append_move(pull_child, g.players.chance, ["Fire", "No fire"])
        # Set chance probabilities
        r = chambers_remaining
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, r), gbt.Rational(r - 1, r)])
        # Chance child 0: Fire -> acting player is shot (terminal)
        fire_child = pull_child.children[0]
        if current_player_index == 0:
            fire_outcome = g.add_outcome([-1, 1], label=f"P1 shot (r={r})")
        else:
            fire_outcome = g.add_outcome([1, -1], label=f"P2 shot (r={r})")
        g.set_outcome(fire_child, fire_outcome)
        # Chance child 1: No fire -> pass to other player with r-1 chambers
        nofire_child = pull_child.children[1]
        # Recursively build the next decision node for the other player
        build_node(nofire_child, 1 - current_player_index, chambers_remaining - 1)

# Start building from the root: Player 1, 6 chambers
build_node(g.root, current_player_index=0, chambers_remaining=6)

# Save the EFG
g.to_efg("russian_roulette.efg")