import pygambit as gbt

# Reasoning (in comments):
# - There are two players: "Player 1" and "Player 2".
# - Chance at the root selects which of the 6 chambers (indices 0..5) contains the bullet,
#   each with probability 1/6. This selection is fixed for the playthrough but unknown to players.
# - Players alternate pulling the trigger or quitting. Pull = risk (may die if current chamber
#   is the loaded one), Quit = get 0 while the other player gets 1.
# - If a pull occurs when the current chamber is the loaded one, the shooter gets -1 and the
#   opponent gets +1. Otherwise play continues to the other player's decision.
# - We model the six possible initial chamber choices as the six branches of a chance node.
# - At each decision node the action ordering is ["Pull", "Quit"] so that the Pull branch is
#   at child index 0 and the Quit branch is at child index 1 across the tree.
# - For imperfect information: at a given turn number, the player does not know which chamber
#   was chosen by chance. Thus all nodes corresponding to the same player's decision on the
#   same turn (across the 6 chance branches) are placed in the same information set.
# - Below we explicitly build the tree without loops or recursion (unrolled for 6 branches
#   and up to 6 turns), set the chance probabilities using gbt.Rational, set the information
#   sets as described, and then add outcomes for quitting and for being shot.
# NOTE: This unrolled explicit construction avoids loops and recursion as requested.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# 1) Chance at root: 6 equally likely chambers
g.append_move(g.root, g.players.chance,
              ["Chamber 0", "Chamber 1", "Chamber 2", "Chamber 3", "Chamber 4", "Chamber 5"])
