import pygambit as gbt

# Create game
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver alternating-turn game")

# Chance: which chamber (1..6) contains the bullet
chance_actions = [f"Bullet in chamber {i}" for i in range(1, 7)]
g.append_move(g.root, g.players.chance, chance_actions)
# Set equal probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Pre-create outcomes (player order: ["Player 1", "Player 2"])
p1_quits = g.add_outcome([0, 1], label="P1 quits (P2 wins)")
p2_quits = g.add_outcome([1, 0], label="P2 quits (P1 wins)")
p1_dies = g.add_outcome([-1, 1], label="P1 dies (P2 wins)")
p2_dies = g.add_outcome([1, -1], label="P2 dies (P1 wins)")

# For each possible loaded chamber L (1..6), build the subtree
for L in range(1, 7):
    # Root child corresponding to bullet in chamber L
    node = g.root.children[L - 1]
    current_player_idx = 0  # 0 => Player 1, 1 => Player 2

    # On turn t (1-based) the current chamber is t (1..6). We only need to build until t == L.
    for t in range(1, L + 1):
        player_name = f"Player {current_player_idx + 1}"
        # Append the move for this single node
        g.append_move(node, player_name, ["Pull", "Quit"])

        # The "Quit" branch is the second child (index 1)
        if current_player_idx == 0:
            # Player 1 quits => P1 gets 0, P2 gets 1
            g.set_outcome(node.children[1], p1_quits)
        else:
            # Player 2 quits => P1 gets 1, P2 gets 0
            g.set_outcome(node.children[1], p2_quits)

        # The "Pull" branch is the first child (index 0)
        if t == L:
            # This pull hits the loaded chamber -> shooter dies (terminal)
            if current_player_idx == 0:
                g.set_outcome(node.children[0], p1_dies)
            else:
                g.set_outcome(node.children[0], p2_dies)
            # No further children; subtree for this L complete
        else:
            # Safe pull: continue with the pull-child as the next decision node
            node = node.children[0]
            # Toggle player for the next turn
            current_player_idx = 1 - current_player_idx

# Save EFG
g.to_efg("revolver_game.efg")