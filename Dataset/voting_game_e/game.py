import pygambit as gbt
import itertools

# Create the game with the required player order
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Sequential Borda voting: Player 2 votes first, then Player 1")

# Generate all strict orderings (ballots) of candidates A, B, C in a deterministic order
ballots = ['>'.join(p) for p in itertools.permutations(["A", "B", "C"])]

# Player 2 moves first at the root, choosing one of the 6 ballots
g.append_move(g.root, "Player 2", ballots)

# For each of Player 2's child nodes, Player 1 chooses a ballot (6 actions)
for p2_node in g.root.children:
    g.append_move(p2_node, "Player 1", ballots)

# Predefine outcomes for each possible winner to reuse the Outcome objects
# Player order is ["Player 1", "Player 2"], so payoffs must be [Player1_payoff, Player2_payoff]
outcome_A = g.add_outcome([2, 0], label="A wins")  # Player1 prefers A best; Player2 least for A
outcome_B = g.add_outcome([1, 1], label="B wins")  # Middle preference for both
outcome_C = g.add_outcome([0, 2], label="C wins")  # Player2 prefers C best; Player1 least for C

# Helper to compute the winner given two ballot strings like "A>B>C"
def compute_winner(ballot1_str, ballot2_str):
    # Initialize scores
    scores = {"A": 0, "B": 0, "C": 0}
    # Parse ballots
    b1 = ballot1_str.split('>')
    b2 = ballot2_str.split('>')
    # Borda points: first=2, second=1, third=0
    for idx, candidate in enumerate(b1):
        if idx == 0:
            scores[candidate] += 2
        elif idx == 1:
            scores[candidate] += 1
    for idx, candidate in enumerate(b2):
        if idx == 0:
            scores[candidate] += 2
        elif idx == 1:
            scores[candidate] += 1
    # Determine highest score and apply tie-break A > B > C
    max_score = max(scores.values())
    for candidate in ["A", "B", "C"]:
        if scores[candidate] == max_score:
            return candidate
    # Should never reach here
    return "A"

# Iterate over all terminal nodes and set outcomes according to the winner
for i, p2_node in enumerate(g.root.children):
    p2_ballot = ballots[i]
    for j, p1_node in enumerate(p2_node.children):
        p1_ballot = ballots[j]
        winner = compute_winner(p1_ballot, p2_ballot)  # note: each player's ballot contributes; order doesn't matter for scores
        if winner == "A":
            g.set_outcome(p1_node, outcome_A)
        elif winner == "B":
            g.set_outcome(p1_node, outcome_B)
        else:  # winner == "C"
            g.set_outcome(p1_node, outcome_C)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['A>C>B'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['B>A>C'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['B>C>A'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['C>A>B'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['C>B>A'], g.root.children['A>B>C'].infoset)

# Save the EFG file
g.to_efg("borda_sequential_vote_game.efg")