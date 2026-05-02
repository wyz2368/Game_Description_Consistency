import pygambit as gbt

# Create the game with two players
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver alternating game")

# Add chance move at root: which chamber contains the bullet (1..6)
chamber_actions = [f"Chamber {i}" for i in range(1, 7)]
g.append_move(g.root, g.players.chance, chamber_actions)

# Set uniform chance probabilities 1/6 for each chamber
probs = [gbt.Rational(1, 6) for _ in range(6)]
g.set_chance_probs(g.root.infoset, probs)

# Pre-create outcomes for the four terminal types to avoid duplicates
# Order of payoffs is [Player 1, Player 2]
out_quit_p1 = g.add_outcome([0, 1], label="Player1 quits -> P2 wins")
out_quit_p2 = g.add_outcome([1, 0], label="Player2 quits -> P1 wins")
out_shot_p1 = g.add_outcome([-1, 1], label="Player1 shot -> P2 wins")
out_shot_p2 = g.add_outcome([1, -1], label="Player2 shot -> P1 wins")

# Recursive builder for alternating play after a specific chance branch.
# node: current node where the current player must decide
# current_player_idx: 0 for Player 1, 1 for Player 2
# chamber_index: which chamber (1..6) is currently aligned for this trigger pull
# bullet_pos: the chamber that contains the bullet (1..6), fixed for the chance branch
def build_turn(node, current_player_idx, chamber_index, bullet_pos):
    player_name = "Player 1" if current_player_idx == 0 else "Player 2"
    # Append the decision: Quit or Pull (Quit is child 0, Pull is child 1)
    g.append_move(node, player_name, ["Quit", "Pull"])
    # Quit branch: child 0
    quit_child = node.children[0]
    if current_player_idx == 0:
        g.set_outcome(quit_child, out_quit_p1)
    else:
        g.set_outcome(quit_child, out_quit_p2)
    # Pull branch: child 1
    pull_child = node.children[1]
    # If the current chamber is the bullet, shooter dies -> terminal
    if chamber_index == bullet_pos:
        if current_player_idx == 0:
            g.set_outcome(pull_child, out_shot_p1)
        else:
            g.set_outcome(pull_child, out_shot_p2)
    else:
        # Otherwise survive and pass to the other player with next chamber
        next_chamber = chamber_index + 1
        if next_chamber > 6:
            next_chamber = 1
        # Recurse: other player's turn at this child node
        build_turn(pull_child, 1 - current_player_idx, next_chamber, bullet_pos)

# For each chance child (each possible bullet position), build the subtree.
# Note: g.root.children is a list with 6 nodes corresponding to "Chamber 1" .. "Chamber 6"
for i, chance_child in enumerate(g.root.children):
    bullet_position = i + 1  # chamber numbering 1..6
    # The first trigger pull, if played, uses chamber_index = 1
    # Player 1 acts first.
    build_turn(chance_child, current_player_idx=0, chamber_index=1, bullet_pos=bullet_position)

# Save the EFG
g.to_efg("revolver_game.efg")