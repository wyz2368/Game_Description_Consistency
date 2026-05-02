import pygambit as gbt

# Create game and players
g = gbt.Game.new_tree(players=["Player1", "Player2"],
                      title="Alternating revolver (6 chambers)")

# Chance: choose which chamber (1..6) contains the bullet; we index 0..5.
# Actions labeling the 6 possible loaded-chamber outcomes.
g.append_move(g.root, g.players.chance, ["Chamber0", "Chamber1", "Chamber2", "Chamber3", "Chamber4", "Chamber5"])
# Set equal probabilities 1/6 for each chamber.
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Prepare outcome objects to reuse
# If a player quits, the quitter gets 0 and the other player gets 1.
p1_quit = g.add_outcome([0, 1], label="P1 quits")
p2_quit = g.add_outcome([1, 0], label="P2 quits")
# If a player shoots himself, he gets -1 and the other player gets 1.
p1_die = g.add_outcome([-1, 1], label="P1 dies")
p2_die = g.add_outcome([1, -1], label="P2 dies")

# Reasoning:
# - At start the current chamber is the first chamber to be fired.
# - If chance selected chamber i (0-based), the bullet will fire on the (i+1)-th pull.
# - We explicitly construct the sequence of Pull/Quit moves along each chance branch.
# - Action order is ["Pull", "Quit"] so Pull is child 0 and Quit is child 1.
# - For each branch we set quit outcomes on the Quit child (children[1]).
# - If the Pull at a given step is the fatal pull for that branch, set the Pull child to be terminal with the appropriate death outcome.
# - Otherwise, append the next player's decision at the Pull child and continue.

# ---------- Branch for loaded chamber 0 (bullet on first pull) ----------
# Player1 moves at root.children[0]
g.append_move(g.root.children[0], "Player1", ["Pull", "Quit"])
# If Player1 quits: P1 gets 0, P2 gets 1.
g.set_outcome(g.root.children[0].children[1], p1_quit)
# Pull child: since this is the first pull and chamber 0 is loaded, pulling kills P1.
g.set_outcome(g.root.children[0].children[0], p1_die)

# ---------- Branch for loaded chamber 1 (bullet on second pull) ----------
g.append_move(g.root.children[1], "Player1", ["Pull", "Quit"])
g.set_outcome(g.root.children[1].children[1], p1_quit)
# Player1 Pull is safe in this branch, so append Player2's move at that Pull child.
g.append_move(g.root.children[1].children[0], "Player2", ["Pull", "Quit"])
# If Player2 quits: P2 gets 0, P1 gets 1.
g.set_outcome(g.root.children[1].children[0].children[1], p2_quit)
# Player2 Pull is the fatal second pull for this branch (loaded chamber 1).
g.set_outcome(g.root.children[1].children[0].children[0], p2_die)

# ---------- Branch for loaded chamber 2 (bullet on third pull) ----------
g.append_move(g.root.children[2], "Player1", ["Pull", "Quit"])
g.set_outcome(g.root.children[2].children[1], p1_quit)
# First pull (P1) safe -> Player2 decision
g.append_move(g.root.children[2].children[0], "Player2", ["Pull", "Quit"])
g.set_outcome(g.root.children[2].children[0].children[1], p2_quit)
# Second pull (P2) safe -> Player1 decision
g.append_move(g.root.children[2].children[0].children[0], "Player1", ["Pull", "Quit"])
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quit)
# Third pull (P1) is fatal in this branch
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_die)

# ---------- Branch for loaded chamber 3 (bullet on fourth pull) ----------
g.append_move(g.root.children[3], "Player1", ["Pull", "Quit"])
g.set_outcome(g.root.children[3].children[1], p1_quit)
# First pull safe -> Player2
g.append_move(g.root.children[3].children[0], "Player2", ["Pull", "Quit"])
g.set_outcome(g.root.children[3].children[0].children[1], p2_quit)
# Second pull safe -> Player1
g.append_move(g.root.children[3].children[0].children[0], "Player1", ["Pull", "Quit"])
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quit)
# Third pull safe -> Player2
g.append_move(g.root.children[3].children[0].children[0].children[0], "Player2", ["Pull", "Quit"])
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quit)
# Fourth pull (P2) is fatal in this branch
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_die)

# ---------- Branch for loaded chamber 4 (bullet on fifth pull) ----------
g.append_move(g.root.children[4], "Player1", ["Pull", "Quit"])
g.set_outcome(g.root.children[4].children[1], p1_quit)
# First pull safe -> Player2
g.append_move(g.root.children[4].children[0], "Player2", ["Pull", "Quit"])
g.set_outcome(g.root.children[4].children[0].children[1], p2_quit)
# Second pull safe -> Player1
g.append_move(g.root.children[4].children[0].children[0], "Player1", ["Pull", "Quit"])
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quit)
# Third pull safe -> Player2
g.append_move(g.root.children[4].children[0].children[0].children[0], "Player2", ["Pull", "Quit"])
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quit)
# Fourth pull safe -> Player1
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "Player1", ["Pull", "Quit"])
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quit)
# Fifth pull (P1) is fatal in this branch
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_die)

# ---------- Branch for loaded chamber 5 (bullet on sixth pull) ----------
g.append_move(g.root.children[5], "Player1", ["Pull", "Quit"])
g.set_outcome(g.root.children[5].children[1], p1_quit)
# 1st -> Player2
g.append_move(g.root.children[5].children[0], "Player2", ["Pull", "Quit"])
g.set_outcome(g.root.children[5].children[0].children[1], p2_quit)
# 2nd -> Player1
g.append_move(g.root.children[5].children[0].children[0], "Player1", ["Pull", "Quit"])
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quit)
# 3rd -> Player2
g.append_move(g.root.children[5].children[0].children[0].children[0], "Player2", ["Pull", "Quit"])
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quit)
# 4th -> Player1
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "Player1", ["Pull", "Quit"])
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quit)
# 5th -> Player2
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "Player2", ["Pull", "Quit"])
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quit)
# 6th pull (P2) is fatal in this branch
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_die)

# ---------- Set information sets for imperfect information ----------
# All Player1 initial decision nodes (one per chance outcome) are indistinguishable.
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Player2 nodes after one safe pull exist for branches 1..5.
# Use branch 1's Player2 node as the representative infoset and link others to it.
g.set_infoset(g.root.children[2].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[1].children[0].infoset)

# Player1 nodes after two safe pulls exist for branches 2..5.
g.set_infoset(g.root.children[3].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[2].children[0].children[0].infoset)

# Player2 nodes after three safe pulls exist for branches 3..5.
g.set_infoset(g.root.children[4].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)

# Player1 nodes after four safe pulls exist for branches 4..5.
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].children[0].infoset)

# Player2 node after five safe pulls exists only in branch 5, so no grouping needed.

# Save the EFG
g.to_efg("revolver_6chambers.efg")