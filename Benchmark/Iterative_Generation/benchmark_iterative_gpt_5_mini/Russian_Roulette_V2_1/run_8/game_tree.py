import pygambit as gbt

# Create game
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating revolver (6-chamber)")

# Pre-create outcomes:
# Player ordering: ["Player 1", "Player 2"]
p1_quits = g.add_outcome([0, 1], label="P1 quits")
p2_quits = g.add_outcome([1, 0], label="P2 quits")
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_dies = g.add_outcome([1, -1], label="P2 dies")

def expand(node, current_player_idx, remaining_chambers):
    """
    Expand the decision node where current_player_idx (0 or 1) moves
    and there are remaining_chambers unpulled chambers left.
    """
    current_player = g.players[current_player_idx]
    # Append the player's move: ["Quit", "Pull"]
    g.append_move(node, current_player, ["Quit", "Pull"])

    # After append_move, children exist:
    # child 0 -> "Quit"
    # child 1 -> "Pull"
    quit_node = node.children[0]
    pull_node = node.children[1]

    # Set outcome for quitting:
    if current_player_idx == 0:
        # Player 1 quits: [0,1]
        g.set_outcome(quit_node, p1_quits)
    else:
        # Player 2 quits: [1,0]
        g.set_outcome(quit_node, p2_quits)

    # Now handle pulling:
    # Chance actions: always include "Fire"; include "Empty" only if remaining_chambers > 1
    if remaining_chambers > 1:
        chance_actions = ["Fire", "Empty"]
    else:
        # remaining_chambers == 1 -> certain fire; do not include zero-prob action
        chance_actions = ["Fire"]

    g.append_move(pull_node, g.players.chance, chance_actions)

    # Set chance probabilities
    if remaining_chambers > 1:
        # Fire prob = 1 / remaining_chambers
        g.set_chance_probs(pull_node.infoset,
                           [gbt.Rational(1, remaining_chambers),
                            gbt.Rational(remaining_chambers - 1, remaining_chambers)])
    else:
        # Certain fire
        g.set_chance_probs(pull_node.infoset, [gbt.Rational(1, 1)])

    # Handle the "Fire" child: shooter dies -> terminal
    fire_node = pull_node.children[0]
    if current_player_idx == 0:
        g.set_outcome(fire_node, p1_dies)
    else:
        g.set_outcome(fire_node, p2_dies)

    # Handle the "Empty" child (if present): continue with other player and remaining_chambers - 1
    if remaining_chambers > 1:
        empty_node = pull_node.children[1]
        expand(empty_node, 1 - current_player_idx, remaining_chambers - 1)

# Expand from the root: Player 1 moves first, 6 chambers initially
expand(g.root, current_player_idx=0, remaining_chambers=6)

# Save the EFG
g.to_efg("revolver_game.efg")