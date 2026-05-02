import pygambit as gbt

# Create game with two players; Player 1 acts first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver (Russian roulette style)")

# Chance selects which chamber (1..6) contains the bullet
chamber_actions = [f"Chamber {i}" for i in range(1, 7)]
g.append_move(g.root, g.players.chance, chamber_actions)

# Set equal probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Recursive expansion function
def expand(node, bullet_pos, current_chamber, player_idx):
    """
    node: current tree node where player player_idx acts
    bullet_pos: integer in 0..5 indicating which initial chamber is loaded
               (mapping: "Chamber 1" -> 0, ..., "Chamber 6" -> 5)
    current_chamber: integer 0..5 representing the chamber to be fired now
    player_idx: 0 for Player 1, 1 for Player 2
    """
    player = g.players[player_idx]

    # Add the decision for this player at this node: Pull or Quit
    g.append_move(node, player, ["Pull", "Quit"])

    # "Pull" branch is child 0
    pull_node = node.children[0]
    if current_chamber == bullet_pos:
        # The shooter hits the loaded chamber and dies: shooter -1, other +1
        payoffs = [0, 0]
        payoffs[player_idx] = -1
        payoffs[1 - player_idx] = 1
        outcome = g.add_outcome(payoffs, label=f"{player} shot")
        g.set_outcome(pull_node, outcome)
    else:
        # Survives this shot; play continues with next player and next chamber
        next_chamber = (current_chamber + 1) % 6
        next_player_idx = 1 - player_idx
        expand(pull_node, bullet_pos, next_chamber, next_player_idx)

    # "Quit" branch is child 1: quitting player gets 0, other gets 1
    quit_node = node.children[1]
    payoffs = [0, 0]
    payoffs[player_idx] = 0
    payoffs[1 - player_idx] = 1
    outcome = g.add_outcome(payoffs, label=f"{player} quits")
    g.set_outcome(quit_node, outcome)


# Expand each chance branch separately (one bullet position per branch).
# Map Chamber 1 -> bullet_pos 0, ..., Chamber 6 -> bullet_pos 5.
for bullet_pos, chance_child in enumerate(g.root.children):
    # At the start, current_chamber is 0 (first trigger would test chamber 0)
    expand(chance_child, bullet_pos, current_chamber=0, player_idx=0)

# Save the EFG
g.to_efg("revolver_game.efg")