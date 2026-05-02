import pygambit as gbt

# Players: Player 1 acts first
players = ["Player 1", "Player 2"]
g = gbt.Game.new_tree(players=players, title="Six-chamber Russian Roulette")

# Chance: which chamber contains the bullet (1..6)
g.append_move(g.root, g.players.chance, [f"Bullet at chamber {i+1}" for i in range(6)])
# Set uniform probabilities 1/6 each
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Pre-create outcome objects (order matches players = ["Player 1", "Player 2"])
quit_p1 = g.add_outcome([0, 1], label="Player1 quits (0), Player2 wins (1)")
quit_p2 = g.add_outcome([1, 0], label="Player2 quits (0), Player1 wins (1)")
death_p1 = g.add_outcome([-1, 1], label="Player1 dies (-1), Player2 wins (1)")
death_p2 = g.add_outcome([1, -1], label="Player2 dies (-1), Player1 wins (1)")

# Recursive expansion of decision nodes
def expand(node, current_player_idx, chamber_idx, bullet_pos):
    """
    node: the current decision node (not a chance node)
    current_player_idx: 0 for Player 1, 1 for Player 2
    chamber_idx: index of the current chamber (0..5) for this trigger pull
    bullet_pos: fixed bullet position (0..5) chosen by chance at the root
    """
    # Append decision for the current player: actions "Quit" and "Pull"
    g.append_move(node, players[current_player_idx], ["Quit", "Pull"])
    quit_node = node.children[0]   # child for "Quit"
    pull_node = node.children[1]   # child for "Pull"

    # If the current player quits, they get 0, the other gets 1
    if current_player_idx == 0:
        g.set_outcome(quit_node, quit_p1)
    else:
        g.set_outcome(quit_node, quit_p2)

    # If the player pulls the trigger and the current chamber has the bullet -> death terminal
    if chamber_idx == bullet_pos:
        if current_player_idx == 0:
            g.set_outcome(pull_node, death_p1)
        else:
            g.set_outcome(pull_node, death_p2)
    else:
        # Otherwise, continue with the other player and next chamber
        next_player = 1 - current_player_idx
        next_chamber = (chamber_idx + 1) % 6
        expand(pull_node, next_player, next_chamber, bullet_pos)

# Build subtree for each bullet location (each is a child of the root chance node)
for b in range(6):
    start_node = g.root.children[b]  # node corresponding to "Bullet at chamber b+1"
    # Start with Player 1 acting and chamber index 0 (the first pull checks chamber 1)
    expand(start_node, current_player_idx=0, chamber_idx=0, bullet_pos=b)

# Save the EFG
g.to_efg("russian_roulette.efg")