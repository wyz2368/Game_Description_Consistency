import pygambit as gbt

# Construct an extensive-form game for the alternating Russian-roulette-like quitting/pulling game.
# Players: Player 1 (acts first) and Player 2.
# Reasoning about modeling choices (in comments inline):
#
# - The single loaded chamber is chosen by chance among 6 positions (1..6). We model this by a
#   chance move at the root with 6 equiprobable outcomes. Each root child corresponds to a different
#   loaded chamber position. The chance move is the only chance node: subsequent "firing" outcomes
#   are determined by the initial loaded position and the number of pulls so far.
#
# - At each nonterminal decision node the current player has two actions. The first action is "Pull"
#   (attempt to fire the current chamber). The second action is "Quit" (withdraw and let the other
#   player win). We order actions as ["Pull", "Quit"] so that the Pull branch is always child index 0
#   and the Quit branch is always child index 1. This ordering is important because the reasoning
#   about which nodes exist / are grouped into information sets uses those indices.
#
# - If a player Pulls at a node whose current chamber number equals the pre-chosen loaded position,
#   that player dies (payoff -1 to shooter, +1 to opponent). Otherwise the pull is safe and play
#   passes to the other player with the next chamber number (deterministically determined by the
#   loaded position chosen at the root).
#
# - Quitting yields payoff 0 to the quitter and +1 to the other player.
#
# - Imperfect information: at each player's decision nodes they cannot tell which initial loaded
#   position was chosen, only how many safe pulls have occurred. Thus decision nodes at the same
#   depth that are consistent with the same history of survivals are grouped into information sets.
#
# The code below constructs the full tree explicitly without loops or recursion, and sets the
# information sets following the justification above.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating quit/pull six-chamber game")

# 1) Chance move at the root: choose the loaded chamber position among 6 equiprobable positions.
g.append_move(g.root, g.players.chance,
              ["Chamber 1", "Chamber 2", "Chamber 3", "Chamber 4", "Chamber 5", "Chamber 6"])
g.set_chance_probs(g.root.infoset,
                   [gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6),
                    gbt.Rational(1, 6), gbt.Rational(1, 6), gbt.Rational(1, 6)])

# 2) Player 1 moves first at each of the 6 chance outcomes.
#    Actions ordered as ["Pull", "Quit"] so Pull is child index 0 and Quit is child index 1.
g.append_move(g.root.children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[1], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[2], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5], "Player 1", ["Pull", "Quit"])

# 3) Group Player 1's initial decision nodes into a single information set (Player 1 does not know which chamber)
#    We use the infoset of the node for Chamber 2 (root.children[1]) as the reference.
g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)
g.set_infoset(g.root.children[3], g.root.children[1].infoset)
g.set_infoset(g.root.children[4], g.root.children[1].infoset)
g.set_infoset(g.root.children[5], g.root.children[1].infoset)

# 4) Prepare outcome objects to reuse identical payoff vectors.
p1_dies = g.add_outcome([-1, 1], label="Player1 dies")
p2_dies = g.add_outcome([1, -1], label="Player2 dies")
p1_quit = g.add_outcome([0, 1], label="Player1 quits")
p2_quit = g.add_outcome([1, 0], label="Player2 quits")

# 5) Set outcomes for Player 1's Quit actions at the first decision layer (all root children .children[1])
g.set_outcome(g.root.children[0].children[1], p1_quit)
g.set_outcome(g.root.children[1].children[1], p1_quit)
g.set_outcome(g.root.children[2].children[1], p1_quit)
g.set_outcome(g.root.children[3].children[1], p1_quit)
g.set_outcome(g.root.children[4].children[1], p1_quit)
g.set_outcome(g.root.children[5].children[1], p1_quit)

# 6) Handle Pull at root.children[0] (loaded chamber 1): Player 1 pulls into the loaded chamber and dies.
#    That is terminal.
g.set_outcome(g.root.children[0].children[0], p1_dies)

# 7) For the other root children (loaded chamber 2..6), Player 1's Pull is safe and play passes to Player 2.
#    Append Player 2 moves at those nodes. Actions also ["Pull", "Quit"] with Pull as child index 0.
g.append_move(g.root.children[1].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[2].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0], "Player 2", ["Pull", "Quit"])

# 8) Player 2's decision nodes after one survival (for loaded positions 2..6) are indistinguishable to Player 2,
#    so group them into a single information set (use the infoset of the node for Chamber 2 as the base).
g.set_infoset(g.root.children[2].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[3].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[4].children[0], g.root.children[1].children[0].infoset)
g.set_infoset(g.root.children[5].children[0], g.root.children[1].children[0].infoset)

