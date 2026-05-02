import pygambit as gbt

# Create the game with the specified player order
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian Roulette")

# Pre-create outcome objects (payoffs follow [Player 1, Player 2])
p1_quits = g.add_outcome([0, 1], label="Player 1 quits")
p2_quits = g.add_outcome([1, 0], label="Player 2 quits")
p1_dies = g.add_outcome([-1, 1], label="Player 1 dies")
p2_dies = g.add_outcome([1, -1], label="Player 2 dies")

def expand(node, acting_player_index, remaining_chambers):
    """
    node: current node where acting player chooses
    acting_player_index: 0 for Player 1, 1 for Player 2
    remaining_chambers: number of unpulled chambers before this player's pull
    """
    player_name = g.players[acting_player_index]
    # Append the player's decision: Pull or Quit
    g.append_move(node, player_name, ["Pull", "Quit"])

    # Children: node.children[0] -> "Pull", node.children[1] -> "Quit"
    pull_node = node.children[0]
    quit_node = node.children[1]

    # Set outcome for quitting: quitting player gets 0, other gets 1
    if acting_player_index == 0:
        # Player 1 quits
        g.set_outcome(quit_node, p1_quits)
    else:
        # Player 2 quits
        g.set_outcome(quit_node, p2_quits)

    # Handle the pull action
    if remaining_chambers == 1:
        # Pull fires for certain -> acting player dies
        if acting_player_index == 0:
            g.set_outcome(pull_node, p1_dies)
        else:
            g.set_outcome(pull_node, p2_dies)
    else:
        # Chance node: "Fire" with prob 1/remaining, "Click" with prob (remaining-1)/remaining
        g.append_move(pull_node, g.players.chance, ["Fire", "Click"])
        # Set chance probabilities on this chance infoset
        g.set_chance_probs(pull_node.infoset,
                           [gbt.Rational(1, remaining_chambers),
                            gbt.Rational(remaining_chambers - 1, remaining_chambers)])
        # pull_node.children[0] -> "Fire", pull_node.children[1] -> "Click"
        fire_node = pull_node.children[0]
        click_node = pull_node.children[1]

        # Fire outcome: acting player dies
        if acting_player_index == 0:
            g.set_outcome(fire_node, p1_dies)
        else:
            g.set_outcome(fire_node, p2_dies)

        # Click: pass to the other player with one fewer chamber
        next_player_index = 1 - acting_player_index
        expand(click_node, next_player_index, remaining_chambers - 1)

# Build the tree starting with Player 1 and 6 chambers
expand(g.root, acting_player_index=0, remaining_chambers=6)

# Save the EFG
g.to_efg("russian_roulette.efg")