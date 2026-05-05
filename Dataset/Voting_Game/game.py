import pygambit as gbt

# Create the game with the correct player order
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Two-player Borda voting (3 candidates A,B,C)")

# All strict rankings (ballots) as action labels
ballots = ["A>B>C", "A>C>B", "B>A>C", "B>C>A", "C>A>B", "C>B>A"]

# Player 1 moves at the root
g.append_move(g.root, "Player 1", ballots)

# For each child (each Player 1 ballot), append a Player 2 move
for node in g.root.children:
    g.append_move(node, "Player 2", ballots)

# Create outcome objects for each possible winning candidate.
# Payoffs follow player order ["Player 1", "Player 2"].
# Player 1: A=2, B=1, C=0
# Player 2: C=2, B=1, A=0
outcome_A = g.add_outcome([2, 0], label="A wins")
outcome_B = g.add_outcome([1, 1], label="B wins")
outcome_C = g.add_outcome([0, 2], label="C wins")

# Helper to convert a ballot label to Borda scores for each candidate
def ballot_scores(ballot_label):
    # ballot_label example: "A>B>C"
    order = ballot_label.split(">")
    scores = {"A": 0, "B": 0, "C": 0}
    scores[order[0]] = 2
    scores[order[1]] = 1
    scores[order[2]] = 0
    return scores

# Tie-breaking priority: A > B > C
priority = ["A", "B", "C"]

# For each pair of ballots (player1_ballot, player2_ballot), compute winner and set outcome
for i, node1 in enumerate(g.root.children):
    b1 = ballots[i]
    s1 = ballot_scores(b1)
    for j, terminal_node in enumerate(node1.children):
        b2 = ballots[j]
        s2 = ballot_scores(b2)
        # Total scores by candidate
        total = {c: s1[c] + s2[c] for c in ["A", "B", "C"]}
        maxscore = max(total.values())
        tied = [c for c, sc in total.items() if sc == maxscore]
        # Apply priority tie-break
        for c in priority:
            if c in tied:
                winner = c
                break
        # Select the corresponding outcome object
        if winner == "A":
            outcome = outcome_A
        elif winner == "B":
            outcome = outcome_B
        else:
            outcome = outcome_C
        # Set outcome at the terminal node
        g.set_outcome(terminal_node, outcome)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['A>C>B'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['B>A>C'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['B>C>A'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['C>A>B'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['C>B>A'], g.root.children['A>B>C'].infoset)

# Save the EFG to a file
g.to_efg("borda_two_player.efg")