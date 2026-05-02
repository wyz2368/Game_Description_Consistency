import pygambit as gbt

# Create the game with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating revolver (Russian roulette)")

# Pre-create outcome objects (payoffs follow the player order: [Player 1, Player 2])
p1_quit = g.add_outcome([0, 1], label="P1 quits")
p2_quit = g.add_outcome([1, 0], label="P2 quits")
p1_shot = g.add_outcome([-1, 1], label="P1 shot")
p2_shot = g.add_outcome([1, -1], label="P2 shot")

player_names = ["Player 1", "Player 2"]

def expand_decision(node, current_player_index, remaining_chambers):
    """
    Expand the decision node for the given player with the given number of remaining chambers.
    node: Node where to append the player's move.
    current_player_index: 0 for Player 1, 1 for Player 2.
    remaining_chambers: number of chambers not yet pulled (1..6).
    """
    player_name = player_names[current_player_index]
    # Add the player's decision: Quit or Pull
    g.append_move(node, player_name, ["Quit", "Pull"])
    # Set the Quit outcome (child 0)
    if current_player_index == 0:
        g.set_outcome(node.children[0], p1_quit)
    else:
        g.set_outcome(node.children[0], p2_quit)

    # Handle the Pull branch (child 1)
    pull_node = node.children[1]

    # Determine chance actions and probabilities depending on remaining_chambers
    if remaining_chambers == 1:
        chance_actions = ["Fire"]  # must fire
        probs = [gbt.Rational(1, 1)]
    else:
        chance_actions = ["Fire", "Blank"]
        probs = [gbt.Rational(1, remaining_chambers),
                 gbt.Rational(remaining_chambers - 1, remaining_chambers)]

    # Append the chance move at the pull node
    g.append_move(pull_node, g.players.chance, chance_actions)
    # Set chance probabilities on the chance node's infoset
    g.set_chance_probs(pull_node.infoset, probs)

    # Set the Fire outcome (child 0 of the chance node)
    if current_player_index == 0:
        g.set_outcome(pull_node.children[0], p1_shot)
    else:
        g.set_outcome(pull_node.children[0], p2_shot)

    # If there is a Blank branch, continue the game with the other player and one fewer chamber
    if remaining_chambers > 1:
        next_node = pull_node.children[1]
        expand_decision(next_node, 1 - current_player_index, remaining_chambers - 1)

# Start expansion from the root: Player 1 acts first, 6 chambers remaining
expand_decision(g.root, current_player_index=0, remaining_chambers=6)

# Save the EFG
g.to_efg("revolver_game.efg")