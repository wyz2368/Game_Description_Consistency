import pygambit as gbt

# Create game with Player 1 moving first
players = ["Player 1", "Player 2"]
g = gbt.Game.new_tree(players=players, title="Sequential revolver (6-chamber)")

# Pre-create outcome objects (payoffs are [Player 1, Player 2])
out_quit_p1 = g.add_outcome([0, 1], label="Player1 quits -> Player2 wins")
out_quit_p2 = g.add_outcome([1, 0], label="Player2 quits -> Player1 wins")
out_die_p1 = g.add_outcome([-1, 1], label="Player1 shot")
out_die_p2 = g.add_outcome([1, -1], label="Player2 shot")

def build(node, player_idx, remaining_chambers):
    """
    Expand the tree at 'node' for the player with index player_idx (0 or 1)
    and with remaining_chambers unpulled chambers.
    """
    # Append decision for the current player: Quit or Pull
    g.append_move(node, players[player_idx], ["Quit", "Pull"])

    # Quit branch (child 0) -> terminal: quitting player gets 0, other gets 1
    quit_child = node.children[0]
    if player_idx == 0:
        g.set_outcome(quit_child, out_quit_p1)
    else:
        g.set_outcome(quit_child, out_quit_p2)

    # Pull branch (child 1)
    pull_child = node.children[1]
    if remaining_chambers == 1:
        # Certain fire -> acting player dies (terminal)
        if player_idx == 0:
            g.set_outcome(pull_child, out_die_p1)
        else:
            g.set_outcome(pull_child, out_die_p2)
    else:
        # Chance determines fire vs no fire
        g.append_move(pull_child, g.players.chance, ["Fire", "No fire"])
        # Set probabilities: Fire = 1/remaining, No fire = (remaining-1)/remaining
        g.set_chance_probs(
            pull_child.infoset,
            [gbt.Rational(1, remaining_chambers), gbt.Rational(remaining_chambers - 1, remaining_chambers)]
        )

        # Fire branch -> terminal (acting player dies)
        fire_node = pull_child.children[0]
        if player_idx == 0:
            g.set_outcome(fire_node, out_die_p1)
        else:
            g.set_outcome(fire_node, out_die_p2)

        # No fire branch -> continue with other player and one fewer chamber
        nofire_node = pull_child.children[1]
        build(nofire_node, 1 - player_idx, remaining_chambers - 1)

# Build the game starting with Player 1 and 6 chambers
build(g.root, player_idx=0, remaining_chambers=6)

# Save the EFG
g.to_efg("revolver_game.efg")