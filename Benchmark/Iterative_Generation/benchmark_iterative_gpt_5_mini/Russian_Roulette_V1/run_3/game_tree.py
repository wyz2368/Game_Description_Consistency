import pygambit as gbt

# Build the game
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian roulette (alternating turns)")

# Chance picks which chamber (1..6) contains the bullet
g.append_move(g.root, g.players.chance, [f"Loaded {i}" for i in range(1, 7)])
# Set equal probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Pre-create commonly used outcomes (payoffs follow order: [Player 1, Player 2])
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_dies = g.add_outcome([1, -1], label="P2 dies")
p1_quits = g.add_outcome([0, 1], label="P1 quits")
p2_quits = g.add_outcome([1, 0], label="P2 quits")

def build_turn(node, current_chamber, loaded_chamber, current_player_idx):
    """
    node: the Node at which the current player moves
    current_chamber: int in 1..6, the chamber index to be checked if pulled now
    loaded_chamber: int in 1..6, the chamber that contains the bullet (fixed for this branch)
    current_player_idx: 0 for Player 1, 1 for Player 2
    """
    player_name = g.players[current_player_idx].label  # e.g., "Player 1" or "Player 2"
    # Append the decision node for this player with actions "Pull" and "Quit"
    g.append_move(node, player_name, ["Pull", "Quit"])
    # After append_move, node.children[0] corresponds to "Pull", node.children[1] to "Quit"
    pull_child = node.children[0]
    quit_child = node.children[1]

    # Handle Quit: quitting player gets 0, other gets 1
    if current_player_idx == 0:
        g.set_outcome(quit_child, p1_quits)
    else:
        g.set_outcome(quit_child, p2_quits)

    # Handle Pull:
    if current_chamber == loaded_chamber:
        # The shooter pulls on the loaded chamber and dies -> terminal
        if current_player_idx == 0:
            g.set_outcome(pull_child, p1_dies)
        else:
            g.set_outcome(pull_child, p2_dies)
    else:
        # Safe pull: advance chamber and pass turn to other player
        next_chamber = current_chamber + 1
        if next_chamber > 6:
            next_chamber = 1
        next_player = 1 - current_player_idx
        # Recursively build the next turn on the pull_child node
        build_turn(pull_child, next_chamber, loaded_chamber, next_player)

# For each chance branch (loaded chamber = 1..6), expand the alternating play
for loaded_idx, chance_child in enumerate(g.root.children, start=1):
    # Play starts with chamber 1 and Player 1's turn
    build_turn(chance_child, current_chamber=1, loaded_chamber=loaded_idx, current_player_idx=0)

# Save the EFG
g.to_efg("revolver_game.efg")