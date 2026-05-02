import pygambit as gbt

# Create the game with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver (alternating pulls)")

players = ["Player 1", "Player 2"]
MAX_CHAMBERS = 6

def build(node, current_idx, pulls_done):
    """
    Recursively build the game tree.
    node: current terminal node where the player chooses
    current_idx: 0 for Player 1, 1 for Player 2
    pulls_done: how many empty chambers have already been tested (0..5)
    """
    # Append the decision for the current player at this node
    g.append_move(node, players[current_idx], ["Quit", "Pull"])

    # The "Quit" child is the first child (index 0)
    quit_child = node.children[0]
    if current_idx == 0:
        # Player 1 quits -> Player 1 gets 0, Player 2 gets 1
        g.set_outcome(quit_child, g.add_outcome([0, 1], label="Quit"))
    else:
        # Player 2 quits -> Player 1 gets 1, Player 2 gets 0
        g.set_outcome(quit_child, g.add_outcome([1, 0], label="Quit"))

    # The "Pull" child is the second child (index 1)
    pull_child = node.children[1]

    remaining = MAX_CHAMBERS - pulls_done  # number of chambers not yet tested

    # Append chance move at the pull child
    if remaining == 1:
        # Guaranteed fire: only a "Fire" action (do not include zero-prob actions)
        g.append_move(pull_child, g.players.chance, ["Fire"])
        # Set deterministic probability 1 for the sole chance action
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, 1)])

        # Terminal: shooter dies
        fire_node = pull_child.children[0]
        if current_idx == 0:
            g.set_outcome(fire_node, g.add_outcome([-1, 1], label="Fire - shooter dies"))
        else:
            g.set_outcome(fire_node, g.add_outcome([1, -1], label="Fire - shooter dies"))

    else:
        # There is a positive probability of "Fire" and "No fire"
        g.append_move(pull_child, g.players.chance, ["Fire", "No fire"])
        # Set rational probabilities 1/remaining and (remaining-1)/remaining
        g.set_chance_probs(pull_child.infoset,
                           [gbt.Rational(1, remaining),
                            gbt.Rational(remaining - 1, remaining)])

        # "Fire" branch: terminal, shooter dies
        fire_node = pull_child.children[0]
        if current_idx == 0:
            g.set_outcome(fire_node, g.add_outcome([-1, 1], label="Fire - shooter dies"))
        else:
            g.set_outcome(fire_node, g.add_outcome([1, -1], label="Fire - shooter dies"))

        # "No fire" branch: continue the game with the other player
        no_fire_node = pull_child.children[1]
        # Recurse: next player, one more chamber tested
        build(no_fire_node, 1 - current_idx, pulls_done + 1)


# Build the tree starting from the root (Player 1, 0 pulls done)
build(g.root, current_idx=0, pulls_done=0)

# Save the EFG
g.to_efg("revolver_game.efg")