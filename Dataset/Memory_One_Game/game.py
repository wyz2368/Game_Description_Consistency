import pygambit as gbt

# Create the game with players A and B
g = gbt.Game.new_tree(players=["A", "B"],
                      title="6-move alternating X/Y game (A moves 1,3,5; B moves 2,4,6)")

# Frontier holds tuples (node, historyA, historyB)
frontier = [(g.root, [], [])]

# Build the tree for 6 moves
for move in range(1, 7):  # moves 1..6
    player = "A" if (move % 2) == 1 else "B"
    new_frontier = []
    for node, histA, histB in frontier:
        # Append a binary choice X/Y for this node (one node at a time)
        g.append_move(node, player, ["X", "Y"])
        # For each action, capture the child node and updated histories
        for i, action in enumerate(["X", "Y"]):
            child = node.children[i]
            if player == "A":
                new_histA = histA + [action]
                new_histB = histB
            else:
                new_histA = histA
                new_histB = histB + [action]
            new_frontier.append((child, new_histA, new_histB))
    frontier = new_frontier

# frontier now contains all terminal nodes at depth 6
# For each terminal node compute payoffs and set outcome
for node, histA, histB in frontier:
    # histA and histB should each have length 3
    scoreA = 0
    scoreB = 0
    for a_choice, b_choice in zip(histA, histB):
        if a_choice == b_choice:
            scoreA += 1
            scoreB += 1
    outcome = g.add_outcome([scoreA, scoreB], label=f"payoffs_{scoreA}_{scoreB}")
    g.set_outcome(node, outcome)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['X'].children['X'].children['X'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['X'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['X'].children['X'].children['Y'].children['Y'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['X'].children['Y'].children['X'].children['X'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['X'].children['Y'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['X'].children['Y'].children['Y'], g.root.children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['X'].children['Y'].children['Y'].children['X'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['X'].children['Y'].children['Y'].children['Y'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'], g.root.children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['X'].children['X'], g.root.children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['X'].children['X'].children['X'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['X'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['X'].children['Y'].children['X'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['X'].children['Y'].children['Y'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['Y'], g.root.children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['Y'].children['X'], g.root.children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['Y'].children['X'].children['X'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['Y'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['Y'].children['Y'], g.root.children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['Y'].children['Y'].children['X'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['X'].children['Y'].children['Y'].children['Y'].children['Y'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'], g.root.children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['X'], g.root.children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['X'].children['X'], g.root.children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['X'].children['X'].children['X'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['X'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['X'].children['Y'].children['X'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['X'].children['Y'].children['Y'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['Y'].children['X'], g.root.children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['Y'].children['X'].children['X'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['Y'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['Y'].children['Y'], g.root.children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['Y'].children['Y'].children['X'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['X'].children['Y'].children['Y'].children['Y'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'], g.root.children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['X'], g.root.children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['X'].children['X'], g.root.children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['X'].children['X'].children['X'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['X'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['X'].children['Y'].children['X'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['X'].children['Y'].children['Y'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['Y'], g.root.children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['Y'].children['X'], g.root.children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['Y'].children['X'].children['X'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['Y'].children['X'].children['Y'], g.root.children['X'].children['X'].children['X'].children['X'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['Y'].children['Y'], g.root.children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['Y'].children['Y'].children['X'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)
    g.set_infoset(g.root.children['Y'].children['Y'].children['Y'].children['Y'].children['Y'], g.root.children['X'].children['X'].children['X'].children['Y'].children['X'].infoset)

replay_infosets(g)

# Save the EFG
g.to_efg("alternating_xy_game.efg")