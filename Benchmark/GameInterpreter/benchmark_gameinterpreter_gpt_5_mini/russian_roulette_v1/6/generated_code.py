import pygambit as gbt

# Create the game with two players
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian Roulette")

# Reasoning summary (also repeated in inline comments below):
# - Chance at root chooses which chamber (1..6) is loaded. That chamber is fixed but unobserved.
# - Players alternate turns. On each turn a player chooses Quit or Pull.
# - Action ordering chosen as ["Quit", "Pull"] so that:
#     * children[0] = Quit (terminal),
#     * children[1] = Pull (may be terminal if that chamber is loaded, otherwise continues).
# - We explicitly expand the tree without loops. Payoffs listed as [Player 1, Player 2].
#     * If a player quits -> quitter 0, other 1.
#     * If a player pulls and the chamber is loaded -> shooter -1, other 1.
# - We group all decision nodes that correspond to the same player's turn (same turn number)
#   into the same information set so they are indistinguishable to that player.
# - All chance probabilities are 1/6 using gbt.Rational.

# 1) Chance: choose bullet position 1..6
g.append_move(g.root, g.players.chance, ["Chamber 1", "Chamber 2", "Chamber 3", "Chamber 4", "Chamber 5", "Chamber 6"])
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                                     gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# ------------------------------------------------------------------
# Turn 1 (Player 1) at each chance branch: append ["Quit","Pull"]
# g.root.children[i] corresponds to bullet in Chamber (i+1)
g.append_move(g.root.children[0], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[2], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5], "Player 1", ["Quit", "Pull"])

# Set outcomes for Quit on Player 1's first turn (quitter gets 0, other gets 1)
g.set_outcome(g.root.children[0].children[0], g.add_outcome([0, 1], label="P1 quits t1 (ch1)"))
g.set_outcome(g.root.children[1].children[0], g.add_outcome([0, 1], label="P1 quits t1 (ch2)"))
g.set_outcome(g.root.children[2].children[0], g.add_outcome([0, 1], label="P1 quits t1 (ch3)"))
g.set_outcome(g.root.children[3].children[0], g.add_outcome([0, 1], label="P1 quits t1 (ch4)"))
g.set_outcome(g.root.children[4].children[0], g.add_outcome([0, 1], label="P1 quits t1 (ch5)"))
g.set_outcome(g.root.children[5].children[0], g.add_outcome([0, 1], label="P1 quits t1 (ch6)"))

# If Player 1 pulls on turn 1:
# - For Chamber 1 (index 0) the shot fires immediately and P1 dies.
g.set_outcome(g.root.children[0].children[1], g.add_outcome([-1, 1], label="P1 shot (ch1)"))

# - For Chambers 2..6 the Pull survives and we must append Player 2's first turn at those continuation nodes:
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[2].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1], "Player 2", ["Quit", "Pull"])

# Set outcomes for Player 2 quitting on their first turn (quitter gets 0, other gets 1)
g.set_outcome(g.root.children[1].children[1].children[0], g.add_outcome([1, 0], label="P2 quits t1 (ch2)"))
g.set_outcome(g.root.children[2].children[1].children[0], g.add_outcome([1, 0], label="P2 quits t1 (ch3)"))
g.set_outcome(g.root.children[3].children[1].children[0], g.add_outcome([1, 0], label="P2 quits t1 (ch4)"))
g.set_outcome(g.root.children[4].children[1].children[0], g.add_outcome([1, 0], label="P2 quits t1 (ch5)"))
g.set_outcome(g.root.children[5].children[1].children[0], g.add_outcome([1, 0], label="P2 quits t1 (ch6)"))

# If Player 2 pulls on their first turn:
# - For Chamber 2 (index 1) the shot fires immediately and P2 dies.
g.set_outcome(g.root.children[1].children[1].children[1], g.add_outcome([1, -1], label="P2 shot (ch2)"))

