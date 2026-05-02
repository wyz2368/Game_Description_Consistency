import pygambit as gbt

def build_node(g, node, player_names, current_player_idx, remaining_chambers):
    """
    Recursively expand the game tree from 'node' where it's the turn of
    player_names[current_player_idx] and 'remaining_chambers' remain.
    """
    player_name = player_names[current_player_idx]
    opponent_idx = 1 - current_player_idx
    opponent_name = player_names[opponent_idx]

    # Add the player's decision: Quit or Pull
    g.append_move(node, player_name, ["Quit", "Pull"])
    # Children:
    quit_child = node.children[0]
    pull_child = node.children[1]

    # Outcome for Quit: quitting player gets 0, other gets 1
    payoffs_quit = [0, 0]
    payoffs_quit[current_player_idx] = 0
    payoffs_quit[opponent_idx] = 1
    outcome_quit = g.add_outcome(payoffs_quit, label="Quit")
    g.set_outcome(quit_child, outcome_quit)

    # Handle Pull:
    if remaining_chambers > 1:
        # Chance with two outcomes: Fire (1/remaining) and No fire ((remaining-1)/remaining)
        g.append_move(pull_child, g.players.chance, ["Fire", "No fire"])
        # Set chance probabilities
        g.set_chance_probs(pull_child.infoset,
                           [gbt.Rational(1, remaining_chambers),
                            gbt.Rational(remaining_chambers - 1, remaining_chambers)])
        # Fire branch: shooter dies
        payoffs_fire = [0, 0]
        payoffs_fire[current_player_idx] = -1
        payoffs_fire[opponent_idx] = 1
        outcome_fire = g.add_outcome(payoffs_fire, label="Fire")
        g.set_outcome(pull_child.children[0], outcome_fire)
        # No fire branch: continue with opponent, remaining_chambers - 1
        nofire_child = pull_child.children[1]
        build_node(g, nofire_child, player_names, opponent_idx, remaining_chambers - 1)
    else:
        # remaining_chambers == 1: Pull fires for certain. Include only "Fire" with prob 1.
        g.append_move(pull_child, g.players.chance, ["Fire"])
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, 1)])
        payoffs_fire = [0, 0]
        payoffs_fire[current_player_idx] = -1
        payoffs_fire[opponent_idx] = 1
        outcome_fire = g.add_outcome(payoffs_fire, label="Fire (certain)")
        g.set_outcome(pull_child.children[0], outcome_fire)


# Build the game
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# Start the recursive expansion from the root: Player 1, 6 chambers
build_node(g, g.root, ["Player 1", "Player 2"], current_player_idx=0, remaining_chambers=6)

# Save the EFG
g.to_efg("russian_roulette.efg")