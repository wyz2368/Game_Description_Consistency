import pygambit as gbt

# Create the game with the required players
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating revolver (Russian roulette style)")

players = ["Player 1", "Player 2"]

# Cache outcomes to avoid repeated identical add_outcome calls
outcome_cache = {}

def get_outcome(payoff_list, label=""):
    """Return an Outcome object for the given payoff_list (in player order),
    reusing previously created outcomes when possible."""
    key = tuple(payoff_list)
    if key not in outcome_cache:
        outcome_cache[key] = g.add_outcome(list(payoff_list), label=label)
    return outcome_cache[key]

def build(node, remaining_chambers, current_player_idx):
    """
    Recursively build the game tree from 'node' given the number of remaining chambers
    and whose turn it is (current_player_idx: 0 for Player 1, 1 for Player 2).
    """
    current_player = players[current_player_idx]
    other_idx = 1 - current_player_idx
    other_player = players[other_idx]

    # Add the current player's decision: Quit or Pull trigger
    g.append_move(node, current_player, ["Quit", "Pull trigger"])

    # Child 0: Quit -> quitting player gets 0, other gets 1
    quit_child = node.children[0]
    quit_payoffs = [None, None]
    quit_payoffs[current_player_idx] = 0
    quit_payoffs[other_idx] = 1
    g.set_outcome(quit_child, get_outcome(tuple(quit_payoffs), label="Quit"))

    # Child 1: Pull trigger
    pull_child = node.children[1]

    # If only one chamber remains, pulling fires for certain
    if remaining_chambers == 1:
        # Acting player dies: acting player -1, other +1
        fire_payoffs = [None, None]
        fire_payoffs[current_player_idx] = -1
        fire_payoffs[other_idx] = 1
        g.set_outcome(pull_child, get_outcome(tuple(fire_payoffs), label="Certain fire"))
    else:
        # Append a chance move at the pull_child with actions "Fire" and "No fire"
        g.append_move(pull_child, g.players.chance, ["Fire", "No fire"])
        # Set chance probabilities: Fire = 1 / remaining_chambers, No fire = (remaining_chambers-1)/remaining_chambers
        g.set_chance_probs(pull_child.infoset, [
            gbt.Rational(1, remaining_chambers),
            gbt.Rational(remaining_chambers - 1, remaining_chambers)
        ])

        # Chance child 0: Fire -> acting player dies
        fire_node = pull_child.children[0]
        fire_payoffs = [None, None]
        fire_payoffs[current_player_idx] = -1
        fire_payoffs[other_idx] = 1
        g.set_outcome(fire_node, get_outcome(tuple(fire_payoffs), label="Fire"))

        # Chance child 1: No fire -> decrement remaining chambers and switch turn to other player
        nofire_node = pull_child.children[1]
        build(nofire_node, remaining_chambers - 1, other_idx)

# Start building from the root: 6 chambers, Player 1 to move first
build(g.root, remaining_chambers=6, current_player_idx=0)

# Save the EFG
g.to_efg("revolver_game.efg")