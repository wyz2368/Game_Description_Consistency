import pygambit as gbt

# Create game with two players; Player 1 acts first (assumption).
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian roulette (sequential)")

# Chance: which chamber (1..6) contains the bullet (uniform)
g.append_move(g.root, g.players.chance, [f"Chamber {i}" for i in range(1, 7)])
# Set equal probabilities 1/6 for all six chance branches
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Pre-create outcome objects (payoff vectors follow ["Player 1", "Player 2"])
p1_wins_quit = g.add_outcome([1, 0], label="P1 wins (P2 quits)")
p1_wins_shot = g.add_outcome([1, -1], label="P1 wins (P2 shot)")
p2_wins_quit = g.add_outcome([0, 1], label="P2 wins (P1 quits)")
p2_wins_shot = g.add_outcome([-1, 1], label="P2 wins (P1 shot)")

def build_subtree(node, loaded_chamber, current_chamber, player_idx):
    """
    Recursively build decision nodes for a fixed loaded_chamber.
    node: current non-terminal node to append a move to
    loaded_chamber: int in 1..6
    current_chamber: int in 1..6 (the chamber that would fire if Pull is chosen here)
    player_idx: 0 for Player 1, 1 for Player 2
    """
    player_name = g.players[player_idx]
    # Append the decision for this node: Quit or Pull
    g.append_move(node, player_name, ["Quit", "Pull"])

    # Quit child: node.children[0] corresponds to "Quit"
    quit_child = node.children[0]
    # Quitting player gets 0, other player gets 1
    if player_idx == 0:
        # Player 1 quits => Player 2 wins
        g.set_outcome(quit_child, p2_wins_quit)
    else:
        # Player 2 quits => Player 1 wins
        g.set_outcome(quit_child, p1_wins_quit)

    # Pull child: node.children[1] corresponds to "Pull"
    pull_child = node.children[1]
    # If current chamber is the loaded one, pulling player dies
    if current_chamber == loaded_chamber:
        if player_idx == 0:
            # Player 1 pulls and is shot -> Player 2 wins by shot
            g.set_outcome(pull_child, p2_wins_shot)
        else:
            # Player 2 pulls and is shot -> Player 1 wins by shot
            g.set_outcome(pull_child, p1_wins_shot)
    else:
        # Survivor: advance chamber and pass to other player
        next_chamber = current_chamber % 6 + 1
        next_player = 1 - player_idx
        build_subtree(pull_child, loaded_chamber, next_chamber, next_player)

# For each chance outcome (loaded chamber = 1..6) build its subtree starting with chamber 1 and Player 1
for idx, chance_child in enumerate(g.root.children):
    loaded = idx + 1  # chamber indices 1..6
    build_subtree(chance_child, loaded_chamber=loaded, current_chamber=1, player_idx=0)

# Save the EFG
g.to_efg("revolver_game.efg")