import pygambit as gbt

# Create the game with two players: "Player 1" and "Player 2".
# Title describes the game: alternating trigger pulls with a six-chamber revolver.
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternating Russian roulette")

# Reasoning (encoded as comments):
# - We model the unknown bullet position by an initial chance node selecting positions 1..6.
# - If the current pull number equals the selected position, the gun fires and the acting player dies.
# - Decision nodes use actions ordered as ["Quit", "Pull"] so that .children[0] is the Quit branch
#   (immediate terminal with the quitter getting 0 and the other player 1),
#   and .children[1] is the Pull branch (which may be terminal if the gun fires,
#   or continues to the opponent otherwise).
# - We explicitly construct all branches (no loops, no recursion).
# - After building the full tree we group nodes into information sets so that a player
#   who has observed the same number of prior surviving pulls cannot distinguish
#   which initial bullet position was drawn.

# Chance node: bullet position 1..6
g.append_move(g.root, g.players.chance, ["Pos1", "Pos2", "Pos3", "Pos4", "Pos5", "Pos6"])

# Player 1 initial decision nodes at each chance outcome (positions 1..6)
g.append_move(g.root.children[0], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[2], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5], "Player 1", ["Quit", "Pull"])

# For initial positions 2..6, if Player 1 pulls and survives, Player 2 gets a decision (first P2-turn).
g.append_move(g.root.children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[2].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1], "Player 2", ["Quit", "Pull"])

# For initial positions 3..6, if P1 and P2 have both pulled and survived, Player 1 gets a second-turn decision.
g.append_move(g.root.children[2].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[3].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1], "Player 1", ["Quit", "Pull"])

# For initial positions 4..6, after three surviving pulls, Player 2 gets a second-turn decision.
g.append_move(g.root.children[3].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[4].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# For initial positions 5..6, after four surviving pulls, Player 1 gets a third-turn decision.
g.append_move(g.root.children[4].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1], "Player 1", ["Quit", "Pull"])

# For initial position 6 only, after five surviving pulls, Player 2 gets a third-turn decision.
g.append_move(g.root.children[5].children[1].children[1].children[1].children[1].children[1], "Player 2", ["Quit", "Pull"])

# Outcomes (reuse common outcomes)
p1_quit = g.add_outcome([0, 1], label="P1 quits")    # P1 quits => P1 0, P2 1
p2_quit = g.add_outcome([1, 0], label="P2 quits")    # P2 quits => P1 1, P2 0
p1_die = g.add_outcome([-1, 1], label="P1 dies")     # P1 pulls and dies => P1 -1, P2 1
p2_die = g.add_outcome([1, -1], label="P2 dies")     # P2 pulls and dies => P1 1, P2 -1

# Set Quit outcomes for every decision node (Quit is .children[0])
# Player 1 initial quits
g.set_outcome(g.root.children[0].children[0], p1_quit)
g.set_outcome(g.root.children[1].children[0], p1_quit)
g.set_outcome(g.root.children[2].children[0], p1_quit)
g.set_outcome(g.root.children[3].children[0], p1_quit)
g.set_outcome(g.root.children[4].children[0], p1_quit)
g.set_outcome(g.root.children[5].children[0], p1_quit)

# Player 2 first-turn quits (nodes are at root.children[i].children[1])
g.set_outcome(g.root.children[1].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[2].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[3].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[4].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[5].children[1].children[0], p2_quit)

# Player 1 second-turn quits (nodes are at root.children[i].children[1].children[1] for i>=2)
g.set_outcome(g.root.children[2].children[1].children[1].children[0], p1_quit)
g.set_outcome(g.root.children[3].children[1].children[1].children[0], p1_quit)
g.set_outcome(g.root.children[4].children[1].children[1].children[0], p1_quit)
g.set_outcome(g.root.children[5].children[1].children[1].children[0], p1_quit)

# Player 2 second-turn quits (nodes are at root.children[i].children[1].children[1].children[1] for i>=3)
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[0], p2_quit)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[0], p2_quit)

# Player 1 third-turn quits (nodes are at root.children[i].children[1].children[1].children[1].children[1] for i>=4)
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[0], p1_quit)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[0], p1_quit)

# Player 2 third-turn quits (position 6 branch)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[0], p2_quit)

# Now set outcomes for Pull actions that result in immediate death (when the pull count equals the bullet position).
# Pull is .children[1] at the relevant node.

# Position 1: Player 1's initial Pull fires.
g.set_outcome(g.root.children[0].children[1], p1_die)

# Position 2: Player 2's first Pull (node at root.children[1].children[1]) fires.
g.set_outcome(g.root.children[1].children[1].children[1], p2_die)

# Position 3: Player 1's second-turn Pull fires (node at root.children[2].children[1].children[1])
g.set_outcome(g.root.children[2].children[1].children[1].children[1], p1_die)

# Position 4: Player 2's second-turn Pull fires (node at root.children[3].children[1].children[1].children[1])
g.set_outcome(g.root.children[3].children[1].children[1].children[1].children[1], p2_die)

# Position 5: Player 1's third-turn Pull fires (node at root.children[4].children[1].children[1].children[1].children[1])
g.set_outcome(g.root.children[4].children[1].children[1].children[1].children[1].children[1], p1_die)

# Position 6: Player 2's third-turn Pull fires (deepest node)
g.set_outcome(g.root.children[5].children[1].children[1].children[1].children[1].children[1].children[1], p2_die)

# Note: For all other Pull branches the branch continues to the opponent's decision node;
# those continuations were already constructed above (and are not terminal outcomes here).

# Now set up the information sets as described:
# Player 1 initial decision (all six chance outcomes are indistinguishable to P1 at the start)
g.set_infoset(g.root.children[1], g.root.children[0].infoset)
g.set_infoset(g.root.children[2], g.root.children[0].infoset)
g.set_infoset(g.root.children[3], g.root.children[0].infoset)
g.set_infoset(g.root.children[4], g.root.children[0].infoset)
g.set_infoset(g.root.children[5], g.root.children[0].infoset)

# Player 2 first-turn decision (after one surviving pull): nodes under initial positions 2..6
g.set_infoset(g.root.children[2].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[3].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1], g.root.children[1].children[1].infoset)

# Player 1 second-turn decision (after two surviving pulls): nodes under initial positions 3..6
g.set_infoset(g.root.children[3].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[4].children[1].children[1], g.root.children[2].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1], g.root.children[2].children[1].children[1].infoset)

# Player 2 second-turn decision (after three surviving pulls): nodes under initial positions 4..6
g.set_infoset(g.root.children[4].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)
g.set_infoset(g.root.children[5].children[1].children[1].children[1], g.root.children[3].children[1].children[1].children[1].infoset)

# Player 1 third-turn decision (after four surviving pulls): nodes under initial positions 5..6
g.set_infoset(g.root.children[5].children[1].children[1].children[1].children[1], g.root.children[4].children[1].children[1].children[1].children[1].infoset)

# Set chance probabilities equally for positions 1..6
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# Save the EFG to a file.
g.to_efg("russian_roulette.efg")