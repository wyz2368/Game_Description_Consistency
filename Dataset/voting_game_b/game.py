import pygambit as gbt

# Create the game
g = gbt.Game.new_tree(players=["Player1", "Player2"],
                      title="Borda voting with three candidates (simultaneous ballots modeled sequentially)")

# Define the six strict rankings (ballots)
ballots = [
    "A>B>C",
    "A>C>B",
    "B>A>C",
    "B>C>A",
    "C>A>B",
    "C>B>A"
]

# Append Player1's move at the root (Player1 chooses a ballot)
g.append_move(g.root, "Player1", ballots)

# For each Player1 action/node, append Player2's move (one node at a time)
for p1_node in g.root.children:
    g.append_move(p1_node, "Player2", ballots)

# Create the three outcome objects (A wins, B wins, C wins)
# Player order in the game is ["Player1", "Player2"], so payoffs are [payoff_P1, payoff_P2]
outcome_A_wins = g.add_outcome([2, 0], label="A wins")
outcome_B_wins = g.add_outcome([1, 1], label="B wins")
outcome_C_wins = g.add_outcome([0, 2], label="C wins")

# Payoff mappings for winners
p1_payoff = {"A": 2, "B": 1, "C": 0}
p2_payoff = {"A": 0, "B": 1, "C": 2}

# Helper: map a ballot label to an ordered list of candidates (first, second, third)
def ballot_to_order(ballot_label):
    # ballot_label examples: "A>B>C"
    return ballot_label.split(">")

# For each terminal node (pair of ballots), compute Borda scores, apply tie-breaking, and set the outcome
for i, p1_node in enumerate(g.root.children):
    for j, p2_node in enumerate(p1_node.children):
        # Get the ballots chosen
        p1_ballot = ballots[i]
        p2_ballot = ballots[j]
        p1_order = ballot_to_order(p1_ballot)
        p2_order = ballot_to_order(p2_ballot)

        # Initialize scores
        scores = {"A": 0, "B": 0, "C": 0}

        # Borda points: position 0 -> 2, pos1 -> 1, pos2 -> 0
        for pos, cand in enumerate(p1_order):
            points = 2 - pos
            scores[cand] += points
        for pos, cand in enumerate(p2_order):
            points = 2 - pos
            scores[cand] += points

        # Determine winner: highest score; tie-break priority C > B > A
        max_score = max(scores.values())
        tied = [cand for cand, sc in scores.items() if sc == max_score]
        if len(tied) == 1:
            winner = tied[0]
        else:
            # Apply tie-break: prefer C, then B, then A
            if "C" in tied:
                winner = "C"
            elif "B" in tied:
                winner = "B"
            else:
                winner = "A"

        # Choose the outcome object based on winner and set it at the terminal node
        terminal_node = p2_node  # this is the terminal node after both moves
        if winner == "A":
            g.set_outcome(terminal_node, outcome_A_wins)
        elif winner == "B":
            g.set_outcome(terminal_node, outcome_B_wins)
        else:  # winner == "C"
            g.set_outcome(terminal_node, outcome_C_wins)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['A>C>B'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['B>A>C'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['B>C>A'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['C>A>B'], g.root.children['A>B>C'].infoset)
    g.set_infoset(g.root.children['C>B>A'], g.root.children['A>B>C'].infoset)

# Save the EFG
g.to_efg("borda_voting.efg")