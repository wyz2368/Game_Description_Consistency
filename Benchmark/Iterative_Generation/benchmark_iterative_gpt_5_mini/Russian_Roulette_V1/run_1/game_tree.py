import pygambit as gbt

# Create game with two players (Player 1 starts)
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver (fixed chamber)")

# Chance determines which chamber (0..5) holds the bullet
g.append_move(g.root, g.players.chance, [f"Chamber {i}" for i in range(6)])
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Outcomes (payoffs ordered to match players=["Player 1", "Player 2"])
# Quit outcomes:
outcome_quit_p1 = g.add_outcome([0, 1], label="P1 quits, P2 wins")
outcome_quit_p2 = g.add_outcome([1, 0], label="P2 quits, P1 wins")
# Shooting outcomes:
outcome_shot_p1 = g.add_outcome([-1, 1], label="P1 shot, P2 wins")
outcome_shot_p2 = g.add_outcome([1, -1], label="P2 shot, P1 wins")

# For each possible bullet position (each chance child), build the turn-by-turn tree
for bullet_pos in range(6):
    node = g.root.children[bullet_pos]  # starting node for this bullet position
    current_player_idx = 0  # 0 => Player 1, 1 => Player 2
    # Turn indices correspond to the chamber index that would be fired on that turn
    for turn in range(6):
        player_name = "Player 1" if current_player_idx == 0 else "Player 2"
        # At this node the player chooses to Pull trigger or Quit
        g.append_move(node, player_name, ["Pull trigger", "Quit"])
        # The "Quit" branch is the second action (index 1)
        if current_player_idx == 0:
            g.set_outcome(node.children[1], outcome_quit_p1)
        else:
            g.set_outcome(node.children[1], outcome_quit_p2)
        # The "Pull trigger" branch is the first action (index 0)
        if bullet_pos == turn:
            # The bullet is in the current chamber: shooter dies -> terminal
            if current_player_idx == 0:
                g.set_outcome(node.children[0], outcome_shot_p1)
            else:
                g.set_outcome(node.children[0], outcome_shot_p2)
            # Branch ends here because the player has been shot
            break
        else:
            # No bullet: continue to next turn at the pull-branch child
            node = node.children[0]
            current_player_idx = 1 - current_player_idx  # alternate player

# Save the EFG
g.to_efg("revolver_game.efg")