# - For Chambers 3..6 the Pull survives and we append Player 1's second turn
g.append_move(g.root.children[2].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1], "Player 1", ["Quit", "Pull"])

# Set outcomes for Player 1 quitting on their second turn (quitter gets 0, other gets 1)
g.set_outcome(g.root.children[2].children[1].children[1].children[0], g.add_outcome([0, 1], label="P1 quits t2 (ch3)"))
g.set_outcome(g.root.children[3].children[1].children[1].children[0], g.add_outcome([0, 1], label="P1 quits t2 (ch4)"))
g.set_outcome(g.root.children[4].children[1].children[1].children[0], g.add_outcome([0, 1], label="P1 quits t2 (ch5)"))
g.set_outcome(g.root.children[5].children[1].children[1].children[0], g.add_outcome([0, 1], label="P1 quits t2 (ch6)"))

# If Player 1 pulls on their second turn:
# - For Chamber 3 (index 2) the shot fires immediately and P1 dies.
g.set_outcome(g.root.children[2].children[1].children[1].children[1], g.add_outcome([-1, 1], label="P1 shot (ch3)"))

# - For Chambers 4..6 the Pull survives and we append Player 2's second turn
g.append_move(g.root.children[3].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# Set outcomes for Player 2 quitting on their second turn
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[0], g.add_outcome([1, 0], label="P2 quits t2 (ch4)"))
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[0], g.add_outcome([1, 0], label="P2 quits t2 (ch5)"))
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[0], g.add_outcome([1, 0], label="P2 quits t2 (ch6)"))

# If Player 2 pulls on their second turn:
# - For Chamber 4 (index 3) the shot fires immediately and P2 dies.
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[1], g.add_outcome([1, -1], label="P2 shot (ch4)"))

# - For Chambers 5..6 the Pull survives and we append Player 1's third turn
g.append_move(g.root.children[4].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])

# Set outcomes for Player 1 quitting on their third turn
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[0], g.add_outcome([0, 1], label="P1 quits t3 (ch5)"))
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[0], g.add_outcome([0, 1], label="P1 quits t3 (ch6)"))

# If Player 1 pulls on their third turn:
# - For Chamber 5 (index 4) the shot fires immediately and P1 dies.
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[1], g.add_outcome([-1, 1], label="P1 shot (ch5)"))

# - For Chamber 6 (index 5) the Pull survives to Player 2's third turn (which is the 6th pull)
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# Set outcome for Player 2 quitting on their third turn (this is before the final pull on ch6)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[0], g.add_outcome([1, 0], label="P2 quits t3 (ch6)"))

# If Player 2 pulls on their third turn:
# - For Chamber 6 (index 5) the shot fires and P2 dies.
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[1], g.add_outcome([1, -1], label="P2 shot (ch6)"))

# ------------------------------------------------------------------
# Set information sets so that nodes corresponding to the same player's turn
# are indistinguishable (they share the same infoset).
# All set_infoset calls are done after append_move for the involved nodes.

# Player 1, Turn 1: all g.root.children[0..5] are in the same infoset
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Player 2, Turn 1: all continuation nodes after P1's first Pull (exist for chambers 2..6)
g.set_infoset(g.root.children[2].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[3].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1], g.root.children[1].children[1].infoset)

# Player 1, Turn 2: continuation nodes after P2's first Pull (exist for chambers 3..6)
g.set_infoset(g.root.children[3].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1], g.root.children[2].children[1].children[1].infoset)

# Player 2, Turn 2: continuation nodes after P1's second Pull (exist for chambers 4..6)
g.set_infoset(g.root.children[4].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)

# Player 1, Turn 3: continuation nodes after P2's second Pull (exist for chambers 5..6)
g.set_infoset(g.root.children[5].children[1].children[1].children[1].children[1], g.root.children[4].children[1].children[1].children[1].children[1].infoset)

# Note: Player 2's third turn (chamber 6 final pull) is a single node (no grouping needed).

# Save the EFG
g.to_efg("six_chamber_russian_roulette.efg")