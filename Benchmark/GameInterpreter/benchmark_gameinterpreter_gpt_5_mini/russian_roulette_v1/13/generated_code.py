import pygambit as gbt

# Construct a 2-player extensive-form game: alternating turns with a six-chamber revolver.
# Reasoning (summarized in comments inline):
# - Chance at the root selects which chamber (1..6) holds the single bullet, each with probability 1/6.
# - The chamber index determines on which pull (turn) the pulling player will be killed.
# - Players alternate: P1 (turn 1), P2 (turn 2), P1 (turn 3), P2 (turn 4), P1 (turn 5), P2 (turn 6).
# - At each decision a player chooses between "Quit" (guaranteed survival: quitter gets 0, other gets 1)
#   or "Pull" (if this pull corresponds to the loaded chamber the pulling player dies and gets -1,
#   the other gets 1; otherwise play continues to the opponent).
# - We explicitly construct the tree for each possible bullet position (6 branches). No loops are used.

g = gbt.Game.new_tree(players=["P1", "P2"],
                      title="Alternating six-chamber Russian roulette")

# Chance: which chamber (1..6) is loaded.
g.append_move(g.root, g.players.chance,
              ["Chamber 1", "Chamber 2", "Chamber 3", "Chamber 4", "Chamber 5", "Chamber 6"])
g.set_chance_probs(g.root.infoset,
                   [gbt.Rational(1, 6),
                    gbt.Rational(1, 6),
                    gbt.Rational(1, 6),
                    gbt.Rational(1, 6),
                    gbt.Rational(1, 6),
                    gbt.Rational(1, 6)])

# Create a few reusable outcomes:
p1_quits = g.add_outcome([0, 1], label="P1 quits (0,1)")
p2_quits = g.add_outcome([1, 0], label="P2 quits (1,0)")
p1_dies = g.add_outcome([-1, 1], label="P1 dies (-1,1)")
p2_dies = g.add_outcome([1, -1], label="P2 dies (1,-1)")

# --- BRANCH for bullet in Chamber 1 (index 0) ---
# Turn1 (P1) exists: append move
g.append_move(g.root.children[0], "P1", ["Quit", "Pull"])
# If P1 quits on turn1 -> terminal (P1 gets 0, P2 gets 1)
g.set_outcome(g.root.children[0].children[0], p1_quits)
# If P1 pulls on turn1 and bullet is chamber 1 -> P1 dies immediately
# So Pull child is terminal with death outcome for P1.
g.set_outcome(g.root.children[0].children[1], p1_dies)

# --- BRANCH for bullet in Chamber 2 (index 1) ---
# Turn1 (P1)
g.append_move(g.root.children[1], "P1", ["Quit", "Pull"])
g.set_outcome(g.root.children[1].children[0], p1_quits)
# P1 pulls on turn1 (survives because bullet is chamber 2): now P2 has a decision on turn2
g.append_move(g.root.children[1].children[1], "P2", ["Quit", "Pull"])
# If P2 quits on turn2 -> terminal (P2 gets 0, P1 gets 1)
g.set_outcome(g.root.children[1].children[1].children[0], p2_quits)
# If P2 pulls on turn2 and bullet is chamber 2 -> P2 dies
g.set_outcome(g.root.children[1].children[1].children[1], p2_dies)

# --- BRANCH for bullet in Chamber 3 (index 2) ---
# Turn1 (P1)
g.append_move(g.root.children[2], "P1", ["Quit", "Pull"])
g.set_outcome(g.root.children[2].children[0], p1_quits)
# P1 pulls on turn1 -> survive (bullet is chamber 3) -> P2 turn2
g.append_move(g.root.children[2].children[1], "P2", ["Quit", "Pull"])
g.set_outcome(g.root.children[2].children[1].children[0], p2_quits)
# P2 pulls on turn2 -> survive (bullet is chamber 3) -> P1 turn3
g.append_move(g.root.children[2].children[1].children[1], "P1", ["Quit", "Pull"])
# If P1 quits on turn3 -> terminal (P1 gets 0, P2 gets 1)
g.set_outcome(g.root.children[2].children[1].children[1].children[0], p1_quits)
# If P1 pulls on turn3 and bullet is chamber 3 -> P1 dies
g.set_outcome(g.root.children[2].children[1].children[1].children[1], p1_dies)