g.set_chance_probs(g.root.infoset,
                   [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                    gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# 2) For each chance branch, append the alternating moves up to 6 turns.
# Turn ordering: Turn 1 = Player 1, Turn 2 = Player 2, Turn 3 = Player 1, ...
# We use action order ["Pull", "Quit"] so Pull is child[0], Quit is child[1].

# Branch 0
g.append_move(g.root.children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[0].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[0].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Branch 1
g.append_move(g.root.children[1], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[1].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[1].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[1].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[1].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[1].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Branch 2
g.append_move(g.root.children[2], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Branch 3
g.append_move(g.root.children[3], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Branch 4
g.append_move(g.root.children[4], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Branch 5
g.append_move(g.root.children[5], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# 3) Set information sets for decisions that correspond to the same turn across chance branches.
# Group Player 1's first-turn decision nodes (turn 1)
g.set_infoset(g.root.children[1], g.root.children[0].infoset)
g.set_infoset(g.root.children[2], g.root.children[0].infoset)
g.set_infoset(g.root.children[3], g.root.children[0].infoset)
g.set_infoset(g.root.children[4], g.root.children[0].infoset)
g.set_infoset(g.root.children[5], g.root.children[0].infoset)

# Group Player 2's first-turn decision nodes (turn 2)
g.set_infoset(g.root.children[1].children[0], g.root.children[0].children[0].infoset)
g.set_infoset(g.root.children[2].children[0], g.root.children[0].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[0].children[0].infoset)

# Group Player 1's second-turn decision nodes (turn 3)
g.set_infoset(g.root.children[1].children[0].children[0], g.root.children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[2].children[0].children[0], g.root.children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[3].children[0].children[0], g.root.children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[0].children[0].children[0].infoset)

# Group Player 2's second-turn decision nodes (turn 4)
g.set_infoset(g.root.children[1].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[2].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[3].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].infoset)

# Group Player 1's third-turn decision nodes (turn 5)
g.set_infoset(g.root.children[1].children[0].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[2].children[0].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[3].children[0].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].children[0].infoset)

# Group Player 2's third-turn decision nodes (turn 6)
g.set_infoset(g.root.children[1].children[0].children[0].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[2].children[0].children[0].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[3].children[0].children[0].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0].children[0], g.root.children[0].children[0].children[0].children[0].children[0].children[0].infoset)

# 4) Outcomes:
# Define outcomes for quitting and for being shot. Outcome vectors are [Player1 payoff, Player2 payoff].
p1_quits = g.add_outcome([0, 1], label="P1 quits, P2 wins")
p2_quits = g.add_outcome([1, 0], label="P2 quits, P1 wins")
p1_shot = g.add_outcome([-1, 1], label="P1 shot, P2 wins")
p2_shot = g.add_outcome([1, -1], label="P2 shot, P1 wins")

# For each branch and each turn, set outcomes for the Quit action nodes (child index 1).
# Branch 0 quitting nodes
g.set_outcome(g.root.children[0].children[1], p1_quits)  # P1 quits on turn1 (branch 0)
g.set_outcome(g.root.children[0].children[0].children[1], p2_quits)  # P2 quits on turn2
g.set_outcome(g.root.children[0].children[0].children[0].children[1], p1_quits)  # P1 quits on turn3
g.set_outcome(g.root.children[0].children[0].children[0].children[0].children[1], p2_quits)  # P2 quits on turn4
g.set_outcome(g.root.children[0].children[0].children[0].children[0].children[0].children[1], p1_quits)  # P1 quits on turn5
g.set_outcome(g.root.children[0].children[0].children[0].children[0].children[0].children[0].children[1], p2_quits)  # P2 quits on turn6

# Branch 1 quitting nodes
g.set_outcome(g.root.children[1].children[1], p1_quits)
g.set_outcome(g.root.children[1].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[1].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[1].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[1].children[0].children[0].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[1].children[0].children[0].children[0].children[0].children[0].children[1], p2_quits)

# Branch 2 quitting nodes
g.set_outcome(g.root.children[2].children[1], p1_quits)
g.set_outcome(g.root.children[2].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[2].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[2].children[0].children[0].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[2].children[0].children[0].children[0].children[0].children[0].children[1], p2_quits)

# Branch 3 quitting nodes
g.set_outcome(g.root.children[3].children[1], p1_quits)
g.set_outcome(g.root.children[3].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0].children[0].children[1], p2_quits)

# Branch 4 quitting nodes
g.set_outcome(g.root.children[4].children[1], p1_quits)
g.set_outcome(g.root.children[4].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0].children[1], p2_quits)

# Branch 5 quitting nodes
g.set_outcome(g.root.children[5].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quits)

# 5) Shot outcomes:
# When the player pulls on turn t and the chosen chamber equals (t-1), the pulling action causes the shooter to be shot.
# The pull action child node is at the position that the next player would otherwise occupy. We set that node's outcome
# to the corresponding "shot" outcome for the branch where the bullet index equals (turn-1).
# For branch c, death occurs on pull at turn t = c + 1, so set outcome at the pull-child node reached after that pull.

# Branch 0: bullet in chamber 0 -> death on turn1 (P1 pulls)
g.set_outcome(g.root.children[0].children[0], p1_shot)  # After P1 pulls on turn1 (branch 0), P1 is shot

# Branch 1: bullet in chamber 1 -> death on turn2 (P2 pulls)
g.set_outcome(g.root.children[1].children[0].children[0], p2_shot)  # After P2 pulls on turn2 (branch 1), P2 is shot

# Branch 2: bullet in chamber 2 -> death on turn3 (P1 pulls)
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_shot)  # After P1 pulls on turn3 (branch 2), P1 is shot

# Branch 3: bullet in chamber 3 -> death on turn4 (P2 pulls)
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_shot)  # After P2 pulls on turn4 (branch 3), P2 is shot

# Branch 4: bullet in chamber 4 -> death on turn5 (P1 pulls)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_shot)  # After P1 pulls on turn5 (branch 4), P1 is shot

# Branch 5: bullet in chamber 5 -> death on turn6 (P2 pulls)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_shot)  # After P2 pulls on turn6 (branch 5), P2 is shot

# Save the EFG to file
g.to_efg("six_chamber_russian_roulette.efg")