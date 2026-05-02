import pygambit as gbt

# Create the game with the required player order
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver alternating play (Russian roulette style)")

# Pre-create the outcomes with correct ordering [Player 1 payoff, Player 2 payoff]
outcome_p1_quits = g.add_outcome([0, 1], label="Player 1 quits")
outcome_p2_quits = g.add_outcome([1, 0], label="Player 2 quits")
outcome_p1_dies = g.add_outcome([-1, 1], label="Player 1 dies")
outcome_p2_dies = g.add_outcome([1, -1], label="Player 2 dies")

player_names = ["Player 1", "Player 2"]

def build(node, acting_player_index, remaining_chambers):
    """
    Recursively build the game tree from 'node' with the acting player index
    and the number of remaining chambers.
    """
    acting_player_name = player_names[acting_player_index]

    # Append the decision move for the acting player: "Quit" or "Pull"
    g.append_move(node, acting_player_name, ["Quit", "Pull"])
    # children: node.children[0] -> "Quit", node.children[1] -> "Pull"

    # Handle "Quit" child: acting player withdraws, other player wins
    quit_child = node.children[0]
    if acting_player_index == 0:
        # Player 1 quits -> [0,1]
        g.set_outcome(quit_child, outcome_p1_quits)
    else:
        # Player 2 quits -> [1,0]
        g.set_outcome(quit_child, outcome_p2_quits)

    # Handle "Pull" child
    pull_child = node.children[1]
    # If only one chamber remains, pulling fires for certain
    if remaining_chambers == 1:
        # Certain fire: acting player dies
        if acting_player_index == 0:
            g.set_outcome(pull_child, outcome_p1_dies)
        else:
            g.set_outcome(pull_child, outcome_p2_dies)
    else:
        # More than one chamber: chance determines fire vs click
        g.append_move(pull_child, g.players.chance, ["Fire", "Click"])
        # Set chance probabilities: Fire with prob 1/remaining_chambers, Click with (remaining_chambers-1)/remaining_chambers
        chance_infoset = pull_child.infoset
        g.set_chance_probs(chance_infoset,
                           [gbt.Rational(1, remaining_chambers),
                            gbt.Rational(remaining_chambers - 1, remaining_chambers)])
        # After chance move: pull_child.children[0] -> "Fire", pull_child.children[1] -> "Click"
        fire_child = pull_child.children[0]
        click_child = pull_child.children[1]

        # Set outcome for fire (acting player dies)
        if acting_player_index == 0:
            g.set_outcome(fire_child, outcome_p1_dies)
        else:
            g.set_outcome(fire_child, outcome_p2_dies)

        # On click, the game continues with the other player and one fewer chamber
        next_player_index = 1 - acting_player_index
        build(click_child, next_player_index, remaining_chambers - 1)

# Build the full tree starting from root, Player 1 acts first, 6 chambers
build(g.root, acting_player_index=0, remaining_chambers=6)

# Save the EFG to file
g.to_efg("revolver_game.efg")