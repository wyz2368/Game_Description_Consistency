import pygambit as gbt

# Create the game with Player 1 moving first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# Add the chance move at the root: which chamber contains the bullet (1..6)
g.append_move(g.root, g.players.chance, [f"Chamber {i+1}" for i in range(6)])
# Set equal probability 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Helper to add outcomes with correct ordering
def outcome_quit(quitter_index):
    # quitter gets 0, other gets 1
    if quitter_index == 0:
        return g.add_outcome([0, 1], label="Quit: P1 quits -> P2 wins")
    else:
        return g.add_outcome([1, 0], label="Quit: P2 quits -> P1 wins")

def outcome_death(shooter_index):
    # shooter gets -1, other gets +1
    if shooter_index == 0:
        return g.add_outcome([-1, 1], label="Death: P1 shot -> P2 wins")
    else:
        return g.add_outcome([1, -1], label="Death: P2 shot -> P1 wins")

# Recursive builder for the subtree after a given chance outcome (bullet_pos fixed).
# node: current decision node (already appended); current_player_index: 0 or 1;
# current_chamber: index 0..5; bullet_pos: index 0..5
def build_subtree(node, current_player_index, current_chamber, bullet_pos):
    # Append the current player's move at this node with actions ["Pull", "Quit"]
    g.append_move(node, g.players[current_player_index], ["Pull", "Quit"])
    # After append_move, node.children[0] corresponds to "Pull", node.children[1] to "Quit"
    pull_child = node.children[0]
    quit_child = node.children[1]

    # Handle Quit: immediate terminal outcome
    g.set_outcome(quit_child, outcome_quit(current_player_index))

    # Handle Pull:
    if current_chamber % 6 == bullet_pos:
        # Bullet is in the current chamber -> shooter dies
        g.set_outcome(pull_child, outcome_death(current_player_index))
    else:
        # Shooter survives -> continue with the other player and advanced chamber
        next_player = 1 - current_player_index
        next_chamber = (current_chamber + 1) % 6
        # Recursively build from the pull_child (which is a terminal node until we append a move)
        build_subtree(pull_child, next_player, next_chamber, bullet_pos)

# For each chance branch (bullet position), build the deterministic subtree.
# Root has 6 children corresponding to each chamber action; index i corresponds to bullet_pos = i.
for bullet_pos, chance_child in enumerate(g.root.children):
    # Start with Player 1 to act on that branch; current chamber index starts at 0
    build_subtree(chance_child, current_player_index=0, current_chamber=0, bullet_pos=bullet_pos)

# Save the EFG
g.to_efg("revolver.efg")