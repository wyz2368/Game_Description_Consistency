import pygambit as gbt

# Create a new extensive-form game with two players P1 and P2.
# Reasoning:
# - There are two players, named "P1" and "P2".
# - A single chance move at the root chooses the loaded chamber (0..5) with equal probability.
# - For a bullet at position k (0-based), the killing pull occurs on turn (k+1).
# - Players alternate: P1 moves on turns 1,3,5; P2 moves on turns 2,4,6.
# - At each decision node the acting player can Pull (action 0) or Quit (action 1).
#   We assume "Pull" corresponds to child index 0 and "Quit" to child index 1.
# - If a player Quits, that player gets 0 and the other gets 1.
# - If a player Pulls and the current chamber is loaded, that player dies: payoff -1 to shooter, +1 to the other.
# - If a player Pulls and the chamber is not loaded, play continues to the other player to the next turn.
# - Decision nodes for the same player and same turn across different chance outcomes are in the same infoset,
#   because players observe only the number of past safe pulls (the turn number) and not the chamber position.
g = gbt.Game.new_tree(players=["P1", "P2"],
                      title="Six-chamber Russian roulette (fixed loaded chamber, unobserved)")

# Chance move: six possible loaded-chamber positions (0..5).
g.append_move(g.root, g.players.chance, ["Pos0", "Pos1", "Pos2", "Pos3", "Pos4", "Pos5"])
# Set equal 1/6 probability on each chance branch using Rational.
g.set_chance_probs(g.root.infoset, [
    gbt.Rational(1, 6),
    gbt.Rational(1, 6),
    gbt.Rational(1, 6),
    gbt.Rational(1, 6),
    gbt.Rational(1, 6),
    gbt.Rational(1, 6),
])

# For each chance outcome (Pos0..Pos5) append P1's initial move (turn 1): Pull or Quit.
g.append_move(g.root.children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[1], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[2], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[3], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[4], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[5], "P1", ["Pull", "Quit"])

# When appropriate, append P2's turn-2 moves (these occur after a safe Pull on turn 1).
# They exist for chance outcomes k >= 1 (Pos1..Pos5).
g.append_move(g.root.children[1].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "P2", ["Pull", "Quit"])

# Append P1's turn-3 moves where they exist (after two safe pulls): k >= 2 (Pos2..Pos5).
g.append_move(g.root.children[2].children[0].children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "P1", ["Pull", "Quit"])

# Append P2's turn-4 moves where they exist (after three safe pulls): k >= 3 (Pos3..Pos5).
g.append_move(g.root.children[3].children[0].children[0].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "P2", ["Pull", "Quit"])

# Append P1's turn-5 moves where they exist (after four safe pulls): k >= 4 (Pos4..Pos5).
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "P1", ["Pull", "Quit"])

# Append P2's turn-6 move; this occurs only when k == 5 (Pos5) after five safe pulls.
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "P2", ["Pull", "Quit"])

# Now set up the information sets for nodes that represent the same turn for the same player
# but correspond to different chance outcomes. Players do not observe the chamber position,
# only how many safe pulls have happened (i.e., which turn it is), so these nodes must be grouped.
# Group P1's initial decision nodes (turn 1) across all 6 chance outcomes:
g.set_infoset(g.root.children[1], g.root.children[0].infoset)
g.set_infoset(g.root.children[2], g.root.children[0].infoset)
g.set_infoset(g.root.children[3], g.root.children[0].infoset)
g.set_infoset(g.root.children[4], g.root.children[0].infoset)
g.set_infoset(g.root.children[5], g.root.children[0].infoset)

# Group P2's first decision nodes (turn 2) across chance outcomes k=1..5:
g.set_infoset(g.root.children[2].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[1].children[0].infoset)

# Group P1's second decision nodes (turn 3) across chance outcomes k=2..5:
g.set_infoset(g.root.children[3].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[2].children[0].children[0].infoset)

# Group P2's second decision nodes (turn 4) across chance outcomes k=3..5:
g.set_infoset(g.root.children[4].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)

# Group P1's third decision nodes (turn 5) across chance outcomes k=4..5:
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].children[0].infoset)

# (P2's turn 6 occurs only when k=5, so there is no multi-node infoset to group.)

# Create outcome objects (to reuse the same labels across many terminals).
# - p1_dies: P1 gets -1, P2 gets +1 (P1 pulled the loaded chamber and died).
# - p2_dies: P1 gets +1, P2 gets -1 (P2 pulled the loaded chamber and died).
# - p1_quit: P1 quits => P1 gets 0, P2 gets 1.
# - p2_quit: P2 quits => P2 gets 0, P1 gets 1.
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_dies = g.add_outcome([1, -1], label="P2 dies")
p1_quit = g.add_outcome([0, 1], label="P1 quits")
p2_quit = g.add_outcome([1, 0], label="P2 quits")

# Assign outcomes to all terminal nodes (both Quit terminals and the "Pull leads to death" terminals).
# k = 0 (Pos0): P1's initial Pull kills (turn 1), Quit gives (0,1).
g.set_outcome(g.root.children[0].children[0], p1_dies)   # Pull -> P1 dies
g.set_outcome(g.root.children[0].children[1], p1_quit)   # Quit -> P1 quits

# k = 1 (Pos1): sequence P1 (turn1) -> P2 (turn2)
g.set_outcome(g.root.children[1].children[0].children[0], p2_dies)  # P2 Pull at turn2 kills P2
g.set_outcome(g.root.children[1].children[0].children[1], p2_quit)  # P2 Quit at turn2
g.set_outcome(g.root.children[1].children[1], p1_quit)              # P1 Quit at turn1

# k = 2 (Pos2): P1 (t1) -> P2 (t2) -> P1 (t3)
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_dies)  # P1 Pull at t3 kills P1
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quit)  # P1 Quit at t3
g.set_outcome(g.root.children[2].children[0].children[1], p2_quit)              # P2 Quit at t2
g.set_outcome(g.root.children[2].children[1], p1_quit)                        # P1 Quit at t1

# k = 3 (Pos3): P1 (t1) -> P2 (t2) -> P1 (t3) -> P2 (t4)
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_dies)  # P2 Pull at t4 kills P2
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quit)  # P2 Quit at t4
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quit)              # P1 Quit at t3
g.set_outcome(g.root.children[3].children[0].children[1], p2_quit)                        # P2 Quit at t2
g.set_outcome(g.root.children[3].children[1], p1_quit)                                  # P1 Quit at t1

# k = 4 (Pos4): P1 (t1) -> P2 (t2) -> P1 (t3) -> P2 (t4) -> P1 (t5)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_dies)  # P1 Pull at t5 kills P1
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quit)  # P1 Quit at t5
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quit)              # P2 Quit at t4
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quit)                        # P1 Quit at t3
g.set_outcome(g.root.children[4].children[0].children[1], p2_quit)                                    # P2 Quit at t2
g.set_outcome(g.root.children[4].children[1], p1_quit)                                                # P1 Quit at t1

# k = 5 (Pos5): P1 (t1) -> P2 (t2) -> P1 (t3) -> P2 (t4) -> P1 (t5) -> P2 (t6)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_dies)  # P2 Pull at t6 kills P2
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quit)  # P2 Quit at t6
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quit)               # P1 Quit at t5
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quit)                           # P2 Quit at t4
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quit)                                       # P1 Quit at t3
g.set_outcome(g.root.children[5].children[0].children[1], p2_quit)                                                   # P2 Quit at t2
g.set_outcome(g.root.children[5].children[1], p1_quit)                                                               # P1 Quit at t1

# Save the EFG to a file.
g.to_efg("russian_roulette.efg")