import pygambit as gbt

# Create game with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver alternating game")

# Chance at root: which chamber (1..6) is loaded
g.append_move(g.root, g.players.chance, [f"Loaded {i}" for i in range(1, 7)])

# For each possible loaded chamber, build the deterministic alternating-play subtree
for loaded_index, chance_child in enumerate(g.root.children, start=1):
    current_node = chance_child
    current_player = "Player 1"  # Player 1 starts with t = 1
    # Pull numbers t = 1, 2, ..., up to 6 (will break when loaded_index reached)
    for t in range(1, 7):
        # Add decision for the current player at this node
        g.append_move(current_node, current_player, ["Quit", "Pull"])
        # "Quit" branch: quitting player gets 0, other gets 1
        if current_player == "Player 1":
            g.set_outcome(current_node.children[0], g.add_outcome([0, 1], label=f"Quit P1 at t={t}"))
        else:
            g.set_outcome(current_node.children[0], g.add_outcome([1, 0], label=f"Quit P2 at t={t}"))
        # "Pull" branch:
        pull_child = current_node.children[1]
        if t == loaded_index:
            # The current chamber is loaded: shooter dies
            if current_player == "Player 1":
                g.set_outcome(pull_child, g.add_outcome([-1, 1], label=f"P1 shot at t={t}"))
            else:
                g.set_outcome(pull_child, g.add_outcome([1, -1], label=f"P2 shot at t={t}"))
            break  # terminal because someone died
        else:
            # Not loaded: proceed to next turn (other player) at this pull_child
            current_node = pull_child
            current_player = "Player 2" if current_player == "Player 1" else "Player 1"

# Save the EFG
g.to_efg("revolver_game.efg")