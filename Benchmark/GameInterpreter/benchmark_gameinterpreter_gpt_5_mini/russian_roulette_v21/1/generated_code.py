import pygambit as gbt

# Reasoning and construction in comments below:
# We construct an extensive-form game for two players alternating pulls of a 6-chamber revolver.
# A chance node at the root selects which chamber (0..5) is the loaded one. Each root child
# corresponds to one possible loaded chamber. Players observe only whether a shot fired in past
# pulls (i.e., who died) but not which chamber was initially loaded. Thus decision nodes that
# are consistent with the same number of previous empty pulls are in the same information set.
#
# Conventions:
# - Players: "Player 1" (acts first) and "Player 2".
# - At each decision a player has two actions: "Quit" (withdraw and survive for sure) and "Pull".
# - Payoffs:
#    * If a player quits: quitting player gets 0, the other player gets 1.
#    * If a player pulls and the current chamber is loaded: the pulling player dies and gets -1,
#      the other player gets 1.
#    * If a player pulls and the current chamber is empty: play passes to the other player.
#
# We avoid loops/recursion by writing out every branch for the six possible loaded-chamber indices.
# We also follow the provided instruction about setting information sets only after the relevant
# moves exist. We use gbt.Rational for chance probabilities.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating Russian roulette with 6 chambers")

# Root chance selects loaded chamber among 6 possibilities (indices 0..5)
g.append_move(g.root, g.players.chance, ["Loaded 0", "Loaded 1", "Loaded 2", "Loaded 3", "Loaded 4", "Loaded 5"])
# Equal probability 1/6 for each loaded-chamber action
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# --- Turn 1 (Player 1 acts at each root child). Append P1 moves on all 6 chance branches.
g.append_move(g.root.children[0], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[2], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5], "Player 1", ["Quit", "Pull"])

# The decision nodes for Turn 1 are indistinguishable to Player 1: group them into one infoset.
# Use the infoset of the first node as the representative.
g.set_infoset(g.root.children[1], g.root.children[0].infoset)
g.set_infoset(g.root.children[2], g.root.children[0].infoset)
g.set_infoset(g.root.children[3], g.root.children[0].infoset)
g.set_infoset(g.root.children[4], g.root.children[0].infoset)
g.set_infoset(g.root.children[5], g.root.children[0].infoset)

# Set outcomes for the "Quit" action at Turn 1: P1 quits -> P1:0, P2:1
quit_p1_outcome = g.add_outcome([0, 1], label="P1 quits -> P2 wins")
g.set_outcome(g.root.children[0].children[0], quit_p1_outcome)
g.set_outcome(g.root.children[1].children[0], quit_p1_outcome)
g.set_outcome(g.root.children[2].children[0], quit_p1_outcome)
g.set_outcome(g.root.children[3].children[0], quit_p1_outcome)
g.set_outcome(g.root.children[4].children[0], quit_p1_outcome)
g.set_outcome(g.root.children[5].children[0], quit_p1_outcome)

# Handle the "Pull" action at Turn 1:
# - If loaded index == 0 (root.children[0]) then Pull fires and P1 dies.
p1_death_outcome = g.add_outcome([-1, 1], label="P1 pulls and dies")
g.set_outcome(g.root.children[0].children[1], p1_death_outcome)

# - For loaded indices 1..5, Pull is empty and play passes to Player 2 at those nodes.
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[2].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1], "Player 2", ["Quit", "Pull"])

# --- Turn 2 (Player 2 acts). Group Turn 2 nodes (indices 1..5) into one infoset.
g.set_infoset(g.root.children[2].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[3].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1], g.root.children[1].children[1].infoset)

# P2 "Quit" yields P2:0, P1:1
quit_p2_outcome = g.add_outcome([1, 0], label="P2 quits -> P1 wins")
g.set_outcome(g.root.children[1].children[1].children[0], quit_p2_outcome)
g.set_outcome(g.root.children[2].children[1].children[0], quit_p2_outcome)
g.set_outcome(g.root.children[3].children[1].children[0], quit_p2_outcome)
g.set_outcome(g.root.children[4].children[1].children[0], quit_p2_outcome)
g.set_outcome(g.root.children[5].children[1].children[0], quit_p2_outcome)

# P2 "Pull":
# - If loaded index == 1, P2 dies on this pull.
p2_death_outcome = g.add_outcome([1, -1], label="P2 pulls and dies")
g.set_outcome(g.root.children[1].children[1].children[1], p2_death_outcome)

# - For loaded indices 2..5, P2's Pull is empty and play passes to Player 1.
g.append_move(g.root.children[2].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1], "Player 1", ["Quit", "Pull"])

# --- Turn 3 (Player 1 acts after two empty pulls). Group Turn 3 nodes (indices 2..5).
g.set_infoset(g.root.children[3].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1], g.root.children[2].children[1].children[1].infoset)

# P1 "Quit" -> P1:0, P2:1 at these Turn 3 nodes
g.set_outcome(g.root.children[2].children[1].children[1].children[0], quit_p1_outcome)
g.set_outcome(g.root.children[3].children[1].children[1].children[0], quit_p1_outcome)
g.set_outcome(g.root.children[4].children[1].children[1].children[0], quit_p1_outcome)
g.set_outcome(g.root.children[5].children[1].children[1].children[0], quit_p1_outcome)

# P1 "Pull":
# - If loaded index == 2, P1 dies now.
g.set_outcome(g.root.children[2].children[1].children[1].children[1], p1_death_outcome)

# - For loaded indices 3..5, Pull is empty and play passes to Player 2.
g.append_move(g.root.children[3].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# --- Turn 4 (Player 2 acts after three empty pulls). Group Turn 4 nodes (indices 3..5).
g.set_infoset(g.root.children[4].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)

# P2 "Quit" -> P2:0, P1:1 at these Turn 4 nodes
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[0], quit_p2_outcome)
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[0], quit_p2_outcome)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[0], quit_p2_outcome)

# P2 "Pull":
# - If loaded index == 3, P2 dies now.
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[1], p2_death_outcome)

# - For loaded indices 4..5, Pull is empty and play passes to Player 1.
g.append_move(g.root.children[4].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])

# --- Turn 5 (Player 1 acts after four empty pulls). Group Turn 5 nodes (indices 4..5).
g.set_infoset(g.root.children[5].children[1].children[1].children[1].children[1], g.root.children[4].children[1].children[1].children[1].children[1].infoset)

# P1 "Quit" -> P1:0, P2:1 at these Turn 5 nodes
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[0], quit_p1_outcome)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[0], quit_p1_outcome)

# P1 "Pull":
# - If loaded index == 4, P1 dies now.
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[1], p1_death_outcome)

# - For loaded index 5, Pull is empty and play passes to Player 2 for the 6th pull.
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# --- Turn 6 (Player 2 acts only in the branch where loaded index == 5).
# No infoset grouping needed (singleton).
# P2 "Quit" -> P2:0, P1:1
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[0], quit_p2_outcome)

# P2 "Pull" -> loaded == 5, P2 dies on the 6th pull.
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[1], p2_death_outcome)

# Save the EFG
g.to_efg("alternating_russian_roulette_6chambers.efg")