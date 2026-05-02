import pygambit as gbt

# Create the game with Player 1 moving first
players = ["Player 1", "Player 2"]
g = gbt.Game.new_tree(players=players, title="Six-chamber Russian Roulette")

def build(node, player_idx, remaining_chambers):
    """
    Recursively build the tree from `node` where it's players[player_idx]'s turn
    and `remaining_chambers` chambers remain (k).
    """
    player_name = players[player_idx]

    # Decision: Quit or Pull
    g.append_move(node, player_name, ["Quit", "Pull"])
    # Quit branch is children[0]
    quit_node = node.children[0]
    if player_idx == 0:
        quit_outcome = g.add_outcome([0, 1], label=f"{player_name} quits")
    else:
        quit_outcome = g.add_outcome([1, 0], label=f"{player_name} quits")
    g.set_outcome(quit_node, quit_outcome)

    # Pull branch is children[1]
    pull_node = node.children[1]

    # Chance: determine whether the current chamber is loaded
    if remaining_chambers == 1:
        chance_actions = ["Loaded"]  # deterministic loaded
        probs = [gbt.Rational(1, 1)]
    else:
        chance_actions = ["Loaded", "Empty"]
        probs = [gbt.Rational(1, remaining_chambers),
                 gbt.Rational(remaining_chambers - 1, remaining_chambers)]

    g.append_move(pull_node, g.players.chance, chance_actions)
    # set chance probabilities for this chance infoset
    g.set_chance_probs(pull_node.infoset, probs)

    # Loaded branch (children[0]) => shooter dies, other wins
    loaded_node = pull_node.children[0]
    if player_idx == 0:
        loaded_outcome = g.add_outcome([-1, 1], label=f"{player_name} shot (loaded)")
    else:
        loaded_outcome = g.add_outcome([1, -1], label=f"{player_name} shot (loaded)")
    g.set_outcome(loaded_node, loaded_outcome)

    # Empty branch (children[1]) => if exists, continue with other player and remaining_chambers - 1
    if remaining_chambers > 1:
        empty_node = pull_node.children[1]
        build(empty_node, 1 - player_idx, remaining_chambers - 1)

# Start recursion from the root: Player 1 with 6 chambers
build(g.root, player_idx=0, remaining_chambers=6)

# Save the EFG
g.to_efg("russian_roulette.efg")