# --- BRANCH for bullet in Chamber 4 (index 3) ---
# Turn1 (P1)
g.append_move(g.root.children[3], "P1", ["Quit", "Pull"])
g.set_outcome(g.root.children[3].children[0], p1_quits)
# P1 pulls -> survive (bullet is 4) -> P2 turn2
g.append_move(g.root.children[3].children[1], "P2", ["Quit", "Pull"])
g.set_outcome(g.root.children[3].children[1].children[0], p2_quits)
# P2 pulls -> survive (bullet is 4) -> P1 turn3
g.append_move(g.root.children[3].children[1].children[1], "P1", ["Quit", "Pull"])
g.set_outcome(g.root.children[3].children[1].children[1].children[0], p1_quits)
# P1 pulls -> survive (bullet is 4) -> P2 turn4
g.append_move(g.root.children[3].children[1].children[1].children[1], "P2", ["Quit", "Pull"])
# If P2 quits on turn4 -> terminal (P2 gets 0, P1 gets 1)
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[0], p2_quits)
# If P2 pulls on turn4 and bullet is chamber 4 -> P2 dies
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[1], p2_dies)

# --- BRANCH for bullet in Chamber 5 (index 4) ---
# Turn1 (P1)
g.append_move(g.root.children[4], "P1", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[0], p1_quits)
# P1 pulls -> survive -> P2 turn2
g.append_move(g.root.children[4].children[1], "P2", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[0], p2_quits)
# P2 pulls -> survive -> P1 turn3
g.append_move(g.root.children[4].children[1].children[1], "P1", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[1].children[0], p1_quits)
# P1 pulls -> survive -> P2 turn4
g.append_move(g.root.children[4].children[1].children[1].children[1], "P2", ["Quit", "Pull"])
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[0], p2_quits)
# P2 pulls -> survive -> P1 turn5
g.append_move(g.root.children[4].children[1].children[1].children[1].children[1], "P1", ["Quit", "Pull"])
# If P1 quits on turn5 -> terminal (P1 gets 0, P2 gets 1)
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[0], p1_quits)
# If P1 pulls on turn5 and bullet is chamber 5 -> P1 dies
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[1], p1_dies)

# --- BRANCH for bullet in Chamber 6 (index 5) ---
# Turn1 (P1)
g.append_move(g.root.children[5], "P1", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[0], p1_quits)
# P1 pulls -> survive -> P2 turn2
g.append_move(g.root.children[5].children[1], "P2", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[0], p2_quits)
# P2 pulls -> survive -> P1 turn3
g.append_move(g.root.children[5].children[1].children[1], "P1", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[0], p1_quits)
# P1 pulls -> survive -> P2 turn4
g.append_move(g.root.children[5].children[1].children[1].children[1], "P2", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[0], p2_quits)
# P2 pulls -> survive -> P1 turn5
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1], "P1", ["Quit", "Pull"])
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[0], p1_quits)
# P1 pulls -> survive -> P2 turn6
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1].children[1], "P2", ["Quit", "Pull"])
# If P2 quits on turn6 -> terminal (P2 gets 0, P1 gets 1)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[0], p2_quits)
# If P2 pulls on turn6 and bullet is chamber 6 -> P2 dies
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[1], p2_dies)

# --- Set information sets to reflect that players do not observe which chamber was chosen ---
# Players only know the number of pulls (i.e., which turn it is) and who is to move,
# not which chamber is loaded. Thus nodes on the same player's turn number (across different
# chance branches) are in the same infoset.

# Player 1, turn 1: group g.root.children[0..5]
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Player 2, turn 2: group nodes where they exist (branches with bullet != 1): g.root.children[1..5].children[1]
g.set_infoset(g.root.children[2].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[3].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1], g.root.children[1].children[1].infoset)

# Player 1, turn 3: group nodes where they exist (branches with bullet >= 3): g.root.children[2..5].children[1].children[1]
g.set_infoset(g.root.children[3].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1], g.root.children[2].children[1].children[1].infoset)

# Player 2, turn 4: group nodes where they exist (branches with bullet >= 4): g.root.children[3..5].children[1].children[1].children[1]
g.set_infoset(g.root.children[4].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)

# Player 1, turn 5: group nodes where they exist (branches with bullet >= 5): g.root.children[4..5].children[1].children[1].children[1].children[1]
g.set_infoset(g.root.children[5].children[1].children[1].children[1].children[1], g.root.children[4].children[1].children[1].children[1].children[1].infoset)

# Player 2, turn 6: only branch with bullet == 6 has this node (no grouping necessary)

# Save the EFG to a file.
g.to_efg("six_chamber_russian_roulette.efg")