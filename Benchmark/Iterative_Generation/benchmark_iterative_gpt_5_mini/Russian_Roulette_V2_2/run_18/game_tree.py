import pygambit as gbt

# Create the game with the specified player order
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating revolver (Russian roulette)")

def expand_decision(node, player_idx, remaining_chambers):
    """
    Expand the decision node where player player_idx acts and there are
    remaining_chambers unpulled chambers.
    """
    player_name = g.players[player_idx]
    # Add the decision: Quit or Pull
    g.append_move(node, player_name, ["Quit", "Pull"])
    # Quit branch: acting player withdraws (0), other player wins (1)
    quit_child = node.children[0]
    if player_idx == 0:
        quit_outcome = g.add_outcome([0, 1], label="Quit")
    else:
        quit_outcome = g.add_outcome([1, 0], label="Quit")
    g.set_outcome(quit_child, quit_outcome)

    # Pull branch: chance determines Fire vs No fire (or only Fire if last chamber)
    pull_child = node.children[1]
    if remaining_chambers == 1:
        chance_actions = ["Fire"]
    else:
        chance_actions = ["Fire", "No fire"]

    g.append_move(pull_child, g.players.chance, chance_actions)

    # Set chance probabilities
    if remaining_chambers == 1:
        probs = [gbt.Rational(1, 1)]
    else:
        probs = [gbt.Rational(1, remaining_chambers),
                 gbt.Rational(remaining_chambers - 1, remaining_chambers)]
    # Use the infoset of the node where we appended the chance move
    g.set_chance_probs(pull_child.infoset, probs)

    # Fire outcome: acting player dies (-1), other wins (+1)
    fire_node = pull_child.children[0]
    if player_idx == 0:
        fire_outcome = g.add_outcome([-1, 1], label="Fire")
    else:
        fire_outcome = g.add_outcome([1, -1], label="Fire")
    g.set_outcome(fire_node, fire_outcome)

    # If there is a "No fire" outcome, continue the game with the other player
    if remaining_chambers > 1:
        nofire_node = pull_child.children[1]
        next_player_idx = 1 - player_idx
        expand_decision(nofire_node, next_player_idx, remaining_chambers - 1)

# Build the tree starting from Player 1 and 6 chambers
expand_decision(g.root, player_idx=0, remaining_chambers=6)

# Save to EFG
g.to_efg("revolver_game.efg")