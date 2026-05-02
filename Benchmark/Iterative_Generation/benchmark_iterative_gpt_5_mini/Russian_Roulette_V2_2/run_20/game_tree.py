import pygambit as gbt

# Create game with the two players in order
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian roulette")

# Pre-create outcome objects (payoff order matches ["Player 1", "Player 2"])
p1_quits = g.add_outcome([0, 1], label="P1 quits")
p2_quits = g.add_outcome([1, 0], label="P2 quits")
p1_shot = g.add_outcome([-1, 1], label="P1 shot")
p2_shot = g.add_outcome([1, -1], label="P2 shot")

players = ["Player 1", "Player 2"]

def build(node, current_player_index, remaining_chambers):
    """
    Build the subtree for 'node' where players[current_player_index] acts
    and there are remaining_chambers chambers in the cylinder.
    """
    player_name = players[current_player_index]
    # Add the player's decision: Quit or Pull
    g.append_move(node, player_name, ["Quit", "Pull"])
    # The Quit child is node.children[0]
    if current_player_index == 0:
        g.set_outcome(node.children[0], p1_quits)  # Player 1 quits -> [0,1]
    else:
        g.set_outcome(node.children[0], p2_quits)  # Player 2 quits -> [1,0]

    # The Pull child is node.children[1]
    pull_child = node.children[1]

    if remaining_chambers == 1:
        # Last chamber: pulling fires for certain -> shooter dies
        if current_player_index == 0:
            g.set_outcome(pull_child, p1_shot)
        else:
            g.set_outcome(pull_child, p2_shot)
    else:
        # More than one chamber remains: chance determines Fire vs Click
        g.append_move(pull_child, g.players.chance, ["Fire", "Click"])
        k = remaining_chambers
        # Set chance probabilities: Fire with 1/k, Click with (k-1)/k
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, k), gbt.Rational(k - 1, k)])
        # Fire branch is pull_child.children[0]
        if current_player_index == 0:
            g.set_outcome(pull_child.children[0], p1_shot)
        else:
            g.set_outcome(pull_child.children[0], p2_shot)
        # Click branch continues the game with other player and one fewer chamber
        next_node = pull_child.children[1]
        build(next_node, 1 - current_player_index, remaining_chambers - 1)

# Build the game starting from the root: Player 1 acts first, 6 chambers
build(g.root, current_player_index=0, remaining_chambers=6)

# Save the EFG
g.to_efg("revolver_game.efg")