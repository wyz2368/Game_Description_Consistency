import pygambit as gbt

# Create the game with the two players (Player 1 acts first)
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian roulette")

# Pre-create common outcomes (payoffs follow the order: [Player 1, Player 2])
outcome_p1_quits = g.add_outcome([0, 1], label="P1 quits, P2 wins")
outcome_p2_quits = g.add_outcome([1, 0], label="P2 quits, P1 wins")
outcome_p1_dies = g.add_outcome([-1, 1], label="P1 dies, P2 wins")
outcome_p2_dies = g.add_outcome([1, -1], label="P2 dies, P1 wins")

players = ["Player 1", "Player 2"]

def build(node, current_player_index, remaining_chambers):
    """
    Recursively build the game tree.
    node: current node where current_player will act
    current_player_index: 0 for Player 1, 1 for Player 2
    remaining_chambers: number of unpulled chambers remaining (integer >= 1)
    """
    current_player = players[current_player_index]

    # Append the decision for the current player: Quit or Pull trigger
    g.append_move(node, current_player, ["Quit", "Pull trigger"])
    # children: node.children[0] = Quit branch, node.children[1] = Pull trigger branch
    quit_child = node.children[0]
    pull_child = node.children[1]

    # Set outcome for quitting
    if current_player_index == 0:
        # Player 1 quits -> [0, 1]
        g.set_outcome(quit_child, outcome_p1_quits)
    else:
        # Player 2 quits -> [1, 0]
        g.set_outcome(quit_child, outcome_p2_quits)

    # Handle pulling the trigger
    if remaining_chambers > 1:
        # Chance determines Fire or No fire
        g.append_move(pull_child, g.players.chance, ["Fire", "No fire"])
        # Set probabilities: Fire = 1/remaining, No fire = (remaining-1)/remaining
        g.set_chance_probs(pull_child.infoset,
                           [gbt.Rational(1, remaining_chambers),
                            gbt.Rational(remaining_chambers - 1, remaining_chambers)])
        fire_child = pull_child.children[0]
        nofire_child = pull_child.children[1]

        # Set terminal outcome for fire (acting player dies)
        if current_player_index == 0:
            g.set_outcome(fire_child, outcome_p1_dies)
        else:
            g.set_outcome(fire_child, outcome_p2_dies)

        # If no fire, continue with other player and one fewer chamber
        build(nofire_child, 1 - current_player_index, remaining_chambers - 1)

    else:
        # remaining_chambers == 1: the trigger fires for certain.
        # Create a deterministic chance node with single "Fire" action,
        # set its probability to 1 and set the terminal outcome accordingly.
        g.append_move(pull_child, g.players.chance, ["Fire"])
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, 1)])
        fire_child = pull_child.children[0]
        if current_player_index == 0:
            g.set_outcome(fire_child, outcome_p1_dies)
        else:
            g.set_outcome(fire_child, outcome_p2_dies)

# Build the full tree starting with Player 1 and 6 chambers
build(g.root, current_player_index=0, remaining_chambers=6)

# Save the EFG
g.to_efg("russian_roulette.efg")