import pygambit as gbt

# Build an extensive-form game for alternating six-chamber Russian roulette.
# Players are "Player 1" (starts) and "Player 2".
# Chance initially selects which chamber (0..5) is loaded; players do NOT observe it.
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating six-chamber Russian roulette")

# 1) Chance selects the loaded chamber (0..5) at the root.
g.append_move(g.root, g.players.chance,
              ["Loaded 0", "Loaded 1", "Loaded 2", "Loaded 3", "Loaded 4", "Loaded 5"])
# Set equal probabilities 1/6 for each chamber.
g.set_chance_probs(g.root.infoset,
                   [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                    gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Reasoning:
# - At each chance branch g.root.children[b], Player 1 moves first. He cannot distinguish which
#   branch occurred, so these six nodes form one information set for Player 1.
# Action ordering: ["Quit", "Pull"] so that .children[0] = Quit (terminal), .children[1] = Pull (may continue).
g.append_move(g.root.children[0], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[2], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5], "Player 1", ["Quit", "Pull"])

# Group Player 1's initial decision nodes into one infoset (they were appended above).
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Payoffs conventions:
# - If a player quits: quitter gets 0, other gets 1.
# - If a player pulls and hits the loaded chamber: shooter gets -1, other gets 1.
# - If a player pulls and survives: play continues.

# Outcomes for Player 1 quitting at the very first decision:
out_quit_p1 = g.add_outcome([0, 1], label="P1 quits initially")
g.set_outcome(g.root.children[0].children[0], out_quit_p1)
g.set_outcome(g.root.children[1].children[0], out_quit_p1)
g.set_outcome(g.root.children[2].children[0], out_quit_p1)
g.set_outcome(g.root.children[3].children[0], out_quit_p1)
g.set_outcome(g.root.children[4].children[0], out_quit_p1)
g.set_outcome(g.root.children[5].children[0], out_quit_p1)

# If Player 1 pulls at the initial move:
# - For b = 0 (loaded chamber 0) he dies immediately.
out_p1_shot = g.add_outcome([-1, 1], label="P1 shot on first pull")
g.set_outcome(g.root.children[0].children[1], out_p1_shot)

# - For b = 1..5, P1 pulls and survives (since chamber 0 was fired); play passes to Player 2
#   at nodes g.root.children[b].children[1]. Append Player 2 moves at those nodes.
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[2].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1], "Player 2", ["Quit", "Pull"])

# These P2 nodes after one safe pull are indistinguishable to Player 2, so group them.
g.set_infoset(g.root.children[2].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[3].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1], g.root.children[1].children[1].infoset)

# Outcomes for Player 2 quitting at this stage: P2 gets 0, P1 gets 1
out_quit_p2 = g.add_outcome([1, 0], label="P2 quits after one safe pull")
g.set_outcome(g.root.children[1].children[1].children[0], out_quit_p2)
g.set_outcome(g.root.children[2].children[1].children[0], out_quit_p2)
g.set_outcome(g.root.children[3].children[1].children[0], out_quit_p2)
g.set_outcome(g.root.children[4].children[1].children[0], out_quit_p2)
g.set_outcome(g.root.children[5].children[1].children[0], out_quit_p2)

# If Player 2 pulls now:
# - For b = 1 (loaded chamber 1) P2 dies immediately.
out_p2_shot = g.add_outcome([1, -1], label="P2 shot on second pull")
g.set_outcome(g.root.children[1].children[1].children[1], out_p2_shot)

# - For b = 2..5, P2 pulls and survives; play goes to Player 1 at
#   g.root.children[b].children[1].children[1]. Append P1 moves there.
g.append_move(g.root.children[2].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1], "Player 1", ["Quit", "Pull"])

# These P1 nodes after two safe pulls are indistinguishable to Player 1, so group them.
g.set_infoset(g.root.children[3].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1], g.root.children[2].children[1].children[1].infoset)

# Outcomes for Player 1 quitting at this stage: P1 gets 0, P2 gets 1
out_quit_p1_after2 = g.add_outcome([0, 1], label="P1 quits after two safe pulls")
g.set_outcome(g.root.children[2].children[1].children[1].children[0], out_quit_p1_after2)
g.set_outcome(g.root.children[3].children[1].children[1].children[0], out_quit_p1_after2)
g.set_outcome(g.root.children[4].children[1].children[1].children[0], out_quit_p1_after2)
g.set_outcome(g.root.children[5].children[1].children[1].children[0], out_quit_p1_after2)

# If Player 1 pulls now:
# - For b = 2 (loaded chamber 2) P1 dies immediately.
out_p1_shot_at3 = g.add_outcome([-1, 1], label="P1 shot on third pull")
g.set_outcome(g.root.children[2].children[1].children[1].children[1], out_p1_shot_at3)

# - For b = 3..5, P1 pulls and survives; play goes to Player 2 at
#   g.root.children[b].children[1].children[1].children[1]. Append P2 moves there.
g.append_move(g.root.children[3].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# These P2 nodes after three safe pulls are indistinguishable to Player 2, so group them.
g.set_infoset(g.root.children[4].children[1].children[1].children[1],
              g.root.children[3].children[1].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1].children[1],
              g.root.children[3].children[1].children[1].children[1].infoset)

# Outcomes for Player 2 quitting at this stage: P2 gets 0, P1 gets 1
out_quit_p2_after3 = g.add_outcome([1, 0], label="P2 quits after three safe pulls")
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[0], out_quit_p2_after3)
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[0], out_quit_p2_after3)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[0], out_quit_p2_after3)

# If Player 2 pulls now:
# - For b = 3 (loaded chamber 3) P2 dies immediately.
out_p2_shot_at4 = g.add_outcome([1, -1], label="P2 shot on fourth pull")
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[1], out_p2_shot_at4)

# - For b = 4..5, P2 pulls and survives; play goes to Player 1 at
#   g.root.children[b].children[1].children[1].children[1].children[1]. Append P1 moves there.
g.append_move(g.root.children[4].children[1].children[1].children[1].children[1], "Player 1",
              ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1], "Player 1",
              ["Quit", "Pull"])

# These P1 nodes after four safe pulls are indistinguishable to Player 1, so group them.
g.set_infoset(g.root.children[5].children[1].children[1].children[1].children[1],
              g.root.children[4].children[1].children[1].children[1].children[1].infoset)

# Outcomes for Player 1 quitting at this stage: P1 gets 0, P2 gets 1
out_quit_p1_after4 = g.add_outcome([0, 1], label="P1 quits after four safe pulls")
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[0], out_quit_p1_after4)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[0], out_quit_p1_after4)

# If Player 1 pulls now:
# - For b = 4 (loaded chamber 4) P1 dies immediately.
out_p1_shot_at5 = g.add_outcome([-1, 1], label="P1 shot on fifth pull")
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[1], out_p1_shot_at5)

# - For b = 5, P1 pulls and survives; play goes to Player 2 at the final node
#   g.root.children[5].children[1].children[1].children[1].children[1].children[1].
# Append Player 2 move there.
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1].children[1], "Player 2",
              ["Quit", "Pull"])

# For this final P2 node (b = 5), if P2 quits -> P2 gets 0, P1 gets 1
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[0],
              out_quit_p2_after3)  # reuse [1,0] outcome

# If P2 pulls here (this is the 6th pull, chamber 5), P2 dies for b=5.
out_p2_shot_at6 = g.add_outcome([1, -1], label="P2 shot on sixth pull")
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[1],
              out_p2_shot_at6)

# Save the EFG
g.to_efg("alternating_russian_roulette_six.efg")