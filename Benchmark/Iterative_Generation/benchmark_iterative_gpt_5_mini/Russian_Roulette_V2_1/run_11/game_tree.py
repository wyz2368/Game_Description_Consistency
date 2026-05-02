import pygambit as gbt

# Create the game with two players
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating revolver (six chambers)")

# Pre-create common outcomes (payoffs follow player order ["Player 1", "Player 2"])
out_quit_p1 = g.add_outcome([0, 1], label="Player1 quits -> P2 wins")
out_quit_p2 = g.add_outcome([1, 0], label="Player2 quits -> P1 wins")
out_fire_p1 = g.add_outcome([-1, 1], label="Player1 shot -> P2 wins")
out_fire_p2 = g.add_outcome([1, -1], label="Player2 shot -> P1 wins")

def build(node, current_player_index, remaining_chambers):
    """
    Recursively build the tree.
    node: current decision node
    current_player_index: 0 if Player 1 to move, 1 if Player 2 to move
    remaining_chambers: number of chambers not yet pulled (k); fire prob = 1/k
    """
    players = ["Player 1", "Player 2"]
    current_player = players[current_player_index]
    other_player_index = 1 - current_player_index

    # Append the decision move for the current player with actions "Quit" and "Pull"
    g.append_move(node, current_player, ["Quit", "Pull"])

    # Children: node.children[0] -> "Quit", node.children[1] -> "Pull"
    quit_node = node.children[0]
    pull_node = node.children[1]

    # Set terminal outcome for quitting: quitting player gets 0, other gets 1
    if current_player_index == 0:
        g.set_outcome(quit_node, out_quit_p1)
    else:
        g.set_outcome(quit_node, out_quit_p2)

    # For "Pull", append a chance move that realizes "Fire" or "No fire"
    # If remaining_chambers == 1, the fire probability is 1 and there is no "No fire" branch.
    if remaining_chambers == 1:
        # Only "Fire" branch (probability 1)
        g.append_move(pull_node, g.players.chance, ["Fire"])
        # Set chance probability 1
        g.set_chance_probs(pull_node.infoset, [gbt.Rational(1, 1)])
        # Fire outcome: current player shot
        if current_player_index == 0:
            g.set_outcome(pull_node.children[0], out_fire_p1)
        else:
            g.set_outcome(pull_node.children[0], out_fire_p2)
    else:
        # Two chance branches: "Fire" (1/remaining) and "No fire" ((remaining-1)/remaining)
        g.append_move(pull_node, g.players.chance, ["Fire", "No fire"])
        # Set the chance probabilities for this chance node's infoset
        prob_fire = gbt.Rational(1, remaining_chambers)
        prob_no_fire = gbt.Rational(remaining_chambers - 1, remaining_chambers)
        g.set_chance_probs(pull_node.infoset, [prob_fire, prob_no_fire])

        # Set "Fire" terminal outcome
        if current_player_index == 0:
            g.set_outcome(pull_node.children[0], out_fire_p1)
        else:
            g.set_outcome(pull_node.children[0], out_fire_p2)

        # "No fire" leads to the other player's decision with remaining_chambers - 1
        nofire_node = pull_node.children[1]
        build(nofire_node, other_player_index, remaining_chambers - 1)

# Start building from the root: Player 1 acts first, 6 chambers remaining
build(g.root, current_player_index=0, remaining_chambers=6)

# Save the EFG
g.to_efg("revolver_game.efg")