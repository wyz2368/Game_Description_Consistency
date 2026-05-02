import pygambit as gbt

# Create the game with the two players, Player 1 acts first.
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver alternating-players game")

# Pre-create commonly used outcomes (player order: ["Player 1", "Player 2"])
p1_wins = g.add_outcome([1, -1], label="Player 1 wins")
p1_loses = g.add_outcome([-1, 1], label="Player 1 loses")
p1_quits = g.add_outcome([0, 1], label="Player 1 quits")
p2_quits = g.add_outcome([1, 0], label="Player 2 quits")

# Append the initial move at the root for Player 1
g.append_move(g.root, "Player 1", ["Quit", "Pull trigger"])

def expand_decision(node, acting_player_idx, remaining_chambers):
    """
    node: the decision node (already has children created by a prior append_move)
    acting_player_idx: 0 for Player 1, 1 for Player 2
    remaining_chambers: how many unpulled chambers remain (integer >= 1)
    """
    # Map index to player name
    acting_player_name = g.players[acting_player_idx]
    other_idx = 1 - acting_player_idx

    # Children correspond to the actions in the order they were appended:
    # child 0 => "Quit", child 1 => "Pull trigger"
    # Handle "Quit" action (child 0)
    quit_child = node.children[0]
    if acting_player_idx == 0:
        # Player 1 quits: [0, 1]
        g.set_outcome(quit_child, p1_quits)
    else:
        # Player 2 quits: [1, 0]
        g.set_outcome(quit_child, p2_quits)

    # Handle "Pull trigger" action (child 1)
    pull_node = node.children[1]

    # Set up chance move on the pull_node.
    if remaining_chambers > 1:
        # Two chance outcomes: "Fire" and "No fire"
        g.append_move(pull_node, g.players.chance, ["Fire", "No fire"])
        # Probabilities: Fire = 1/remaining_chambers, No fire = (remaining_chambers-1)/remaining_chambers
        g.set_chance_probs(
            pull_node.infoset,
            [gbt.Rational(1, remaining_chambers),
             gbt.Rational(remaining_chambers - 1, remaining_chambers)]
        )

        # Chance child 0: "Fire" -> acting player dies -> terminal
        fire_child = pull_node.children[0]
        if acting_player_idx == 0:
            # Player 1 dies
            g.set_outcome(fire_child, p1_loses)
        else:
            # Player 2 dies (Player 1 wins)
            g.set_outcome(fire_child, p1_wins)

        # Chance child 1: "No fire" -> play continues with other player and fewer chambers
        no_fire_child = pull_node.children[1]
        # Append the next player's decision at this node
        next_player_name = g.players[other_idx]
        g.append_move(no_fire_child, next_player_name, ["Quit", "Pull trigger"])
        # Recurse: other player acts next, remaining_chambers - 1
        expand_decision(no_fire_child, other_idx, remaining_chambers - 1)

    else:
        # remaining_chambers == 1: the trigger fires for certain
        # Only include "Fire" as a chance action (probability 1)
        g.append_move(pull_node, g.players.chance, ["Fire"])
        g.set_chance_probs(pull_node.infoset, [gbt.Rational(1, 1)])

        # Only one chance child corresponding to "Fire": terminal where acting player dies
        fire_child = pull_node.children[0]
        if acting_player_idx == 0:
            g.set_outcome(fire_child, p1_loses)
        else:
            g.set_outcome(fire_child, p1_wins)

# Start expanding from the root: Player 1 acts first, 6 chambers initially
expand_decision(g.root, acting_player_idx=0, remaining_chambers=6)

# Save the EFG
g.to_efg("revolver_game.efg")