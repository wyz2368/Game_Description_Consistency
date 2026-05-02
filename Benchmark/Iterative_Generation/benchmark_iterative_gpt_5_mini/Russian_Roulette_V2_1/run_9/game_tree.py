import pygambit as gbt

# Create game with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating six-chamber revolver game")

def build(node, player_idx, remaining_chambers):
    """
    Build the decision at 'node' for player with index player_idx,
    given remaining_chambers unpulled chambers.
    """
    player_name = g.players[player_idx]  # use string name for append_move

    # Player chooses to Pull or Quit
    g.append_move(node, player_name, ["Pull", "Quit"])

    # Quit branch: node.children[1]
    quit_node = node.children[1]
    quit_payoffs = [None, None]
    quit_payoffs[player_idx] = 0            # quitting player gets 0
    quit_payoffs[1 - player_idx] = 1        # other player wins and gets 1
    g.set_outcome(quit_node,
                  g.add_outcome(quit_payoffs, label=f"Quit by {player_name}"))

    # Pull branch: node.children[0] -> chance move
    pull_node = node.children[0]

    # If only one chamber remains, the chance outcome is deterministically "Fire"
    if remaining_chambers == 1:
        g.append_move(pull_node, g.players.chance, ["Fire"])
        # Set chance probability = 1 for the single action
        g.set_chance_probs(pull_node.infoset, [gbt.Rational(1, 1)])
        fire_node = pull_node.children[0]
        fire_payoffs = [None, None]
        fire_payoffs[player_idx] = -1           # pulling player dies
        fire_payoffs[1 - player_idx] = 1        # other player wins
        g.set_outcome(fire_node,
                      g.add_outcome(fire_payoffs, label=f"Fire on pull by {player_name}"))
    else:
        # remaining_chambers > 1: two chance outcomes "Fire" and "Click"
        g.append_move(pull_node, g.players.chance, ["Fire", "Click"])
        # Set probabilities: Fire = 1/remaining, Click = (remaining-1)/remaining
        g.set_chance_probs(pull_node.infoset, [
            gbt.Rational(1, remaining_chambers),
            gbt.Rational(remaining_chambers - 1, remaining_chambers)
        ])
        # Fire branch (terminal)
        fire_node = pull_node.children[0]
        fire_payoffs = [None, None]
        fire_payoffs[player_idx] = -1
        fire_payoffs[1 - player_idx] = 1
        g.set_outcome(fire_node,
                      g.add_outcome(fire_payoffs, label=f"Fire on pull by {player_name}"))
        # Click branch: play continues with other player and one fewer chamber
        click_node = pull_node.children[1]
        build(click_node, 1 - player_idx, remaining_chambers - 1)

# Start building from root with Player 1 and 6 chambers
build(g.root, player_idx=0, remaining_chambers=6)

# Save the EFG
g.to_efg("revolver_game.efg")