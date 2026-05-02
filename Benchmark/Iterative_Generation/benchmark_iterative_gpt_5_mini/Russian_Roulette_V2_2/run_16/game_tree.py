import pygambit as gbt

# Create the game with the correct player order
players = ["Player 1", "Player 2"]
g = gbt.Game.new_tree(players=players, title="Two-player Russian roulette (6-chamber)")

# Pre-create outcomes (payoffs follow the players order: [Player 1, Player 2])
p1_dies = g.add_outcome([-1, 1], label="Player 1 dies")
p2_dies = g.add_outcome([1, -1], label="Player 2 dies")
p1_quits = g.add_outcome([0, 1], label="Player 1 quits")
p2_quits = g.add_outcome([1, 0], label="Player 2 quits")

def build(node, current_player_index, remaining_chambers):
    """
    Recursively build the decision tree from `node`.
    current_player_index: 0 for Player 1, 1 for Player 2
    remaining_chambers: number of unpulled chambers remaining
    """
    current_player_name = players[current_player_index]

    # Add the decision move for the current player: "Quit" or "Pull"
    g.append_move(node, current_player_name, ["Quit", "Pull"])

    # Quit branch: node.children[0]
    quit_node = node.children[0]
    if current_player_index == 0:
        # Player 1 quits -> [0, 1]
        g.set_outcome(quit_node, p1_quits)
    else:
        # Player 2 quits -> [1, 0]
        g.set_outcome(quit_node, p2_quits)

    # Pull branch: node.children[1]
    pull_node = node.children[1]

    if remaining_chambers == 1:
        # Pull fires for certain -> acting player dies
        if current_player_index == 0:
            g.set_outcome(pull_node, p1_dies)
        else:
            g.set_outcome(pull_node, p2_dies)
    else:
        # Chance node: "Fire" with prob 1/remaining, "No fire" with prob (remaining-1)/remaining
        g.append_move(pull_node, g.players.chance, ["Fire", "No fire"])
        # set chance probabilities on this chance infoset
        g.set_chance_probs(pull_node.infoset, [gbt.Rational(1, remaining_chambers),
                                                gbt.Rational(remaining_chambers - 1, remaining_chambers)])
        # Fire branch: pull_node.children[0] -> acting player dies
        fire_child = pull_node.children[0]
        if current_player_index == 0:
            g.set_outcome(fire_child, p1_dies)
        else:
            g.set_outcome(fire_child, p2_dies)
        # No fire branch: pull_node.children[1] -> continue with other player and one fewer chamber
        nofire_child = pull_node.children[1]
        next_player_index = 1 - current_player_index
        build(nofire_child, next_player_index, remaining_chambers - 1)

# Build the tree starting from the root: Player 1 acts first, 6 chambers available
build(g.root, current_player_index=0, remaining_chambers=6)

# Save the EFG
g.to_efg("russian_roulette.efg")