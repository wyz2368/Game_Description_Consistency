import pygambit as gbt

# Create the game with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# Pre-create outcomes (payoff ordering matches players=["Player 1", "Player 2"])
quit_p1 = g.add_outcome([0, 1], label="Quit by P1")
shot_p1 = g.add_outcome([-1, 1], label="Shot P1")
quit_p2 = g.add_outcome([1, 0], label="Quit by P2")
shot_p2 = g.add_outcome([1, -1], label="Shot P2")

# Initial move at the root: Player 1 chooses to "Quit" or "Pull trigger"
g.append_move(g.root, "Player 1", ["Quit", "Pull trigger"])

# Frontier for iterative tree construction: list of tuples (decision_node, player_index, remaining_chambers)
# player_index: 0 for Player 1, 1 for Player 2
frontier = [(g.root, 0, 6)]

while frontier:
    node, player_idx, remaining = frontier.pop(0)
    # Children of a decision node: [Quit child, Pull trigger child]
    quit_child = node.children[0]
    pull_child = node.children[1]

    # Set the Quit outcome depending on which player is acting
    if player_idx == 0:
        g.set_outcome(quit_child, quit_p1)
    else:
        g.set_outcome(quit_child, quit_p2)

    # Handle the Pull trigger branch
    if remaining == 1:
        # Gun fires for certain
        if player_idx == 0:
            g.set_outcome(pull_child, shot_p1)
        else:
            g.set_outcome(pull_child, shot_p2)
    else:
        # Chance node: "Fire" with probability 1/remaining, "No fire" with probability (remaining-1)/remaining
        g.append_move(pull_child, g.players.chance, ["Fire", "No fire"])
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, remaining),
                                                 gbt.Rational(remaining - 1, remaining)])
        # Set outcome for the "Fire" child (index 0)
        fire_child = pull_child.children[0]
        if player_idx == 0:
            g.set_outcome(fire_child, shot_p1)
        else:
            g.set_outcome(fire_child, shot_p2)

        # "No fire" child (index 1) continues the game with the other player and remaining-1 chambers
        no_fire_child = pull_child.children[1]
        other_idx = 1 - player_idx
        other_name = g.players[other_idx]
        # Append the decision move for the other player at this node
        g.append_move(no_fire_child, other_name, ["Quit", "Pull trigger"])
        # Add it to the frontier to process its children
        frontier.append((no_fire_child, other_idx, remaining - 1))

# Save the EFG
g.to_efg("russian_roulette.efg")