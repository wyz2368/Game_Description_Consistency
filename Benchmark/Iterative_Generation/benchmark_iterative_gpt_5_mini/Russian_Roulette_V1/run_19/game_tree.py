import pygambit as gbt

# Create the game with two players
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian roulette")

# Chance at root: which chamber contains the bullet (1..6)
chance_actions = [f"Chamber {i}" for i in range(1, 7)]
g.append_move(g.root, g.players.chance, chance_actions)

# Set uniform chance probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Recursive builder for decision nodes
def build_decision(node, current_player_name, current_player_index, chamber_index, bullet_index):
    """
    node: Node where current_player moves
    current_player_name: string name, e.g. "Player 1" or "Player 2"
    current_player_index: 0 for Player 1, 1 for Player 2
    chamber_index: current chamber pointer (1..6)
    bullet_index: fixed loaded chamber chosen by chance (1..6)
    """
    # Add the player's move (two actions: Quit or Pull)
    g.append_move(node, current_player_name, ["Quit", "Pull"])
    # Children in order correspond to the actions above:
    quit_node = node.children[0]
    pull_node = node.children[1]

    # Quit outcome: quitting player gets 0, other gets 1
    quit_payoffs = [0, 0]
    quit_payoffs[current_player_index] = 0
    quit_payoffs[1 - current_player_index] = 1
    quit_outcome = g.add_outcome(quit_payoffs, label=f"Quit_{current_player_name}")
    g.set_outcome(quit_node, quit_outcome)

    # Pull branch: if current chamber is loaded -> shooter dies; else pass turn
    if chamber_index == bullet_index:
        # Shooter dies: shooter -1, other +1
        shot_payoffs = [0, 0]
        shot_payoffs[current_player_index] = -1
        shot_payoffs[1 - current_player_index] = 1
        shot_outcome = g.add_outcome(shot_payoffs, label=f"Shot_{current_player_name}")
        g.set_outcome(pull_node, shot_outcome)
    else:
        # Safe pull: advance chamber and pass to opponent
        next_player_index = 1 - current_player_index
        next_player_name = f"Player {next_player_index + 1}"
        next_chamber = (chamber_index % 6) + 1  # wrap from 6 to 1
        # Recurse on the non-terminal pull node
        build_decision(pull_node, next_player_name, next_player_index, next_chamber, bullet_index)

# For each chance outcome (each fixed bullet position), build the decision subtree
for i, chance_child in enumerate(g.root.children):
    bullet_index = i + 1  # chambers numbered 1..6
    # Game starts with Player 1 and chamber pointer at 1
    build_decision(chance_child, "Player 1", 0, chamber_index=1, bullet_index=bullet_index)

# Save the EFG
g.to_efg("russian_roulette.efg")