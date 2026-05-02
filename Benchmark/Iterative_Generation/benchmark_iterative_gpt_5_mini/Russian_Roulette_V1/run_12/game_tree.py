import pygambit as gbt

# Create the game with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian Roulette (alternating turns)")

# Add chance node at root: which chamber (1..6) contains the bullet
num_chambers = 6
chamber_actions = [f"Chamber {i}" for i in range(1, num_chambers + 1)]
g.append_move(g.root, g.players.chance, chamber_actions)

# Set equal probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, num_chambers) for _ in range(num_chambers)])

# Helper: return opponent player name given current player index 0 or 1
def opponent_index(idx):
    return 1 - idx

# Recursive builder for a particular chance branch (bullet_pos)
def build_branch(node, chamber_idx, bullet_pos, player_idx):
    """
    node: the current node where player player_idx chooses
    chamber_idx: current chamber index to be tested if 'Pull' is chosen (1-based)
    bullet_pos: fixed bullet position for this chance branch
    player_idx: 0 for "Player 1", 1 for "Player 2"
    """
    # Append the player's move at this node with two actions: Pull or Quit
    player_name = g.players[player_idx]  # yields "Player 1" or "Player 2"
    g.append_move(node, player_name, ["Pull", "Quit"])

    # After append_move, children are created in the same order as actions:
    # child 0 = "Pull", child 1 = "Quit"
    pull_child = node.children[0]
    quit_child = node.children[1]

    # Quit outcome: quitter gets 0, other gets 1
    if player_idx == 0:
        quit_payoff = [0, 1]  # Player1 quits -> [0,1]
    else:
        quit_payoff = [1, 0]  # Player2 quits -> [1,0]
    g.set_outcome(quit_child, g.add_outcome(quit_payoff, label=f"Quit at chamber {chamber_idx} (player {player_name})"))

    # Pull action
    if chamber_idx == bullet_pos:
        # Shot: shooter dies -> shooter -1, other +1
        if player_idx == 0:
            shot_payoff = [-1, 1]  # Player1 shot
        else:
            shot_payoff = [1, -1]  # Player2 shot
        g.set_outcome(pull_child, g.add_outcome(shot_payoff, label=f"Shot at chamber {chamber_idx} (player {player_name} dies)"))
    else:
        # Safe pull: continue to next chamber with the other player's decision
        next_player_idx = opponent_index(player_idx)
        build_branch(pull_child, chamber_idx + 1, bullet_pos, next_player_idx)

# For each chance branch (child of root), build the alternating decision subtree
# The root's children correspond to the chance actions "Chamber 1" .. "Chamber 6"
for b_idx, chance_child in enumerate(g.root.children, start=1):
    # b_idx is the bullet position for this branch (1..6)
    # Start the play with chamber index 1 and Player 1's turn
    build_branch(chance_child, chamber_idx=1, bullet_pos=b_idx, player_idx=0)

# Save the EFG
g.to_efg("russian_roulette.efg")