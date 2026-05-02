import pygambit as gbt

# Create the game with the specified player order
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating Russian Roulette (6-chamber)")

# Cache outcomes by payoff tuple to avoid duplicate outcome objects
_outcome_cache = {}

def get_outcome(p1_payoff, p2_payoff, label=""):
    key = (p1_payoff, p2_payoff)
    if key not in _outcome_cache:
        _outcome_cache[key] = g.add_outcome([p1_payoff, p2_payoff], label=label)
    return _outcome_cache[key]

def build(node, current_player_index, remaining_chambers):
    """
    Recursively build the decision/chance tree.
    node: current Node
    current_player_index: 0 for Player 1, 1 for Player 2
    remaining_chambers: number of chambers not yet pulled
    """
    # Current player label
    player = g.players[current_player_index]

    # Decision: "Quit" or "Pull"
    g.append_move(node, player, ["Quit", "Pull"])

    # Quit branch: node.children[0]
    quit_node = node.children[0]
    # quitting player gets 0, other player gets 1
    if current_player_index == 0:
        g.set_outcome(quit_node, get_outcome(0, 1, label=f"{player} quits"))
    else:
        g.set_outcome(quit_node, get_outcome(1, 0, label=f"{player} quits"))

    # Pull branch: node.children[1]
    pull_node = node.children[1]

    # Chance move after pulling: "Fire" (loaded) and possibly "Blank" (empty)
    if remaining_chambers > 1:
        # Both branches exist
        g.append_move(pull_node, g.players.chance, ["Fire", "Blank"])
        # Set probabilities: Fire = 1/remaining, Blank = (remaining-1)/remaining
        g.set_chance_probs(pull_node.infoset,
                           [gbt.Rational(1, remaining_chambers),
                            gbt.Rational(remaining_chambers - 1, remaining_chambers)])
        fire_node = pull_node.children[0]
        blank_node = pull_node.children[1]
    else:
        # Only "Fire" branch remains (probability 1)
        g.append_move(pull_node, g.players.chance, ["Fire"])
        g.set_chance_probs(pull_node.infoset, [gbt.Rational(1, 1)])
        fire_node = pull_node.children[0]
        blank_node = None

    # Fire branch outcome: shooter dies -> shooter gets -1, other gets 1
    if current_player_index == 0:
        g.set_outcome(fire_node, get_outcome(-1, 1, label=f"{player} shot (loaded)"))
    else:
        g.set_outcome(fire_node, get_outcome(1, -1, label=f"{player} shot (loaded)"))

    # Blank branch: continue with other player and one fewer remaining chamber
    if blank_node is not None:
        build(blank_node, 1 - current_player_index, remaining_chambers - 1)

# Start building from the root: Player 1 starts, 6 chambers
build(g.root, current_player_index=0, remaining_chambers=6)

# Save the EFG
g.to_efg("russian_roulette_game.efg")