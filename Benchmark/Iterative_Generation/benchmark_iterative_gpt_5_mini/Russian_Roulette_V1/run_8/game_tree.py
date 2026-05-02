import pygambit as gbt

# Create game with two players; Player 1 acts first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver alternating game")

# Add chance move at root: which chamber (1..6) contains the bullet
chambers = [f"Chamber {i}" for i in range(1, 7)]
g.append_move(g.root, g.players.chance, chambers)
# Set equal probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in chambers])

# Pre-create outcomes (payoff order = [Player 1, Player 2])
out_quit_p1 = g.add_outcome([0, 1], label="Player1 quits")
out_quit_p2 = g.add_outcome([1, 0], label="Player2 quits")
out_die_p1 = g.add_outcome([-1, 1], label="Player1 dies")
out_die_p2 = g.add_outcome([1, -1], label="Player2 dies")

def build_subtree(node, current_chamber_pos, loaded_chamber, current_player_idx):
    """
    Recursive builder for one chance realization (loaded_chamber is an int 1..6).
    node: the current Node object to add a move to
    current_chamber_pos: int 1..6 indicating which chamber is currently aligned for this trigger pull
    loaded_chamber: int 1..6 chosen by chance at the root (fixed for this subtree)
    current_player_idx: 0 for Player 1, 1 for Player 2
    """
    player = g.players[current_player_idx]
    # Add the decision for this player: Pull or Quit
    g.append_move(node, player, ["Pull", "Quit"])
    # Children: node.children[0] is "Pull", node.children[1] is "Quit"
    pull_child = node.children[0]
    quit_child = node.children[1]

    # Set outcome for quitting: quitter gets 0, other gets 1
    if current_player_idx == 0:
        g.set_outcome(quit_child, out_quit_p1)
    else:
        g.set_outcome(quit_child, out_quit_p2)

    # Handle pulling the trigger
    if current_chamber_pos == loaded_chamber:
        # The pulling player is killed -> payoff -1 for shooter, +1 for other
        if current_player_idx == 0:
            g.set_outcome(pull_child, out_die_p1)
        else:
            g.set_outcome(pull_child, out_die_p2)
    else:
        # Empty chamber: advance to next chamber and pass turn to other player
        next_chamber = current_chamber_pos % 6 + 1  # wrap 1..6
        next_player_idx = 1 - current_player_idx
        # Recurse on the pull_child node
        build_subtree(pull_child, next_chamber, loaded_chamber, next_player_idx)

# For each chance outcome (which chamber is loaded), build the subtree starting at chamber position 1
for i, chance_child in enumerate(g.root.children):
    loaded = i + 1  # Chamber numbering 1..6
    # At the very start, the current chamber position is 1
    build_subtree(chance_child, current_chamber_pos=1, loaded_chamber=loaded, current_player_idx=0)

# Save the EFG
g.to_efg("revolver_game.efg")