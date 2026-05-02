import pygambit as gbt

# Create the game with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver (Russian roulette)")

# Pre-create common outcomes (payoffs follow [Player 1, Player 2])
p1_quits = g.add_outcome([0, 1], label="P1 quits")
p1_shot  = g.add_outcome([-1, 1], label="P1 shot")
p2_quits = g.add_outcome([1, 0], label="P2 quits")
p2_shot  = g.add_outcome([1, -1], label="P2 shot")

def build(node, current_player_index, remaining_chambers):
    """
    Recursively expand the game tree from `node`.
    current_player_index: 0 for Player 1, 1 for Player 2
    remaining_chambers: integer >= 1
    """
    # Name of the current player as a string (append_move accepts player name)
    player_name = f"Player {current_player_index + 1}"

    # Add the decision for the current player: Quit or Pull trigger
    g.append_move(node, player_name, ["Quit", "Pull trigger"])

    # Quit branch (child 0): terminal outcome
    quit_child = node.children[0]
    if current_player_index == 0:
        g.set_outcome(quit_child, p1_quits)
    else:
        g.set_outcome(quit_child, p2_quits)

    # Pull trigger branch (child 1): leads to a chance node
    pull_child = node.children[1]

    if remaining_chambers > 1:
        # Two possible chance outcomes: Fires (prob 1/remaining) or Doesn't fire (prob (remaining-1)/remaining)
        g.append_move(pull_child, g.players.chance, ["Fires", "Doesn't fire"])
        g.set_chance_probs(pull_child.infoset,
                           [gbt.Rational(1, remaining_chambers),
                            gbt.Rational(remaining_chambers - 1, remaining_chambers)])
        # Fires -> terminal
        fire_child = pull_child.children[0]
        if current_player_index == 0:
            g.set_outcome(fire_child, p1_shot)
        else:
            g.set_outcome(fire_child, p2_shot)
        # Doesn't fire -> continue with other player and one fewer chamber
        nofire_child = pull_child.children[1]
        build(nofire_child, 1 - current_player_index, remaining_chambers - 1)
    else:
        # remaining_chambers == 1: pulling the trigger fires for certain
        g.append_move(pull_child, g.players.chance, ["Fires"])
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, 1)])
        fire_child = pull_child.children[0]
        if current_player_index == 0:
            g.set_outcome(fire_child, p1_shot)
        else:
            g.set_outcome(fire_child, p2_shot)

# Build the tree starting with Player 1 and 6 chambers
build(g.root, current_player_index=0, remaining_chambers=6)

# Save the EFG
g.to_efg("revolver_game.efg")