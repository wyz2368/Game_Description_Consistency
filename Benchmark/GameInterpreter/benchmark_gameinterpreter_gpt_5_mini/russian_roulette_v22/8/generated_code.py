import pygambit as gbt

# Construct the extensive-form game for alternating Russian Roulette (6 chambers).
# Players: Player 1 acts first, then Player 2, and so on.
# On each turn the active player chooses "Quit" (withdraw, gets 0; the other player gets 1)
# or "Pull" (pull the trigger). A pull either fires (acting player gets -1, other gets 1)
# or clicks and play continues with one fewer unpulled chamber.
#
# Thought process (also repeated in-line as comments):
# - The history (how many pulls have happened and whose turn it is) is common knowledge.
# - Chance nodes model whether the gun fires. There are no nontrivial information sets
#   for players, so we don't merge any decision nodes.
# - We unroll the full tree explicitly from 6 remaining chambers down to 1.
# - We avoid loops/recursion and avoid the '+' operator as requested.

g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Alternating Russian Roulette (6-chamber)")

# Root decision: Player 1 chooses Quit or Pull.
g.append_move(g.root, "Player 1", ["Quit", "Pull"])

# Terminal outcome objects reused where possible:
p1_quits = g.add_outcome([0, 1], label="P1 quits (P2 wins)")
p2_quits = g.add_outcome([1, 0], label="P2 quits (P1 wins)")
p1_dies = g.add_outcome([-1, 1], label="P1 dies (P2 wins)")
p2_dies = g.add_outcome([1, -1], label="P2 dies (P1 wins)")

# Player 1: Quit branch (immediate terminal)
p1_quit_node = g.root.children[0]
g.set_outcome(p1_quit_node, p1_quits)

# Player 1: Pull branch -> chance with 6 remaining chambers
p1_pull_node = g.root.children[1]
g.append_move(p1_pull_node, g.players.chance, ["Fire6", "Click6"])
# Fire with probability 1/6, Click with probability 5/6
g.set_chance_probs(p1_pull_node.infoset, [gbt.Rational(1, 6), gbt.Rational(5, 6)])

# Chance outcome: Fire immediately kills Player 1
p1_fire6 = p1_pull_node.children[0]
g.set_outcome(p1_fire6, p1_dies)

# Chance outcome: Click -> now Player 2 decides with 5 remaining chambers
p1_click6 = p1_pull_node.children[1]
g.append_move(p1_click6, "Player 2", ["Quit", "Pull"])

# Player 2 Quit after first click -> terminal
p2_quit_after1 = p1_click6.children[0]
g.set_outcome(p2_quit_after1, p2_quits)

# Player 2 Pull -> chance with 5 remaining chambers
p2_pull1 = p1_click6.children[1]
g.append_move(p2_pull1, g.players.chance, ["Fire5", "Click5"])
g.set_chance_probs(p2_pull1.infoset, [gbt.Rational(1, 5), gbt.Rational(4, 5)])

# Fire on Player 2's pull -> Player 2 dies
p2_fire5 = p2_pull1.children[0]
g.set_outcome(p2_fire5, p2_dies)

# Click -> Player 1's turn with 4 remaining chambers
p2_click5 = p2_pull1.children[1]
g.append_move(p2_click5, "Player 1", ["Quit", "Pull"])

# Player 1 Quit at this stage -> terminal
p1_quit_after2 = p2_click5.children[0]
g.set_outcome(p1_quit_after2, p1_quits)

# Player 1 Pull -> chance with 4 remaining chambers
p1_pull2 = p2_click5.children[1]
g.append_move(p1_pull2, g.players.chance, ["Fire4", "Click4"])
g.set_chance_probs(p1_pull2.infoset, [gbt.Rational(1, 4), gbt.Rational(3, 4)])

# Fire -> Player 1 dies
p1_fire4 = p1_pull2.children[0]
g.set_outcome(p1_fire4, p1_dies)

# Click -> Player 2's turn with 3 remaining chambers
p1_click4 = p1_pull2.children[1]
g.append_move(p1_click4, "Player 2", ["Quit", "Pull"])

# Player 2 Quit -> terminal
p2_quit_after3 = p1_click4.children[0]
g.set_outcome(p2_quit_after3, p2_quits)

# Player 2 Pull -> chance with 3 remaining chambers
p2_pull3 = p1_click4.children[1]
g.append_move(p2_pull3, g.players.chance, ["Fire3", "Click3"])
g.set_chance_probs(p2_pull3.infoset, [gbt.Rational(1, 3), gbt.Rational(2, 3)])

# Fire -> Player 2 dies
p2_fire3 = p2_pull3.children[0]
g.set_outcome(p2_fire3, p2_dies)

# Click -> Player 1's turn with 2 remaining chambers
p2_click3 = p2_pull3.children[1]
g.append_move(p2_click3, "Player 1", ["Quit", "Pull"])

# Player 1 Quit -> terminal
p1_quit_after4 = p2_click3.children[0]
g.set_outcome(p1_quit_after4, p1_quits)

# Player 1 Pull -> chance with 2 remaining chambers
p1_pull4 = p2_click3.children[1]
g.append_move(p1_pull4, g.players.chance, ["Fire2", "Click2"])
g.set_chance_probs(p1_pull4.infoset, [gbt.Rational(1, 2), gbt.Rational(1, 2)])

# Fire -> Player 1 dies
p1_fire2 = p1_pull4.children[0]
g.set_outcome(p1_fire2, p1_dies)

# Click -> Player 2's turn with 1 remaining chamber
p1_click2 = p1_pull4.children[1]
g.append_move(p1_click2, "Player 2", ["Quit", "Pull"])

# Player 2 Quit -> terminal
p2_quit_final = p1_click2.children[0]
g.set_outcome(p2_quit_final, p2_quits)

# Player 2 Pull when only 1 chamber remains: it fires for certain.
# We model this as a chance node with a single "Fire1" action with probability 1.
p2_pull_final = p1_click2.children[1]
g.append_move(p2_pull_final, g.players.chance, ["Fire1"])
g.set_chance_probs(p2_pull_final.infoset, [gbt.Rational(1, 1)])

# Fire1 -> Player 2 dies
p2_fire1 = p2_pull_final.children[0]
g.set_outcome(p2_fire1, p2_dies)

# Save the EFG
g.to_efg("alternating_russian_roulette_6chambers.efg")