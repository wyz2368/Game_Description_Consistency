import pygambit as gbt

# Create new tree game with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating revolver (Russian roulette)")

# Pre-create outcome objects for reuse:
# When current player quits: quitting player 0, other 1
quit_p1 = g.add_outcome([0, 1], label="Player1 quits")
quit_p2 = g.add_outcome([1, 0], label="Player2 quits")
# When current player pulls and is shot: shooter -1, other +1
death_p1 = g.add_outcome([-1, 1], label="Player1 shot")
death_p2 = g.add_outcome([1, -1], label="Player2 shot")

def build(node, current_player_index, remaining):
    """
    Recursively build the game from 'node' where it's the turn of
    player with index current_player_index (0 or 1) and 'remaining'
    chambers remain.
    """
    player_name = g.players[current_player_index]  # string like "Player 1"

    # Append the player's decision: "Pull" or "Quit"
    g.append_move(node, player_name, ["Pull", "Quit"])

    # Children: index 0 -> "Pull", index 1 -> "Quit"
    pull_child = node.children[0]
    quit_child = node.children[1]

    # Set outcome for quitting: quitting player 0, other 1
    if current_player_index == 0:
        g.set_outcome(quit_child, quit_p1)
    else:
        g.set_outcome(quit_child, quit_p2)

    # Handle the Pull branch: chance determines Loaded vs Empty
    # If remaining == 1, only "Loaded" branch should exist (prob 1)
    if remaining == 1:
        # Only "Loaded" action (probability 1)
        g.append_move(pull_child, g.players.chance, ["Loaded"])
        # Set chance probability explicitly to 1
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, 1)])
        loaded_node = pull_child.children[0]
        # Shooter dies
        if current_player_index == 0:
            g.set_outcome(loaded_node, death_p1)
        else:
            g.set_outcome(loaded_node, death_p2)
        # No "Empty" branch to continue
    else:
        # remaining > 1: include both branches with appropriate probabilities
        g.append_move(pull_child, g.players.chance, ["Loaded", "Empty"])
        # Set chance probabilities: Loaded = 1/remaining, Empty = (remaining-1)/remaining
        g.set_chance_probs(
            pull_child.infoset,
            [gbt.Rational(1, remaining), gbt.Rational(remaining - 1, remaining)]
        )
        loaded_node = pull_child.children[0]
        empty_node = pull_child.children[1]

        # Set outcome for loaded -> shooter dies
        if current_player_index == 0:
            g.set_outcome(loaded_node, death_p1)
        else:
            g.set_outcome(loaded_node, death_p2)

        # For empty -> continue with the other player's turn and remaining-1
        next_player = 1 - current_player_index
        build(empty_node, next_player, remaining - 1)

# Build the full tree starting at root, Player 1 to act, 6 chambers
build(g.root, current_player_index=0, remaining=6)

# Save the EFG
g.to_efg("revolver_game.efg")