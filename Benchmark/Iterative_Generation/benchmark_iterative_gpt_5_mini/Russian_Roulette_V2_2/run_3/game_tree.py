import pygambit as gbt

# Create the game with explicit player order
players = ["Player 1", "Player 2"]
g = gbt.Game.new_tree(players=players, title="Six-chamber alternating Russian roulette")

# Pre-create outcomes (payoffs correspond to [Player 1, Player 2])
p1_quits = g.add_outcome([0, 1], label="Player 1 quits")
p2_quits = g.add_outcome([1, 0], label="Player 2 quits")
p1_dies = g.add_outcome([-1, 1], label="Player 1 dies")
p2_dies = g.add_outcome([1, -1], label="Player 2 dies")

def build(node, current_player_index, chambers):
    """
    Expand the game tree from node where it's current_player_index's turn
    and `chambers` chambers remain in the cylinder.
    """
    current_player_name = players[current_player_index]
    # Add the player's decision: Quit or Pull
    g.append_move(node, current_player_name, ["Quit", "Pull"])
    quit_child = node.children[0]
    pull_child = node.children[1]

    # Set the outcome for quitting
    if current_player_index == 0:
        g.set_outcome(quit_child, p1_quits)
    else:
        g.set_outcome(quit_child, p2_quits)

    # Handle pulling the trigger
    if chambers == 1:
        # Certain fire: acting player dies
        if current_player_index == 0:
            g.set_outcome(pull_child, p1_dies)
        else:
            g.set_outcome(pull_child, p2_dies)
    else:
        # Chance node for Fire vs Misfire
        g.append_move(pull_child, g.players.chance, ["Fire", "Misfire"])
        # Set probabilities: Fire with probability 1/chambers, Misfire with (chambers-1)/chambers
        g.set_chance_probs(
            pull_child.infoset,
            [gbt.Rational(1, chambers), gbt.Rational(chambers - 1, chambers)]
        )
        fire_child = pull_child.children[0]
        misfire_child = pull_child.children[1]

        # Fire outcome: acting player dies
        if current_player_index == 0:
            g.set_outcome(fire_child, p1_dies)
        else:
            g.set_outcome(fire_child, p2_dies)

        # Misfire: play continues with the other player and one fewer chamber
        next_player_index = 1 - current_player_index
        build(misfire_child, next_player_index, chambers - 1)

# Build the tree starting from the root: Player 1 starts, 6 chambers
build(g.root, current_player_index=0, chambers=6)

# Save to EFG file
g.to_efg("russian_roulette.efg")