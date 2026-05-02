import pygambit as gbt

# Define player order and create the game
players = ["Player 1", "Player 2"]
g = gbt.Game.new_tree(players=players, title="Six-chamber revolver (Russian Roulette)")

# Chance selects which chamber (1..6) contains the bullet
chance_actions = [f"Chamber {i+1}" for i in range(6)]
g.append_move(g.root, g.players.chance, chance_actions)
# Set equal probability 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Pre-create common outcomes (payoff vectors follow [Player 1, Player 2])
outcome_p1_quits = g.add_outcome([0, 1], label="P1 quits")
outcome_p2_quits = g.add_outcome([1, 0], label="P2 quits")
outcome_p1_shot = g.add_outcome([-1, 1], label="P1 shot")
outcome_p2_shot = g.add_outcome([1, -1], label="P2 shot")

# For each chance outcome (each fixed bullet index), build the decision sequence
for bullet_index, chance_child in enumerate(g.root.children):
    # frontier entries: (node, current_chamber_index, current_player_index)
    # current_chamber_index starts at 0 for the first trigger position
    frontier = [(chance_child, 0, 0)]  # Player 1 starts
    while frontier:
        node, chamber_idx, player_idx = frontier.pop(0)
        player_name = players[player_idx]

        # At this node the current player chooses to Quit or Pull
        g.append_move(node, player_name, ["Quit", "Pull"])

        # Quit branch is terminal: quitting player gets 0, other gets 1
        if player_idx == 0:
            g.set_outcome(node.children[0], outcome_p1_quits)
        else:
            g.set_outcome(node.children[0], outcome_p2_quits)

        # Pull branch: check if the current chamber is the bullet
        pull_child = node.children[1]
        if chamber_idx == bullet_index:
            # Shooter gets -1, other gets +1
            if player_idx == 0:
                g.set_outcome(pull_child, outcome_p1_shot)
            else:
                g.set_outcome(pull_child, outcome_p2_shot)
        else:
            # Safe pull: advance chamber and pass turn to the other player
            next_chamber = (chamber_idx + 1) % 6
            next_player = 1 - player_idx
            frontier.append((pull_child, next_chamber, next_player))

# Save the EFG
g.to_efg("revolver.efg")