import pygambit as gbt

# Create the game with the given player order
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian roulette, alternating players")

# Pre-create outcome objects for the recurring terminal payoff patterns
# Format is [payoff for Player 1, payoff for Player 2]
quit_p1 = g.add_outcome([0, 1], label="Player 1 quits -> Player 2 wins")
quit_p2 = g.add_outcome([1, 0], label="Player 2 quits -> Player 1 wins")
fire_p1 = g.add_outcome([-1, 1], label="Player 1 shot (dies)")
fire_p2 = g.add_outcome([1, -1], label="Player 2 shot (dies)")

def expand(node, current_player, remaining_chambers):
    """
    Recursively expand the game tree from 'node' where it's 'current_player''s turn
    and 'remaining_chambers' chambers remain unpulled.
    current_player: 0 for Player 1, 1 for Player 2
    """
    player_name = f"Player {current_player + 1}"
    # Add decision for the current player: Quit or Pull
    g.append_move(node, player_name, ["Quit", "Pull"])
    # After append_move, node.children[0] is the "Quit" terminal node,
    # node.children[1] is the "Pull" branch (which may lead to chance or terminal)
    quit_node = node.children[0]
    pull_node = node.children[1]

    # Set outcome for quitting: quitter gets 0, other gets 1
    if current_player == 0:
        g.set_outcome(quit_node, quit_p1)
    else:
        g.set_outcome(quit_node, quit_p2)

    # Handle the Pull branch
    if remaining_chambers == 1:
        # Certain fire: acting player dies
        if current_player == 0:
            g.set_outcome(pull_node, fire_p1)
        else:
            g.set_outcome(pull_node, fire_p2)
    else:
        # Chance determines whether the gun fires (prob 1/remaining_chambers)
        # or clicks (prob (remaining_chambers-1)/remaining_chambers)
        g.append_move(pull_node, g.players.chance, ["Fire", "No fire"])
        chance_node = pull_node.children[0]
        # Set chance probabilities
        g.set_chance_probs(chance_node.infoset,
                           [gbt.Rational(1, remaining_chambers),
                            gbt.Rational(remaining_chambers - 1, remaining_chambers)])
        # Fire branch: terminal, acting player dies
        fire_terminal = chance_node.children[0]
        if current_player == 0:
            g.set_outcome(fire_terminal, fire_p1)
        else:
            g.set_outcome(fire_terminal, fire_p2)
        # No fire branch: game continues, other player moves, remaining_chambers - 1
        nofire_node = chance_node.children[1]
        next_player = 1 - current_player
        expand(nofire_node, next_player, remaining_chambers - 1)

# Build the tree starting from root: Player 1 starts, 6 chambers
expand(g.root, current_player=0, remaining_chambers=6)

# Save the EFG
g.to_efg("russian_roulette.efg")