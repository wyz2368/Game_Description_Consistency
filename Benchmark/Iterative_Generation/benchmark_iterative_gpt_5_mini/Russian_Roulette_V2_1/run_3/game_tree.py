import pygambit as gbt

# Create the game tree with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating revolver: quit or pull (6-chamber)")

def expand(node, remaining_chambers, player_index):
    """
    Expand the node where the player with index player_index chooses between
    "Quit" and "Pull". remaining_chambers is the number of chambers not yet pulled.
    """
    player = g.players[player_index]
    # Add the player's move at this node
    g.append_move(node, player, ["Quit", "Pull"])
    # Children: node.children[0] is Quit child, node.children[1] is Pull child
    quit_child = node.children[0]
    pull_child = node.children[1]

    # Quit outcome: quitting player gets 0, other gets 1
    if player_index == 0:
        quit_outcome = g.add_outcome([0, 1], label="Player 1 quits")
    else:
        quit_outcome = g.add_outcome([1, 0], label="Player 2 quits")
    g.set_outcome(quit_child, quit_outcome)

    # Pull outcome handled by a chance move
    if remaining_chambers == 1:
        # Certain fire: only "Fire" branch with probability 1
        g.append_move(pull_child, g.players.chance, ["Fire"])
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, 1)])
        fire_node = pull_child.children[0]
        # Puller dies: pulling player gets -1, opponent gets 1
        if player_index == 0:
            fire_outcome = g.add_outcome([-1, 1], label="Player 1 shot")
        else:
            fire_outcome = g.add_outcome([1, -1], label="Player 2 shot")
        g.set_outcome(fire_node, fire_outcome)
    else:
        # Two chance outcomes: Fire with prob 1/remaining, Click with prob (remaining-1)/remaining
        g.append_move(pull_child, g.players.chance, ["Fire", "Click"])
        g.set_chance_probs(pull_child.infoset,
                           [gbt.Rational(1, remaining_chambers),
                            gbt.Rational(remaining_chambers - 1, remaining_chambers)])
        fire_node = pull_child.children[0]
        click_node = pull_child.children[1]
        # Fire branch: pulling player dies
        if player_index == 0:
            fire_outcome = g.add_outcome([-1, 1], label="Player 1 shot")
        else:
            fire_outcome = g.add_outcome([1, -1], label="Player 2 shot")
        g.set_outcome(fire_node, fire_outcome)
        # Click branch: game continues with the other player and one fewer chamber
        expand(click_node, remaining_chambers - 1, 1 - player_index)

# Start expanding from the root with 6 chambers remaining and Player 1 to move
expand(g.root, remaining_chambers=6, player_index=0)

# Save the game to an EFG file
g.to_efg("revolver_game.efg")