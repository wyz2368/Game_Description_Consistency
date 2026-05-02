import pygambit as gbt

# Create the game with the two players
player_names = ["Player 1", "Player 2"]
g = gbt.Game.new_tree(players=player_names, title="Alternating Russian Roulette (6-chamber)")

def expand(node, current_player_idx, remaining_chambers):
    """
    Expand the game tree at 'node' where it's current_player's turn
    and there are remaining_chambers unpulled chambers.
    """
    # Append the decision for the current player: Quit or Pull
    g.append_move(node, player_names[current_player_idx], ["Quit", "Pull"])

    # Handle the "Quit" action (child 0)
    quit_child = node.children[0]
    quit_payoffs = [0, 0]
    quit_payoffs[current_player_idx] = 0
    quit_payoffs[1 - current_player_idx] = 1
    quit_outcome = g.add_outcome(quit_payoffs, label=f"{player_names[current_player_idx]} quits")
    g.set_outcome(quit_child, quit_outcome)

    # Handle the "Pull" action (child 1)
    pull_child = node.children[1]

    # Determine chance actions based on remaining_chambers
    # If remaining_chambers == 1, safe probability is 0 so only include "Fire"
    if remaining_chambers == 1:
        chance_actions = ["Fire"]
        g.append_move(pull_child, g.players.chance, chance_actions)
        # Fire prob = 1
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, 1)])
    else:
        chance_actions = ["Fire", "Safe"]
        g.append_move(pull_child, g.players.chance, chance_actions)
        # Fire prob = 1/remaining_chambers, Safe prob = (remaining_chambers-1)/remaining_chambers
        g.set_chance_probs(
            pull_child.infoset,
            [gbt.Rational(1, remaining_chambers), gbt.Rational(remaining_chambers - 1, remaining_chambers)]
        )

    # "Fire" branch (child 0 of the chance node): shooter dies
    fire_node = pull_child.children[0]
    fire_payoffs = [0, 0]
    fire_payoffs[current_player_idx] = -1
    fire_payoffs[1 - current_player_idx] = 1
    fire_outcome = g.add_outcome(fire_payoffs, label=f"{player_names[current_player_idx]} shot")
    g.set_outcome(fire_node, fire_outcome)

    # "Safe" branch (child 1 of the chance node) — only present when remaining_chambers > 1
    if remaining_chambers > 1:
        safe_node = pull_child.children[1]
        # Continue with the other player's turn and one fewer remaining chamber
        expand(safe_node, 1 - current_player_idx, remaining_chambers - 1)

# Build the tree starting from the root: Player 1 goes first, 6 chambers total
expand(g.root, current_player_idx=0, remaining_chambers=6)

# Save the game to an EFG file
g.to_efg("russian_roulette.efg")