# 9) Set Quit outcomes at these Player 2 nodes (child index 1 of each).
g.set_outcome(g.root.children[1].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[2].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[3].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[4].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[5].children[0].children[1], p2_quit)

# 10) Pull at Player 2's nodes:
#     - For loaded position 2 (root.children[1]) a Pull by Player 2 hits the loaded chamber and Player 2 dies.
g.set_outcome(g.root.children[1].children[0].children[0], p2_dies)

#     - For loaded positions 3..6, Player 2's Pull is safe and play passes back to Player 1.
#       Append Player 1 moves at those deeper nodes.
g.append_move(g.root.children[2].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[3].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0], "Player 1", ["Pull", "Quit"])

# 11) Player 1's decision nodes after two survivals (for loaded positions 3..6) are indistinguishable to Player 1,
#     so group them into a single information set (use the node for Chamber 3 as base).
g.set_infoset(g.root.children[3].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[4].children[0].children[0], g.root.children[2].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0], g.root.children[2].children[0].children[0].infoset)

# 12) Set Quit outcomes for these Player 1 nodes (child index 1).
g.set_outcome(g.root.children[2].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[3].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[4].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[5].children[0].children[0].children[1], p1_quit)

# 13) Pull at Player 1's nodes at this depth:
#     - For loaded position 3 (root.children[2]) a Pull by Player 1 hits the loaded chamber and Player 1 dies.
g.set_outcome(g.root.children[2].children[0].children[0].children[0], p1_dies)

#     - For loaded positions 4..6, Player 1's Pull is safe and play passes to Player 2 again.
#       Append Player 2 moves at those nodes.
g.append_move(g.root.children[3].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[4].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# 14) Player 2's decision nodes after three survivals (loaded positions 4..6) are indistinguishable to Player 2.
#     Group nodes for Chamber 5 and Chamber 6 to the infoset of Chamber 4's node.
g.set_infoset(g.root.children[4].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)
g.set_infoset(g.root.children[5].children[0].children[0].children[0], g.root.children[3].children[0].children[0].children[0].infoset)

# 15) Set Quit outcomes for these Player 2 nodes (child index 1).
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[1], p2_quit)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[1], p2_quit)

# 16) Pull at Player 2 nodes at this depth:
#     - For loaded position 4 (root.children[3]) a Pull by Player 2 hits the loaded chamber and Player 2 dies.
g.set_outcome(g.root.children[3].children[0].children[0].children[0].children[0], p2_dies)

#     - For loaded positions 5 and 6, Player 2's Pull is safe and play passes back to Player 1.
#       Append Player 1 moves at those deeper nodes.
g.append_move(g.root.children[4].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0], "Player 1", ["Pull", "Quit"])

# 17) After four survivals, Player 1 has decision nodes for loaded positions 5 and 6. These two nodes are
#     indistinguishable to Player 1 (group them). Use Chamber 5 node as the base.
g.set_infoset(g.root.children[5].children[0].children[0].children[0].children[0], g.root.children[4].children[0].children[0].children[0].children[0].infoset)

# 18) Set Quit outcomes for these Player 1 nodes (child index 1).
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[1], p1_quit)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[1], p1_quit)

# 19) Pull at Player 1 nodes at this depth:
#     - For loaded position 5 (root.children[4]) a Pull by Player 1 hits loaded chamber and Player 1 dies.
g.set_outcome(g.root.children[4].children[0].children[0].children[0].children[0].children[0], p1_dies)

#     - For loaded position 6 (root.children[5]) a Pull by Player 1 is safe (this is the 5th safe pull) and
#       play passes to Player 2 for the final (6th) decision. Append that final Player 2 move.
g.append_move(g.root.children[5].children[0].children[0].children[0].children[0].children[0], "Player 2", ["Pull", "Quit"])

# 20) The final Player 2 node (reached only if loaded position is 6 and five safe pulls have occurred):
#     - If Player 2 Pulls here, the 6th chamber is fired and Player 2 dies (p2_dies).
#     - If Player 2 Quits here, Player 2 withdraws and Player 1 wins (p2_quit).
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[0], p2_dies)
g.set_outcome(g.root.children[5].children[0].children[0].children[0].children[0].children[0].children[1], p2_quit)

# 21) Save the constructed EFG to a file.
g.to_efg("russian_roulette.efg")