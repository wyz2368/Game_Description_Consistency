import pygambit as gbt

# Create game
players = ["Player 1", "Player 2"]
g = gbt.Game.new_tree(players=players, title="Russian Roulette (6-chamber)")

# Add chance move at the root: which chamber (1..6) contains the bullet
g.append_move(g.root, g.players.chance, [f"Chamber {i}" for i in range(1, 7)])
# Set uniform probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])

# Payoff mapping: L = -1 (shoots oneself), D = 0 (quits and loses), W = 1 (wins)
# Pre-create outcome objects to reuse
p1_dies = g.add_outcome([-1, 1], label="P1 dies (L)")
p2_dies = g.add_outcome([1, -1], label="P2 dies (L)")
p1_quits = g.add_outcome([0, 1], label="P1 quits (D)")
p2_quits = g.add_outcome([1, 0], label="P2 quits (D)")

# Recursively expand the subtree for a given chance child (bullet_pos)
def expand_from(node, current_player_idx, chamber_idx, bullet_pos):
    """
    node: the current decision node (Node)
    current_player_idx: 0 for Player 1, 1 for Player 2
    chamber_idx: current chamber index that would be fired if someone pulls (1..6)
    bullet_pos: which chamber contains the bullet (1..6), fixed by chance
    """
    # Append the move for the current player with actions "Pull" and "Quit"
    g.append_move(node, players[current_player_idx], ["Pull", "Quit"])
    pull_node = node.children[0]  # child corresponding to "Pull"
    quit_node = node.children[1]  # child corresponding to "Quit"

    # "Quit" is terminal: quitter gets D=0, opponent gets W=1
    if current_player_idx == 0:
        g.set_outcome(quit_node, p1_quits)
    else:
        g.set_outcome(quit_node, p2_quits)

    # "Pull": if current chamber is the bullet -> shooter dies (L), else continue
    if chamber_idx == bullet_pos:
        # shooter dies immediately
        if current_player_idx == 0:
            g.set_outcome(pull_node, p1_dies)
        else:
            g.set_outcome(pull_node, p2_dies)
    else:
        # advance chamber (wrap 6 -> 1) and pass turn to other player
        next_chamber = chamber_idx + 1 if chamber_idx < 6 else 1
        next_player_idx = 1 - current_player_idx
        expand_from(pull_node, next_player_idx, next_chamber, bullet_pos)

# For each chance outcome (bullet position), expand the game starting with chamber 1 and Player 1
for idx, chance_child in enumerate(g.root.children, start=1):
    bullet_position = idx  # 1..6
    # Start with chamber 1 and Player 1 to act
    expand_from(chance_child, current_player_idx=0, chamber_idx=1, bullet_pos=bullet_position)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['Chamber 2'], g.root.children['Chamber 1'].infoset)
    g.set_infoset(g.root.children['Chamber 3'], g.root.children['Chamber 1'].infoset)
    g.set_infoset(g.root.children['Chamber 3'].children['Pull'], g.root.children['Chamber 2'].children['Pull'].infoset)
    g.set_infoset(g.root.children['Chamber 4'], g.root.children['Chamber 1'].infoset)
    g.set_infoset(g.root.children['Chamber 4'].children['Pull'], g.root.children['Chamber 2'].children['Pull'].infoset)
    g.set_infoset(g.root.children['Chamber 4'].children['Pull'].children['Pull'], g.root.children['Chamber 3'].children['Pull'].children['Pull'].infoset)
    g.set_infoset(g.root.children['Chamber 5'], g.root.children['Chamber 1'].infoset)
    g.set_infoset(g.root.children['Chamber 5'].children['Pull'], g.root.children['Chamber 2'].children['Pull'].infoset)
    g.set_infoset(g.root.children['Chamber 5'].children['Pull'].children['Pull'], g.root.children['Chamber 3'].children['Pull'].children['Pull'].infoset)
    g.set_infoset(g.root.children['Chamber 5'].children['Pull'].children['Pull'].children['Pull'], g.root.children['Chamber 4'].children['Pull'].children['Pull'].children['Pull'].infoset)
    g.set_infoset(g.root.children['Chamber 6'], g.root.children['Chamber 1'].infoset)
    g.set_infoset(g.root.children['Chamber 6'].children['Pull'], g.root.children['Chamber 2'].children['Pull'].infoset)
    g.set_infoset(g.root.children['Chamber 6'].children['Pull'].children['Pull'], g.root.children['Chamber 3'].children['Pull'].children['Pull'].infoset)
    g.set_infoset(g.root.children['Chamber 6'].children['Pull'].children['Pull'].children['Pull'], g.root.children['Chamber 4'].children['Pull'].children['Pull'].children['Pull'].infoset)
    g.set_infoset(g.root.children['Chamber 6'].children['Pull'].children['Pull'].children['Pull'].children['Pull'], g.root.children['Chamber 5'].children['Pull'].children['Pull'].children['Pull'].children['Pull'].infoset)

replay_infosets(g)

# Save the EFG
g.to_efg("russian_roulette.efg")