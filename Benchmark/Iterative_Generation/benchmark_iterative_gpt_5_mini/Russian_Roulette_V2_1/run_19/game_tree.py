import pygambit as gbt

# Create the game with the specified player order
players = ["Player 1", "Player 2"]
g = gbt.Game.new_tree(players=players, title="Six-chamber Russian Roulette")

# Pre-create the outcomes (payoffs follow [Player 1, Player 2])
outcome_p1_quits = g.add_outcome([0, 1], label="P1 quits, P2 wins")
outcome_p2_quits = g.add_outcome([1, 0], label="P2 quits, P1 wins")
outcome_p1_death = g.add_outcome([-1, 1], label="P1 dies, P2 wins")
outcome_p2_death = g.add_outcome([1, -1], label="P2 dies, P1 wins")

def add_turn(node, current_player_idx, remaining_chambers):
    """
    Add a decision node for the current player at 'node', handling the "Quit" and "Pull" actions.
    If "Pull" is taken, add a chance node with probabilities depending on remaining_chambers.
    """
    current_player = players[current_player_idx]
    other_player_idx = 1 - current_player_idx

    # Add the player's decision: "Quit" or "Pull"
    g.append_move(node, current_player, ["Quit", "Pull"])

    # The "Quit" branch is the first child (index 0)
    quit_child = node.children[0]
    if current_player_idx == 0:
        # Player 1 quits -> [0,1]
        g.set_outcome(quit_child, outcome_p1_quits)
    else:
        # Player 2 quits -> [1,0]
        g.set_outcome(quit_child, outcome_p2_quits)

    # The "Pull" branch is the second child (index 1)
    pull_child = node.children[1]

    # For the pull, add a chance move:
    # If remaining_chambers == 1, include only the "Fire" action (certainty).
    if remaining_chambers == 1:
        chance_actions = ["Fire"]
    else:
        chance_actions = ["Fire", "Click"]

    g.append_move(pull_child, g.players.chance, chance_actions)

    # Set chance probabilities
    if remaining_chambers == 1:
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, 1)])
    else:
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, remaining_chambers),
                                                 gbt.Rational(remaining_chambers - 1, remaining_chambers)])

    # The "Fire" outcome is the first child of the chance node
    fire_child = pull_child.children[0]
    if current_player_idx == 0:
        # Player 1 pulled and the gun fired -> P1 dies
        g.set_outcome(fire_child, outcome_p1_death)
    else:
        # Player 2 pulled and the gun fired -> P2 dies
        g.set_outcome(fire_child, outcome_p2_death)

    # If "Click" exists, recurse to the other player's turn with one fewer remaining chamber
    if remaining_chambers > 1:
        click_child = pull_child.children[1]
        add_turn(click_child, other_player_idx, remaining_chambers - 1)

# Build the game starting from the root: Player 1 acts first, 6 chambers
add_turn(g.root, current_player_idx=0, remaining_chambers=6)

# Save the EFG
g.to_efg("six_chamber_russian_roulette.efg")