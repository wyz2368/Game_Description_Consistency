import pygambit as gbt

# Russian roulette with a six-chamber revolver, two players P1 and P2 alternating.
# Chance selects which chamber (0..5) contains the bullet. Players do not observe the selection.
# At each decision a player chooses between quitting (guaranteed survival, other player wins)
# or pulling the trigger (may die if the current chamber is the loaded one).
#
# The modeling decision: label actions as ["Quit", "Pull"] so that the Pull branch is
# always child index 1. This matches the information-set grouping scheme described in the prompt,
# which references many nodes as ".children[1]".
#
# Information structure: when a player faces a decision they know how many safe pulls have occurred,
# but not the bullet position. Thus for a given turn number (count of previous safe pulls)
# all nodes for the same player must be in the same information set.
#
# We build the tree explicitly without loops or recursion, and we use gbt.Rational for chance probs.

g = gbt.Game.new_tree(players=["P1", "P2"],
                      title="Six-chamber russian roulette, alternating players")

# Chance at the root selects which chamber is loaded (0..5).
g.append_move(g.root, g.players.chance, ["Chamber 0", "Chamber 1", "Chamber 2", "Chamber 3", "Chamber 4", "Chamber 5"])
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Create outcome objects for reuse:
# P1_quit: P1 quits -> P1 gets 0, P2 gets 1
# P2_quit: P2 quits -> P1 gets 1, P2 gets 0
# P1_die: P1 pulls and hits bullet -> P1 gets -1, P2 gets 1
# P2_die: P2 pulls and hits bullet -> P1 gets 1, P2 gets -1
P1_quit = g.add_outcome([0, 1], label="P1 quits")
P2_quit = g.add_outcome([1, 0], label="P2 quits")
P1_die = g.add_outcome([-1, 1], label="P1 dies")
P2_die = g.add_outcome([1, -1], label="P2 dies")

# Append P1's initial move for each possible chamber (root children 0..5).
# Actions order is ["Quit", "Pull"] so that children[0] is Quit terminal, children[1] is Pull branch.
g.append_move(g.root.children[0], "P1", ["Quit", "Pull"])
g.append_move(g.root.children[1], "P1", ["Quit", "Pull"])
g.append_move(g.root.children[2], "P1", ["Quit", "Pull"])
g.append_move(g.root.children[3], "P1", ["Quit", "Pull"])
g.append_move(g.root.children[4], "P1", ["Quit", "Pull"])
g.append_move(g.root.children[5], "P1", ["Quit", "Pull"])

# All P1 initial nodes (turn 1) are in the same information set (they differ only by bullet position).
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Set outcomes for P1 quitting at the initial decision nodes (children[0] of each root child).
g.set_outcome(g.root.children[0].children[0], P1_quit)
g.set_outcome(g.root.children[1].children[0], P1_quit)
g.set_outcome(g.root.children[2].children[0], P1_quit)
g.set_outcome(g.root.children[3].children[0], P1_quit)
g.set_outcome(g.root.children[4].children[0], P1_quit)
g.set_outcome(g.root.children[5].children[0], P1_quit)

# For chamber 0: if P1 pulls (child index 1) he dies immediately.
g.set_outcome(g.root.children[0].children[1], P1_die)

# For chambers 1..5: P1 pulls and survives (since loaded chamber != 0), so we must append P2 moves
# at the Pull child (which is children[1] for each root child).
g.append_move(g.root.children[1].children[1], "P2", ["Quit", "Pull"])
g.append_move(g.root.children[2].children[1], "P2", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1], "P2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1], "P2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1], "P2", ["Quit", "Pull"])

# Group all P2 first-turn nodes (these occur after one safe pull) into the same infoset.
# Use the node at chamber 1 as the representative infoset.
g.set_infoset(g.root.children[2].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[3].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1], g.root.children[1].children[1].infoset)

# Set outcomes for P2 quitting at their first-turn nodes (children[0] of each P2 node).
g.set_outcome(g.root.children[1].children[1].children[0], P2_quit)
g.set_outcome(g.root.children[2].children[1].children[0], P2_quit)
g.set_outcome(g.root.children[3].children[1].children[0], P2_quit)
g.set_outcome(g.root.children[4].children[1].children[0], P2_quit)
g.set_outcome(g.root.children[5].children[1].children[0], P2_quit)

# On P2's first-turn Pull (children[1]):
# - For chamber 1: P2 dies immediately.
g.set_outcome(g.root.children[1].children[1].children[1], P2_die)

# - For chambers 2..5: P2 pulls and survives, so the play passes back to P1.
#   Append P1 moves at those nodes (these are P1's turn 2 nodes).
g.append_move(g.root.children[2].children[1].children[1], "P1", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1].children[1], "P1", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1], "P1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1], "P1", ["Quit", "Pull"])

# Group P1 turn 2 nodes (occur after two safe pulls) together.
g.set_infoset(g.root.children[3].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1], g.root.children[2].children[1].children[1].infoset)

# Set outcomes for P1 quitting at P1 turn 2 nodes (children[0] of these nodes).
g.set_outcome(g.root.children[2].children[1].children[1].children[0], P1_quit)
g.set_outcome(g.root.children[3].children[1].children[1].children[0], P1_quit)
g.set_outcome(g.root.children[4].children[1].children[1].children[0], P1_quit)
g.set_outcome(g.root.children[5].children[1].children[1].children[0], P1_quit)

# On P1's turn 2 Pull (children[1]):
# - For chamber 2: P1 dies at this pull.
g.set_outcome(g.root.children[2].children[1].children[1].children[1], P1_die)

# - For chambers 3..5: P1 pulls and survives, play passes to P2 (turn 2).
g.append_move(g.root.children[3].children[1].children[1].children[1], "P2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1].children[1], "P2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1], "P2", ["Quit", "Pull"])

# Group P2 turn 2 nodes (occur after three safe pulls) together.
g.set_infoset(g.root.children[4].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)

# Set outcomes for P2 quitting at these nodes (children[0]).
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[0], P2_quit)
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[0], P2_quit)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[0], P2_quit)

# On P2's turn 2 Pull (children[1]):
# - For chamber 3: P2 dies at this pull.
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[1], P2_die)

# - For chambers 4..5: P2 pulls and survives, play passes back to P1 (turn 3).
g.append_move(g.root.children[4].children[1].children[1].children[1].children[1], "P1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1], "P1", ["Quit", "Pull"])

# Group P1 turn 3 nodes (occur after four safe pulls) together.
g.set_infoset(g.root.children[5].children[1].children[1].children[1].children[1], g.root.children[4].children[1].children[1].children[1].children[1].infoset)

# Set outcomes for P1 quitting at turn 3 nodes (children[0]).
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[0], P1_quit)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[0], P1_quit)

# On P1's turn 3 Pull (children[1]):
# - For chamber 4: P1 dies at this pull.
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[1], P1_die)

# - For chamber 5: P1 pulls and survives, play passes to P2 for his third turn (after five safe pulls).
#   This node exists only for chamber 5.
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1].children[1], "P2", ["Quit", "Pull"])

# For P2 at turn 3 (this occurs only for chamber 5); quitting gives P2_quit outcome at children[0].
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[0], P2_quit)

# For P2's turn 3 Pull (children[1]):
# - For chamber 5: P2 dies at this pull.
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[1], P2_die)

# Now save the constructed EFG.
g.to_efg("russian_roulette_six.efg")