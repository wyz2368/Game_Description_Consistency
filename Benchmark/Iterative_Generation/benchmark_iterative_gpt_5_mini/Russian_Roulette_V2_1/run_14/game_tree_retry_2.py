import pygambit as gbt

# Create game with the specified player order
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# Pre-create outcome objects to reuse
# Payoffs ordered as [Player 1, Player 2]
p1_quits = g.add_outcome([0, 1], label="Player1 quits, Player2 wins")
p2_quits = g.add_outcome([1, 0], label="Player2 quits, Player1 wins")
p1_dies = g.add_outcome([-1, 1], label="Player1 dies")
p2_dies = g.add_outcome([1, -1], label="Player2 dies")

def build_turn(node, current_player_idx, remaining_chambers):
    """
    Recursively build the decision and subsequent chance branches.
    node: Node at which the current player chooses.
    current_player_idx: 0 for Player 1, 1 for Player 2.
    remaining_chambers: number of chambers not yet pulled (integer >= 1).
    """
    # Use the Player object directly (no .name)
    player = g.players[current_player_idx]

    # Append the decision move for the current player: Quit or Pull
    g.append_move(node, player, ["Quit", "Pull"])

    # Handle "Quit" child (children[0])
    quit_node = node.children[0]
    if current_player_idx == 0:
        # Player 1 quits -> [0,1]
        g.set_outcome(quit_node, p1_quits)
    else:
        # Player 2 quits -> [1,0]
        g.set_outcome(quit_node, p2_quits)

    # Handle "Pull" child (children[1])
    pull_node = node.children[1]

    # Prepare chance actions: "Fire" always present. "Click" only if remaining_chambers > 1
    if remaining_chambers > 1:
        chance_actions = ["Fire", "Click"]
        # Append chance move and set probabilities 1/remaining and (remaining-1)/remaining
        g.append_move(pull_node, g.players.chance, chance_actions)
        probs = [gbt.Rational(1, remaining_chambers),
                 gbt.Rational(remaining_chambers - 1, remaining_chambers)]
        g.set_chance_probs(pull_node.infoset, probs)

        # Fire child: current player dies
        fire_node = pull_node.children[0]
        if current_player_idx == 0:
            g.set_outcome(fire_node, p1_dies)
        else:
            g.set_outcome(fire_node, p2_dies)

        # Click child: continue with other player and one fewer chamber
        click_node = pull_node.children[1]
        next_player_idx = 1 - current_player_idx
        build_turn(click_node, next_player_idx, remaining_chambers - 1)

    else:
        # remaining_chambers == 1: only "Fire" with probability 1 (no "Click" branch)
        chance_actions = ["Fire"]
        g.append_move(pull_node, g.players.chance, chance_actions)
        g.set_chance_probs(pull_node.infoset, [gbt.Rational(1, 1)])

        # Fire child: current player dies (no continuation possible)
        fire_node = pull_node.children[0]
        if current_player_idx == 0:
            g.set_outcome(fire_node, p1_dies)
        else:
            g.set_outcome(fire_node, p2_dies)

# Build the tree starting from the root: Player 1 starts, 6 chambers remaining
build_turn(g.root, current_player_idx=0, remaining_chambers=6)

# Save the EFG
g.to_efg("russian_roulette.efg")