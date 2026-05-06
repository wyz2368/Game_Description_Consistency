import pygambit as gbt
from itertools import permutations

# Create the game
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Two-player Borda voting (3 candidates): Player 1 moves first, Player 2 moves second")

# All strict rankings (permutations) as action labels, and keep the permutation tuples in the same order
perm_tuples = list(permutations(["A", "B", "C"]))  # e.g., ('A','B','C'), ...
action_labels = [">".join(p) for p in perm_tuples]  # "A>B>C", etc.

# Append Player 1's move at the root (one node)
g.append_move(g.root, "Player 1", action_labels)

# Helper to compute the winner given two ranking tuples
def compute_winner(r1, r2):
    # Borda points: first = 2, second = 1, third = 0
    scores = {"A": 0, "B": 0, "C": 0}
    # Add Player 1's points
    scores[r1[0]] += 2
    scores[r1[1]] += 1
    # Third gets 0 automatically
    # Add Player 2's points
    scores[r2[0]] += 2
    scores[r2[1]] += 1

    # Find candidates with max score
    max_score = max(scores.values())
    tied = [c for c, s in scores.items() if s == max_score]

    # Tie-breaking: prefer A over B and C, and B over C
    for preferred in ["A", "B", "C"]:
        if preferred in tied:
            return preferred
    # (should never reach here)
    return tied[0]

# Define outcomes (payoffs depend only on winner)
# Player 1 payoffs: A -> 2, C -> 1, B -> 0
# Player 2 payoffs: B -> 2, C -> 1, A -> 0
outcome_A = g.add_outcome([2, 0], label="A wins")
outcome_B = g.add_outcome([0, 2], label="B wins")
outcome_C = g.add_outcome([1, 1], label="C wins")

# For each Player 1 action-node, append a Player 2 move (do this one node at a time)
for i, p1_node in enumerate(g.root.children):
    g.append_move(p1_node, "Player 2", action_labels)
    # Now set outcomes for each of Player 2's action branches
    for j, p2_child in enumerate(p1_node.children):
        p1_rank = perm_tuples[i]
        p2_rank = perm_tuples[j]
        winner = compute_winner(p1_rank, p2_rank)
        if winner == "A":
            g.set_outcome(p2_child, outcome_A)
        elif winner == "B":
            g.set_outcome(p2_child, outcome_B)
        else:  # "C"
            g.set_outcome(p2_child, outcome_C)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['A>C>B'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['B>A>C'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['B>C>A'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['C>A>B'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['C>B>A'], g.root.children['A>B>C'].infoset)

# Save the EFG
g.to_efg("borda_three_candidates.efg")