import pygambit as gbt

# Create the game tree with Player 1 moving first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Sequential 6-chamber revolver (Russian roulette)")

# Pre-create outcome objects (ensure ordering matches players=["Player 1","Player 2"])
p1_shot = g.add_outcome([-1, 1], label="Player 1 dies")
p2_shot = g.add_outcome([1, -1], label="Player 2 dies")
p1_quits = g.add_outcome([0, 1], label="Player 1 quits")
p2_quits = g.add_outcome([1, 0], label="Player 2 quits")

def build_subtree(node, current_player_idx, remaining_chambers):
    """
    Build the subtree rooted at `node` where it's current_player_idx's turn
    and `remaining_chambers` chambers remain (>=1).
    """
    # Decision actions for the current player
    actions = ["Pull", "Quit"]
    g.append_move(node, g.players[current_player_idx], actions)

    # Locate children for the player's actions
    pull_child = node.children[0]   # child corresponding to "Pull"
    quit_child = node.children[1]   # child corresponding to "Quit"

    # Set the outcome for quitting: quitting player gets 0, other gets 1
    if current_player_idx == 0:
        g.set_outcome(quit_child, p1_quits)
    else:
        g.set_outcome(quit_child, p2_quits)

    # Handle the Pull action: append a chance move at the pull_child
    if remaining_chambers == 1:
        chance_actions = ["Fire"]
        g.append_move(pull_child, g.players.chance, chance_actions)
        # certain fire
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, 1)])
        # The only child is the "Fire" outcome: shooter dies
        fire_child = pull_child.children[0]
        if current_player_idx == 0:
            g.set_outcome(fire_child, p1_shot)
        else:
            g.set_outcome(fire_child, p2_shot)
    else:
        chance_actions = ["Fire", "Click"]
        g.append_move(pull_child, g.players.chance, chance_actions)
        # Fire prob = 1 / remaining_chambers, Click prob = (remaining_chambers - 1) / remaining_chambers
        g.set_chance_probs(pull_child.infoset, [
            gbt.Rational(1, remaining_chambers),
            gbt.Rational(remaining_chambers - 1, remaining_chambers)
        ])
        # Fire branch -> terminal: shooter dies
        fire_child = pull_child.children[0]
        if current_player_idx == 0:
            g.set_outcome(fire_child, p1_shot)
        else:
            g.set_outcome(fire_child, p2_shot)
        # Click branch -> continue with other player and one fewer chamber
        click_child = pull_child.children[1]
        next_player_idx = 1 - current_player_idx
        build_subtree(click_child, next_player_idx, remaining_chambers - 1)

# Build the entire tree starting from root with Player 1 and 6 chambers
build_subtree(g.root, current_player_idx=0, remaining_chambers=6)

# Save the EFG
g.to_efg("revolver_game.efg")