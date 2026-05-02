import pygambit as gbt

# Create game with Player 1 moving first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver alternating pull-or-quit game")

players = ["Player 1", "Player 2"]

# Pre-create outcome objects for reuse (payoffs are in the same order as players)
# Quit outcomes
quit_p1 = g.add_outcome([0, 1], label="Player1 quits (P1:0, P2:1)")
quit_p2 = g.add_outcome([1, 0], label="Player2 quits (P1:1, P2:0)")
# Death outcomes (acting player dies -> -1 for actor, +1 for other)
death_p1 = g.add_outcome([-1, 1], label="Player1 dies (P1:-1, P2:1)")
death_p2 = g.add_outcome([1, -1], label="Player2 dies (P1:1, P2:-1)")

def build(node, player_idx, remaining_chambers):
    """
    Recursively build the game tree from node where it's players[player_idx]'s turn
    and remaining_chambers chambers remain in the revolver.
    """
    player_name = players[player_idx]
    # Decision: Quit or Pull trigger
    g.append_move(node, player_name, ["Quit", "Pull trigger"])
    # children: [Quit_node, Pull_node]
    quit_node = node.children[0]
    pull_node = node.children[1]

    # Set outcome for quitting
    if player_idx == 0:
        g.set_outcome(quit_node, quit_p1)
    else:
        g.set_outcome(quit_node, quit_p2)

    # Handle pulling the trigger
    if remaining_chambers == 1:
        # Certain fire -> acting player dies
        if player_idx == 0:
            g.set_outcome(pull_node, death_p1)
        else:
            g.set_outcome(pull_node, death_p2)
    else:
        # Chance determines whether it fires: probability 1/remaining_chambers to fire
        g.append_move(pull_node, g.players.chance, ["Fire", "No fire"])
        # Set chance probabilities: Fire = 1/remaining, No fire = (remaining-1)/remaining
        g.set_chance_probs(pull_node.infoset, [
            gbt.Rational(1, remaining_chambers),
            gbt.Rational(remaining_chambers - 1, remaining_chambers)
        ])
        # Chance children: [Fire_node, NoFire_node]
        fire_node = pull_node.children[0]
        nofire_node = pull_node.children[1]

        # Fire -> acting player dies (terminal)
        if player_idx == 0:
            g.set_outcome(fire_node, death_p1)
        else:
            g.set_outcome(fire_node, death_p2)

        # No fire -> pass to the other player with one fewer chamber
        build(nofire_node, 1 - player_idx, remaining_chambers - 1)

# Build the tree starting from the root: Player 1, 6 chambers
build(g.root, player_idx=0, remaining_chambers=6)

# Save the EFG file
g.to_efg("revolver_game.efg")