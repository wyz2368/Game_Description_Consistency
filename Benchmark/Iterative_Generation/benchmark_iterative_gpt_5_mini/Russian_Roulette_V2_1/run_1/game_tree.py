import pygambit as gbt

# Create game with the required player order
players = ["Player 1", "Player 2"]
g = gbt.Game.new_tree(players=players, title="Six-chamber Russian Roulette")

# Predefine reusable outcomes (payoff order matches players list above)
p1_quits = g.add_outcome([0, 1], label="Player 1 quits")
p2_quits = g.add_outcome([1, 0], label="Player 2 quits")
p1_dies = g.add_outcome([-1, 1], label="Player 1 dies")
p2_dies = g.add_outcome([1, -1], label="Player 2 dies")

def expand(node, current_idx, remaining_chambers):
    """
    Expand the decision node for the player with index current_idx
    and given number of remaining chambers.
    """
    current_player = players[current_idx]
    other_idx = 1 - current_idx

    # Add the decision: Quit or Pull
    g.append_move(node, current_player, ["Quit", "Pull"])
    # children: [Quit child, Pull child]
    quit_node = node.children[0]
    pull_node = node.children[1]

    # Set outcome for quitting: quitting player gets 0, other gets 1
    if current_idx == 0:
        g.set_outcome(quit_node, p1_quits)
    else:
        g.set_outcome(quit_node, p2_quits)

    # Add chance move for the pull action
    # When remaining_chambers == 1, only the "Loaded" action exists (prob 1)
    if remaining_chambers == 1:
        chance_actions = ["Loaded"]
        g.append_move(pull_node, g.players.chance, chance_actions)
        # probability 1 for Loaded
        g.set_chance_probs(pull_node.infoset, [gbt.Rational(1, 1)])
        loaded_child = pull_node.children[0]
        # The pulling player dies
        g.set_outcome(loaded_child, p1_dies if current_idx == 0 else p2_dies)
    else:
        chance_actions = ["Loaded", "Empty"]
        g.append_move(pull_node, g.players.chance, chance_actions)
        # Set probabilities: Loaded = 1/remaining, Empty = (remaining-1)/remaining
        g.set_chance_probs(
            pull_node.infoset,
            [gbt.Rational(1, remaining_chambers), gbt.Rational(remaining_chambers - 1, remaining_chambers)]
        )
        loaded_child = pull_node.children[0]
        empty_child = pull_node.children[1]

        # Loaded => pulling player dies
        g.set_outcome(loaded_child, p1_dies if current_idx == 0 else p2_dies)

        # Empty => continue with other player and remaining_chambers - 1
        expand(empty_child, other_idx, remaining_chambers - 1)

# Start recursion from root: Player 1, 6 chambers
expand(g.root, current_idx=0, remaining_chambers=6)

# Save the EFG
g.to_efg("russian_roulette_six_chamber.efg")