import pygambit as gbt

# Create the game with two players
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating Russian Roulette (6-chamber)")

# Reasoning:
# 1) Chance chooses which of the six chambers is loaded. Each chamber has equal probability 1/6.
# 2) Players alternate: Player 1 acts before pulls 1,3,5. Player 2 acts before pulls 2,4,6.
# 3) At each decision a player can "Pull" or "Quit". We put "Pull" as the first action so that
#    child index 0 of a decision node corresponds to the Pull branch and child index 1 to Quit.
# 4) If a player quits, that player gets 0 and the other gets 1.
# 5) If a player pulls and the current chamber is loaded, that player dies and gets -1 while the other gets 1.
# 6) If a player pulls and the chamber is empty, play passes to the other player's decision node.

# 1) Add the initial chance move selecting the loaded chamber among six equally likely chambers.
g.append_move(g.root, g.players.chance,
              ["Chamber 1", "Chamber 2", "Chamber 3", "Chamber 4", "Chamber 5", "Chamber 6"])
# Set equal probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset,
                   [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                    gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Prepare common outcome objects to reuse
p1_dies = g.add_outcome([-1, 1], label="P1 dies")
p2_dies = g.add_outcome([1, -1], label="P2 dies")
p1_wins = g.add_outcome([1, 0], label="P1 wins")
p2_wins = g.add_outcome([0, 1], label="P2 wins")

# Now build the decision tree explicitly for each chance branch (no loops, unrolled).

# CHAMBER 1 branch (index 0): bullet is at pull 1
# Player 1 initial decision node on this branch
g.append_move(g.root.children[0], "Player 1", ["Pull", "Quit"])
# If Player 1 quits immediately, outcome is [0,1]
g.set_outcome(g.root.children[0].children[1], p2_wins)
# If Player 1 pulls on pull 1, since chamber 1 is loaded, Player 1 dies
g.set_outcome(g.root.children[0].children[0], p1_dies)

# CHAMBER 2 branch (index 1): bullet at pull 2
g.append_move(g.root.children[1], "Player 1", ["Pull", "Quit"])
g.set_outcome(g.root.children[1].children[1], p2_wins)
# If P1 pulls at pull 1, it's safe, so append Player 2 first-turn node
g.append_move(g.root.children[1].children[0], "Player 2", ["Pull", "Quit"])
# If Player 2 quits at this node, outcome [1,0]
g.set_outcome(g.root.children[1].children[0].children[1], p1_wins)
# If Player 2 pulls at pull 2, chamber 2 is loaded => Player 2 dies
g.set_outcome(g.root.children[1].children[0].children[0], p2_dies)

# CHAMBER 3 branch (index 2): bullet at pull 3
g.append_move(g.root.children[2], "Player 1", ["Pull", "Quit"])
g.set_outcome(g.root.children[2].children[1], p2_wins)
# P1 pulls at pull1 -> safe, go to P2 first-turn
g.append_move(g.root.children[2].children[0], "Player 2", ["Pull", "Quit"])
g.set_outcome(g.root.children[2].children[0].children[1], p1_wins)
# P2 pulls at pull2 -> safe (since bullet is at pull3), go to P1 second-turn
g.append_move(g.root.children[2].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p2_wins)
# P1 pulls at pull3 -> bullet, P1 dies
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_dies)

# CHAMBER 4 branch (index 3): bullet at pull 4
g.append_move(g.root.children[3], "Player 1", ["Pull", "Quit"])
g.set_outcome(g.root.children[3].children[1], p2_wins)
g.append_move(g.root.children[3].children[0], "Player 2", ["Pull", "Quit"])
g.set_outcome(g.root.children[3].children[0].children[1], p1_wins)
g.append_move(g.root.children[3].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p2_wins)
# P1 pulls at pull3 -> safe, go to P2 second-turn before pull4
g.append_move(g.root.children[3].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p1_wins)
# P2 pulls at pull4 -> bullet, P2 dies
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_dies)

# CHAMBER 5 branch (index 4): bullet at pull 5
g.append_move(g.root.children[4], "Player 1", ["Pull", "Quit"])
g.set_outcome(g.root.children[4].children[1], p2_wins)
g.append_move(g.root.children[4].children[0], "Player 2", ["Pull", "Quit"])
g.set_outcome(g.root.children[4].children[0].children[1], p1_wins)
g.append_move(g.root.children[4].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p2_wins)
g.append_move(g.root.children[4].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p1_wins)
# P2 pulls at pull4 -> safe, go to P1 third-turn before pull5
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p2_wins)
# P1 pulls at pull5 -> bullet, P1 dies
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_dies)

# CHAMBER 6 branch (index 5): bullet at pull 6
g.append_move(g.root.children[5], "Player 1", ["Pull", "Quit"])
g.set_outcome(g.root.children[5].children[1], p2_wins)
g.append_move(g.root.children[5].children[0], "Player 2", ["Pull", "Quit"])
g.set_outcome(g.root.children[5].children[0].children[1], p1_wins)
g.append_move(g.root.children[5].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p2_wins)
g.append_move(g.root.children[5].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p1_wins)
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p2_wins)
# After P1 pulls at pull5 and survives (since bullet at pull6), we reach P2 before pull6.
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
# If P2 quits before the 6th pull, P1 wins
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p1_wins)
# If P2 pulls at pull6, the bullet is in chamber 6 and P2 dies
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_dies)

# Now set the information sets to reflect players' imperfect information:
# Players cannot observe which chamber was chosen; they only observe the number of safe clicks so far.
# Therefore decision nodes that occur after the same number of prior safe pulls are in the same infoset.

# Group all Player 1 initial decision nodes (before the 1st pull): all chance branches 0..5
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Group all Player 2 first-turn nodes (before the 2nd pull): occur on branches where bullet != chamber 1 (chance children 1..5)
g.set_infoset(g.root.children[2].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[1].children[0].infoset)

# Group all Player 1 second-turn nodes (before the 3rd pull): branches where bullet not in {1,2} => chance children 2..5
g.set_infoset(g.root.children[3].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[2].children[0].children[0].infoset)

# Group all Player 2 second-turn nodes (before the 4th pull): branches where bullet not in {1,2,3} => chance children 3..5
g.set_infoset(g.root.children[4].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)

# Group all Player 1 third-turn nodes (before the 5th pull): branches where bullet not in {1,2,3,4} => chance children 4..5
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0],
              g.root.children[4].children[0].children[0].children[0].children[0].infoset)

# Save the EFG to a file
g.to_efg("alternating_russian_roulette.efg")