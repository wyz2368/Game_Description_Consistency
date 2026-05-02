import pygambit as gbt

# Player names (order matters for payoff vectors)
player_names = ["Player 1", "Player 2"]

# Create the game
g = gbt.Game.new_tree(players=player_names,
                      title="Six-chamber Russian roulette (alternating turns)")

# Pre-create commonly used outcomes (respecting player order [Player 1, Player 2])
# Player quits: quitting player 0, other 1
outcome_p1_quits = g.add_outcome([0, 1], label="P1 quits (P2 wins)")
outcome_p2_quits = g.add_outcome([1, 0], label="P2 quits (P1 wins)")
# Player dies by firing: acting player -1, other +1
outcome_p1_dies = g.add_outcome([-1, 1], label="P1 shot (P2 wins)")
outcome_p2_dies = g.add_outcome([1, -1], label="P2 shot (P1 wins)")

def build_decision(node, current_player_idx, remaining_chambers):
    """
    Build the decision node for the player with index current_player_idx
    when remaining_chambers remain in the revolver.
    """
    current_player_name = player_names[current_player_idx]

    # Append the player's decision: Quit or Pull
    g.append_move(node, current_player_name, ["Quit", "Pull"])
    # After append_move, node.children[0] => Quit branch, node.children[1] => Pull branch

    # Quit branch: terminal outcome
    if current_player_idx == 0:
        # Player 1 quits => [0,1]
        g.set_outcome(node.children[0], outcome_p1_quits)
    else:
        # Player 2 quits => [1,0]
        g.set_outcome(node.children[0], outcome_p2_quits)

    # Pull branch: chance determines Fire vs No fire (or certain Fire if only 1 chamber remains)
    pull_child = node.children[1]

    if remaining_chambers == 1:
        # Certain fire: single chance action "Fire" with probability 1
        g.append_move(pull_child, g.players.chance, ["Fire"])
        # Set chance probability = 1
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, 1)])
        # Fire => acting player dies
        if current_player_idx == 0:
            g.set_outcome(pull_child.children[0], outcome_p1_dies)
        else:
            g.set_outcome(pull_child.children[0], outcome_p2_dies)
    else:
        # Remaining > 1: chance has two actions
        g.append_move(pull_child, g.players.chance, ["Fire", "No fire"])
        # Probabilities: Fire = 1/remaining_chambers, No fire = (remaining_chambers-1)/remaining_chambers
        g.set_chance_probs(
            pull_child.infoset,
            [gbt.Rational(1, remaining_chambers),
             gbt.Rational(remaining_chambers - 1, remaining_chambers)]
        )
        # Fire branch: acting player dies -> terminal
        if current_player_idx == 0:
            g.set_outcome(pull_child.children[0], outcome_p1_dies)
        else:
            g.set_outcome(pull_child.children[0], outcome_p2_dies)

        # No fire branch: continue with the other player and one fewer chamber
        next_node = pull_child.children[1]
        build_decision(next_node, 1 - current_player_idx, remaining_chambers - 1)

# Build the tree starting from root: Player 1 acts first with 6 chambers
build_decision(g.root, current_player_idx=0, remaining_chambers=6)

# Save the game to an EFG file
g.to_efg("revolver_game.efg")