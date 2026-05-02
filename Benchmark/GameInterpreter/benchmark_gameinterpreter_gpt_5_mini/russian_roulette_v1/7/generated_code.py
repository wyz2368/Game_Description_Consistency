import pygambit as gbt

# Build an extensive-form game for alternating play with a 6-chamber revolver.
# Reasoning (in comments):
# - Chance selects the bullet position among 6 chambers (positions 1..6), each with probability 1/6.
# - The current chamber fired on the first pull is chamber 1. Each pull advances to the next chamber.
# - Players do not observe the bullet position; they only observe the history (who pulled and whether they survived).
# - On each turn the active player chooses Pull or Quit. Pull may kill if the current chamber is the loaded one.
# - If a player quits, he gets 0 and the other player gets 1. If a player is shot, he gets -1 and the other gets 1.
# - We explicitly expand all branches up to the sixth pull (someone must be shot by then).
# - We set information sets so that a player cannot distinguish different chance initializations but can distinguish number of prior pulls.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating Russian Roulette (6-chamber)")

# Chance selects the bullet position among 6 chambers.
g.append_move(g.root, g.players.chance, ["Position 1", "Position 2", "Position 3", "Position 4", "Position 5", "Position 6"])
# Set equal probabilities 1/6 for each position.
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Pre-create commonly used outcomes.
p1_dies = g.add_outcome([-1, 1], label="P1 killed")
p2_dies = g.add_outcome([1, -1], label="P2 killed")
p1_quits = g.add_outcome([0, 1], label="P1 quits")
p2_quits = g.add_outcome([1, 0], label="P2 quits")

# ===============
# First pull: Player 1 at each chance child (chamber 1 is fired).
# Actions order: ["Pull", "Quit"] so child 0 = Pull, child 1 = Quit
# ===============
g.append_move(g.root.children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[1], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[2], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5], "Player 1", ["Pull", "Quit"])

# Set Player 1 quitting outcomes (for each initial bullet position).
g.set_outcome(g.root.children[0].children[1], p1_quits)
g.set_outcome(g.root.children[1].children[1], p1_quits)
g.set_outcome(g.root.children[2].children[1], p1_quits)
g.set_outcome(g.root.children[3].children[1], p1_quits)
g.set_outcome(g.root.children[4].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[1], p1_quits)

# Handle Pull results on first pull:
# - If bullet position is 1 (root.children[0]), Pull kills P1.
g.set_outcome(g.root.children[0].children[0], p1_dies)
# - Otherwise (initial positions 2..6), Pull survives and leads to Player 2's first decision node.
g.append_move(g.root.children[1].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "Player 2", ["Pull", "Quit"])

# Set Player 2 quitting outcomes for these first-turn nodes.
g.set_outcome(g.root.children[1].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[2].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[3].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[4].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[5].children[0].children[1], p2_quits)

# Handle Player 2 Pull on first-turn:
# - If bullet position is 2 (root.children[1]), Pull kills P2.
g.set_outcome(g.root.children[1].children[0].children[0], p2_dies)
# - Otherwise (initial positions 3..6), Pull survives and leads to Player 1's second-turn decision node.
g.append_move(g.root.children[2].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "Player 1", ["Pull", "Quit"])

# Set Player 1 quitting outcomes for second-turn nodes.
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quits)

# Handle Player 1 Pull on second-turn:
# - If bullet position is 3 (root.children[2]), Pull kills P1.
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_dies)
# - Otherwise (initial positions 4..6), Pull survives and leads to Player 2's second-turn node.
g.append_move(g.root.children[3].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Set Player 2 quitting outcomes for second-turn nodes.
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quits)

# Handle Player 2 Pull on second-turn:
# - If bullet position is 4 (root.children[3]), Pull kills P2.
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_dies)
# - Otherwise (initial positions 5..6), Pull survives and leads to Player 1's third-turn node.
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])

# Set Player 1 quitting outcomes for third-turn nodes.
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quits)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quits)

# Handle Player 1 Pull on third-turn:
# - If bullet position is 5 (root.children[4]), Pull kills P1.
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_dies)
# - Otherwise (initial position 6, root.children[5]) Pull survives and leads to Player 2's third-turn node.
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# Set Player 2 quitting outcome for the third-turn node (initial pos 6).
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quits)
# Handle Player 2 Pull on third-turn:
# - If bullet position is 6 (root.children[5]), Pull kills P2.
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_dies)

# =====================
# Set information sets to reflect imperfect information (players cannot see bullet position).
# The following grouping follows the mapping in the problem statement:
# =====================

# Group P1's first-turn decision nodes (before any pull): all 6 chance-child nodes.
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# Group P2's first-turn decision nodes (after one survived pull): nodes reached when initial bullet is in positions 2..6.
# These are g.root.children[1].children[0] .. g.root.children[5].children[0].
g.set_infoset(g.root.children[1].children[0], g.root.children[2].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[2].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[2].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[2].children[0].infoset)

# Group P1's second-turn decision nodes (after two survived pulls): nodes for initial positions 3..6.
# These are g.root.children[2].children[0].children[0] .. g.root.children[5].children[0].children[0].
g.set_infoset(g.root.children[2].children[0].children[0], g.root.children[3].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[3].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[3].children[0].children[0].infoset)

# Group P2's second-turn decision nodes (after three survived pulls): nodes for initial positions 4..6.
# These are g.root.children[3].children[0].children[0].children[0] .. g.root.children[5].children[0].children[0].children[0].
g.set_infoset(g.root.children[3].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].infoset)

# Group P1's third-turn decision nodes (after four survived pulls): nodes for initial positions 5..6.
# These are g.root.children[4].children[0].children[0].children[0].children[0] and g.root.children[5].children[0].children[0].children[0].children[0].
g.set_infoset(g.root.children[4].children[0].children[0].children[0].children[0], g.root.children[5].children[0].children[0].children[0].children[0].infoset)

# Save to EFG file.
g.to_efg("russian_roulette_6.efg")