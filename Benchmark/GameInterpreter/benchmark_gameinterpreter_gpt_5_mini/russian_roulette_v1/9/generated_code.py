import pygambit as gbt

# Build the extensive-form game for 2 players playing with a 6-chamber revolver.
# Players: P1 (moves on odd turns) and P2 (moves on even turns).
#
# Reasoning (written as code comments, step-by-step):
# 1) Chance selects which chamber (1..6) contains the bullet. Each chamber has probability 1/6.
# 2) For each chance outcome we create P1's first decision node (turn 1).
#    At every decision node a player has two actions: "Pull" or "Quit".
#    - Quit: the quitting player withdraws and gets 0; the other player wins and gets 1.
#    - Pull: if the current chamber is the loaded one, the pulling player dies (payoff -1),
#            the other player wins (payoff +1). Otherwise, play passes to the other player
#            and the sequence continues to the next turn.
# 3) We explicitly construct the full tree up to the maximal possible sequence of pulls
#    (which can reach the 6th pull). We avoid loops and recursion by constructing every
#    branch explicitly. We also ensure the information-set grouping described in the prompt
#    is created only after the relevant moves exist.
#
# The code below follows these steps without using loops or the '+' operator.

g = gbt.Game.new_tree(players=["P1", "P2"],
                      title="6-chamber Russian roulette (alternating turns)")

# 1) Chance chooses the loaded chamber (1..6). All equally likely (1/6).
g.append_move(g.root, g.players.chance, ["Ch1", "Ch2", "Ch3", "Ch4", "Ch5", "Ch6"])
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                                     gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# 2) Append P1's turn-1 move at each chance outcome: actions ["Pull", "Quit"].
g.append_move(g.root.children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[1], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[2], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[3], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[4], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[5], "P1", ["Pull", "Quit"])

# Outcomes commonly used
p1_quits = g.add_outcome([0, 1], label="P1 quits (P2 wins)")
p2_quits = g.add_outcome([1, 0], label="P2 quits (P1 wins)")
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_dies = g.add_outcome([1, -1], label="P2 dies")

# Set outcomes for P1's Quit actions on turn 1 (present at every root.children[i].children[1]).
g.set_outcome(g.root.children[0].children[1], p1_quits)
g.set_outcome(g.root.children[1].children[1], p1_quits)
g.set_outcome(g.root.children[2].children[1], p1_quits)
g.set_outcome(g.root.children[3].children[1], p1_quits)
g.set_outcome(g.root.children[4].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[1], p1_quits)

# Handle P1's Pull on turn 1:
# - If bullet is in chamber 1 (root.children[0]), Pull kills P1 immediately.
g.set_outcome(g.root.children[0].children[0], p1_dies)

# - For the other chance outcomes (2..6), P1's Pull is safe and play passes to P2 (turn 2).
#   So we must append P2's turn-2 move at those pull nodes.
g.append_move(g.root.children[1].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "P2", ["Pull", "Quit"])

# Set P2's Quit outcomes at turn 2 (when present).
g.set_outcome(g.root.children[1].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[2].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[3].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[4].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[5].children[0].children[1], p2_quits)

# P2's Pull on turn 2:
# - If bullet is in chamber 2 (root.children[1]), P2 Pull kills P2 immediately.
g.set_outcome(g.root.children[1].children[0].children[0], p2_dies)

# - For chance outcomes 3..6, P2's Pull is safe and passes back to P1 (turn 3).
#   Append P1's turn-3 move at those nodes.
g.append_move(g.root.children[2].children[0].children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "P1", ["Pull", "Quit"])

# Set P1's Quit outcomes at turn 3 (when present).
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quits)

# P1's Pull on turn 3:
# - If bullet is in chamber 3 (root.children[2]), P1 Pull kills P1.
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_dies)

# - For chance outcomes 4..6, P1's Pull is safe and play passes to P2 (turn 4).
#   Append P2's turn-4 moves at those nodes.
g.append_move(g.root.children[3].children[0].children[0].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "P2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "P2", ["Pull", "Quit"])

# Set P2's Quit outcomes at turn 4 (when present).
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quits)

# P2's Pull on turn 4:
# - If bullet is in chamber 4 (root.children[3]), P2 Pull kills P2.
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_dies)

# - For chance outcomes 5..6, P2's Pull is safe and play passes back to P1 (turn 5).
#   Append P1's turn-5 moves at those nodes.
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "P1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "P1", ["Pull", "Quit"])

# Set P1's Quit outcomes at turn 5 (when present).
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quits)

# P1's Pull on turn 5:
# - If bullet is in chamber 5 (root.children[4]), P1 Pull kills P1.
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_dies)

# - For chance outcome 6, P1's Pull is safe and passes to P2 for the 6th pull (turn 6).
#   Append P2's turn-6 move for the only remaining branch (bullet in chamber 6).
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "P2", ["Pull", "Quit"])

# Set P2's Quit outcome at turn 6 (if P2 chooses to quit instead of pulling).
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quits)

# P2's Pull on turn 6:
# - If bullet is in chamber 6 (root.children[5]), P2 Pull kills P2.
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_dies)

# 4) Set the information sets as specified in the prompt. Each infoset grouping must be done
#    only after the relevant moves exist. The lines below follow the provided grouping code.

# Group P1's turn 1 nodes (all 6 chance outcomes) into one infoset:
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Group P2's turn 2 nodes (chance outcomes 2..6) into one infoset:
g.set_infoset(g.root.children[2].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[1].children[0].infoset)

# Group P1's turn 3 nodes (chance outcomes 3..6) into one infoset:
g.set_infoset(g.root.children[3].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[2].children[0].children[0].infoset)

# Group P2's turn 4 nodes (chance outcomes 4..6) into one infoset:
g.set_infoset(g.root.children[4].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)

# Group P1's turn 5 nodes (chance outcomes 5..6) into one infoset:
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].children[0].infoset)

# Save the EFG to file
g.to_efg("russian_roulette_6chambers.efg")