import pygambit as gbt

# Create the game with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver (Russian roulette)")

# Add chance move: which chamber (1..6) contains the bullet
chance_actions = [f"Chamber {i}" for i in range(1, 7)]
g.append_move(g.root, g.players.chance, chance_actions)

# Set equal probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

def build_subtree(node, current_player_idx, current_chamber, loaded_chamber):
    """
    Recursively build the alternating decision nodes starting from `node`.
    current_player_idx: 0 for Player 1, 1 for Player 2
    current_chamber: integer 1..6 indicating which chamber is currently under the hammer
    loaded_chamber: the fixed chamber index chosen by chance (1..6)
    """
    player_name = g.players[current_player_idx]  # "Player 1" or "Player 2"
    # Append this player's move: Pull or Quit
    g.append_move(node, player_name, ["Pull", "Quit"])
    # children: node.children[0] corresponds to "Pull", node.children[1] to "Quit"

    # Quit branch: quitting player gets 0, other gets 1
    if current_player_idx == 0:
        payoff_quit = [0, 1]
        label_quit = "Player 1 quits"
    else:
        payoff_quit = [1, 0]
        label_quit = "Player 2 quits"
    quit_outcome = g.add_outcome(payoff_quit, label=label_quit)
    g.set_outcome(node.children[1], quit_outcome)

    # Pull branch:
    if current_chamber == loaded_chamber:
        # Shooter dies: shooter gets -1, other gets +1
        if current_player_idx == 0:
            payoff_shot = [-1, 1]
            label_shot = "Player 1 shot (dies)"
        else:
            payoff_shot = [1, -1]
            label_shot = "Player 2 shot (dies)"
        shot_outcome = g.add_outcome(payoff_shot, label=label_shot)
        g.set_outcome(node.children[0], shot_outcome)
    else:
        # Survives: advance chamber and pass turn to other player
        next_chamber = (current_chamber % 6) + 1
        next_player_idx = 1 - current_player_idx
        # Recurse on the child node (survived after pulling)
        build_subtree(node.children[0], next_player_idx, next_chamber, loaded_chamber)

# For each possible loaded chamber (each chance child), build the decision tree
# The initial current chamber is 1 and Player 1 acts first
for i, chance_child in enumerate(g.root.children):  # i = 0..5 corresponds to loaded chamber 1..6
    loaded_chamber = i + 1
    build_subtree(chance_child, current_player_idx=0, current_chamber=1, loaded_chamber=loaded_chamber)

# Save the EFG
g.to_efg("revolver_game.efg")