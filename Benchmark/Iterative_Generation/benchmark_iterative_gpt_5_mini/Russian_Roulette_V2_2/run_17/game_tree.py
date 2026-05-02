import pygambit as gbt

# Build the game
players = ["Player 1", "Player 2"]
g = gbt.Game.new_tree(players=players, title="Six-chamber alternation (Russian roulette style)")

# A small cache to reuse identical outcomes
outcome_cache = {}

def get_outcome(payoffs, label=""):
    """
    Get or create an Outcome object for the given payoff list.
    payoffs: list or tuple matching the players order in 'players'
    """
    key = tuple(payoffs)
    if key not in outcome_cache:
        outcome_cache[key] = g.add_outcome(list(key), label=label)
    return outcome_cache[key]

def expand(node, current_player_index, remaining_chambers):
    """
    Expand the game tree at 'node' for the player with index current_player_index
    and the given number of remaining unpulled chambers.
    node must be a terminal node when this function is called.
    """
    current_player_label = players[current_player_index]
    other_index = 1 - current_player_index

    # Add the decision: Quit or Pull
    g.append_move(node, current_player_label, ["Quit", "Pull"])
    # children[0] corresponds to "Quit", children[1] to "Pull"
    quit_child = node.children[0]
    pull_child = node.children[1]

    # Outcome for quitting: quitter gets 0, other gets +1
    quit_payoffs = [0, 1] if current_player_index == 0 else [1, 0]
    quit_outcome = get_outcome(quit_payoffs, label=f"Quit by {current_player_label}")
    g.set_outcome(quit_child, quit_outcome)

    # Handle pulling the trigger
    if remaining_chambers == 1:
        # Certain fire: acting player dies (-1), other +1
        shoot_payoffs = [-1, 1] if current_player_index == 0 else [1, -1]
        shoot_outcome = get_outcome(shoot_payoffs, label=f"Shot (certain) by {current_player_label}")
        g.set_outcome(pull_child, shoot_outcome)
    else:
        # Chance node: Fire (prob 1/remaining) or No fire (prob (remaining-1)/remaining)
        g.append_move(pull_child, g.players.chance, ["Fire", "No fire"])
        # set probabilities using Rational
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, remaining_chambers),
                                                gbt.Rational(remaining_chambers - 1, remaining_chambers)])
        fire_child = pull_child.children[0]
        nofire_child = pull_child.children[1]

        # If fire, acting player dies
        shoot_payoffs = [-1, 1] if current_player_index == 0 else [1, -1]
        shoot_outcome = get_outcome(shoot_payoffs, label=f"Shot (chance) by {current_player_label}")
        g.set_outcome(fire_child, shoot_outcome)

        # If no fire, decrease remaining and give the other player the decision
        expand(nofire_child, other_index, remaining_chambers - 1)

# Start expansion from root: Player 1, 6 chambers
expand(g.root, current_player_index=0, remaining_chambers=6)

# Save to EFG
g.to_efg("revolver_game.efg")