import pygambit as gbt
from collections import deque

# Create the game with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating Russian Roulette (6-chamber)")

# Start state: root node, 6 chambers, Player 1 to act (index 0)
start_chambers = 6
queue = deque([(g.root, start_chambers, 0)])

# Helper to produce outcome list in correct player order
def outcome_for_quit(player_idx):
    # quitting player gets 0, other gets 1
    if player_idx == 0:
        return [0, 1]
    else:
        return [1, 0]

def outcome_for_death(player_idx):
    # acting player dies: -1 for acting, +1 for other
    if player_idx == 0:
        return [-1, 1]
    else:
        return [1, -1]

# Expand the tree
while queue:
    node, chambers, p_idx = queue.popleft()
    player_name = g.players[p_idx]  # use player object/name as in examples

    # Append the player's decision (do not pass multiple nodes at once)
    g.append_move(node, player_name, ["Quit", "Pull"])

    # After append_move, children are in order of actions: children[0] => "Quit", children[1] => "Pull"
    quit_child = node.children[0]
    pull_child = node.children[1]

    # Set outcome for quitting
    g.set_outcome(quit_child, g.add_outcome(outcome_for_quit(p_idx), label=f"Player {p_idx+1} quits"))

    # Handle pulling the trigger
    if chambers == 1:
        # Pulling fires for certain -> acting player dies
        g.set_outcome(pull_child, g.add_outcome(outcome_for_death(p_idx), label="Certain death (last chamber)"))
    else:
        # Chance determines if it fires: probability 1/chambers to fire, (chambers-1)/chambers to not fire
        g.append_move(pull_child, g.players.chance, ["Fire", "No fire"])
        # Set chance probabilities on this chance infoset
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, chambers), gbt.Rational(chambers - 1, chambers)])

        fire_child = pull_child.children[0]     # "Fire" branch
        nofire_child = pull_child.children[1]   # "No fire" branch

        # If it fires, acting player dies
        g.set_outcome(fire_child, g.add_outcome(outcome_for_death(p_idx), label="Shot fires"))

        # If it does not fire, one chamber is consumed and play passes to other player
        next_player_idx = 1 - p_idx
        queue.append((nofire_child, chambers - 1, next_player_idx))

# Save the EFG
g.to_efg("alternating_russian_roulette.efg")