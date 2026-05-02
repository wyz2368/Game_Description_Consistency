import pygambit as gbt

# Construct a 2-player extensive-form game for the 6-chamber alternating Russian
# roulette described. Players are "Player 1" and "Player 2". The chance move at
# the root selects which chamber (1..6) is loaded. Player 1 moves first.
#
# Reasoning in comments:
# - The chance node at the root has six equally likely outcomes: Chamber 1..6.
# - For each possible initially loaded chamber k, the play unfolds along a
#   deterministic sequence of pull or quit decisions until someone quits or the
#   pull that corresponds to chamber k is taken and that player dies.
# - We explicitly build each branch for loaded chamber k in full, without using
#   loops or recursion. After appending all moves we set the information sets to
#   reflect that players do not observe which chamber was initially loaded.
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# Chance at root chooses which chamber is loaded (1..6).
g.append_move(g.root, g.players.chance,
              ["Chamber 1", "Chamber 2", "Chamber 3", "Chamber 4", "Chamber 5", "Chamber 6"])
# Set equal probabilities 1/6 for each chamber using gbt.Rational
g.set_chance_probs(g.root.infoset,
                   [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                    gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# For each initial loaded chamber node, Player 1 acts first and chooses Pull or Quit.
g.append_move(g.root.children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[1], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[2], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5], "Player 1", ["Pull", "Quit"])

# If Player 1 pulls and survives on chambers 1..5, play passes to Player 2 at the next chamber.
# Append Player 2 moves on the Pull child of root.children[1] .. root.children[5].
g.append_move(g.root.children[1].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "Player 2", ["Pull", "Quit"])

# If Player 2 pulls and survives on chambers 2..5, play returns to Player 1 at the subsequent chamber.
# Append Player 1 moves at those nodes.
g.append_move(g.root.children[2].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "Player 1", ["Pull", "Quit"])

# If Player 1 pulls and survives again (third pull for Player 1), Player 2 faces a second decision
# on the next chamber for initial loaded chambers 4..6. Append those Player 2 moves.
g.append_move(g.root.children[3].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# If Player 2 survives that second decision, Player 1 faces his third decision for initial chambers 5..6.
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])

# Finally, in the LC=6 branch if Player 1 pulls at chamber 5 and survives, Player 2 faces the final
# (sixth) chamber decision. Append that last Player 2 move for LC=6.
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Now set information sets to encode the players not observing which chamber was initially loaded.
# Group the six initial Player 1 nodes into one information set.
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Player 2's first decision after one survived pull occurs for initial loaded chambers 2..6.
g.set_infoset(g.root.children[2].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[1].children[0].infoset)

# Player 1's second decision (after two survived pulls) occurs for initial chambers 3..6.
g.set_infoset(g.root.children[3].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[2].children[0].children[0].infoset)

# Player 2's second decision (after two survived pulls) occurs for initial chambers 4..6.
g.set_infoset(g.root.children[4].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)

# Player 1's third decision (after three survived pulls) occurs for initial chambers 5..6.
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0],
              g.root.children[4].children[0].children[0].children[0].children[0].infoset)

# Define outcomes to reuse
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_dies = g.add_outcome([1, -1], label="P2 dies")
p1_quit = g.add_outcome([0, 1], label="P1 quits")
p2_quit = g.add_outcome([1, 0], label="P2 quits")

# Set outcomes for all terminal nodes branch by branch.

# LC = 1 (root.children[0])
# Player 1 Pull => dies
g.set_outcome(g.root.children[0].children[0], p1_dies)
# Player 1 Quit => withdraws
g.set_outcome(g.root.children[0].children[1], p1_quit)

# LC = 2 (root.children[1])
# Player 1 Quit at chamber 1
g.set_outcome(g.root.children[1].children[1], p1_quit)
# If Player 1 Pulls and then Player 2 acts:
# Player 2 Pull => dies
g.set_outcome(g.root.children[1].children[0].children[0], p2_dies)
# Player 2 Quit => withdraws
g.set_outcome(g.root.children[1].children[0].children[1], p2_quit)

# LC = 3 (root.children[2])
# Player 1 Quit at chamber 1
g.set_outcome(g.root.children[2].children[1], p1_quit)
# Player 1 Pull leads to Player 2 decision:
# Player 2 Quit at chamber 2
g.set_outcome(g.root.children[2].children[0].children[1], p2_quit)
# Player 2 Pull leads to Player 1 decision at chamber 3:
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_dies)  # P1 pulls and dies
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quit)  # P1 quits

# LC = 4 (root.children[3])
# Player 1 Quit at chamber 1
g.set_outcome(g.root.children[3].children[1], p1_quit)
# Player 1 Pull -> Player 2 at chamber 2
# Player 2 Quit at chamber 2
g.set_outcome(g.root.children[3].children[0].children[1], p2_quit)
# Player 2 Pull -> Player 1 at chamber 3
# Player 1 Quit at chamber 3
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quit)
# Player 1 Pull -> Player 2 at chamber 4
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_dies)
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quit)

# LC = 5 (root.children[4])
# Player 1 Quit at chamber 1
g.set_outcome(g.root.children[4].children[1], p1_quit)
# P1 Pull -> P2 at chamber 2
# P2 Quit
g.set_outcome(g.root.children[4].children[0].children[1], p2_quit)
# P2 Pull -> P1 at chamber 3
# P1 Quit
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quit)
# P1 Pull -> P2 at chamber 4
# P2 Quit
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quit)
# P2 Pull -> P1 at chamber 5
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_dies)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quit)

# LC = 6 (root.children[5])
# Player 1 Quit at chamber 1
g.set_outcome(g.root.children[5].children[1], p1_quit)
# P1 Pull -> P2 at chamber 2
# P2 Quit
g.set_outcome(g.root.children[5].children[0].children[1], p2_quit)
# P2 Pull -> P1 at chamber 3
# P1 Quit
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quit)
# P1 Pull -> P2 at chamber 4
# P2 Quit
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quit)
# P2 Pull -> P1 at chamber 5
# P1 Quit
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quit)
# P1 Pull -> P2 at chamber 6
# P2 Pull => dies at chamber 6
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_dies)
# P2 Quit at that final node
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quit)

# Save the constructed game to an EFG file.
g.to_efg("six_chamber_russian_roulette.efg")