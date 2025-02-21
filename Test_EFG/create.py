import pygambit as gbt

g = gbt.Game.new_tree(players=["Alice", "Bob", "Cindy"], title="test_game")

outcome_1 = g.add_outcome([1, 2, 1], label="")
outcome_2 = g.add_outcome([2, 1, 1], label="")
outcome_3 = g.add_outcome([0, 0, 2], label="")
outcome_4 = g.add_outcome([3, 2, 2], label="")
outcome_5 = g.add_outcome([2, 3, 3], label="")
outcome_6 = g.add_outcome([1, 1, 1], label="")
outcome_7 = g.add_outcome([2, 2, 2], label="")
outcome_8 = g.add_outcome([3, 3, 3], label="")

g.append_move(g.root, "Alice", ["A", "B"])
g.append_move(g.root.children[0], "Bob", ['C', 'D'])
g.append_move(g.root.children[1], "Alice", ["E", "F"])

g.append_move(g.root.children[0].children[0], "Cindy", ["G", "H"])
g.append_move(g.root.children[0].children[1], "Cindy", ["G", "H"])

g.append_move(g.root.children[1].children[0], "Cindy", ["G", "H"])
g.append_move(g.root.children[1].children[1], "Cindy", ["G", "H"])

g.set_outcome(g.root.children[0].children[0].children[0], outcome_1)
g.set_outcome(g.root.children[0].children[0].children[1], outcome_2)
g.set_outcome(g.root.children[0].children[1].children[0], outcome_3)
g.set_outcome(g.root.children[0].children[1].children[1], outcome_4)
g.set_outcome(g.root.children[1].children[0].children[0], outcome_5)
g.set_outcome(g.root.children[1].children[0].children[1], outcome_6)
g.set_outcome(g.root.children[1].children[1].children[0], outcome_7)
g.set_outcome(g.root.children[1].children[1].children[1], outcome_8)


g.set_infoset(g.root.children[1].children[0], g.root.children[1].children[1].infoset)
g.set_infoset(g.root.children[0].children[0], g.root.children[0].children[1].infoset)

# Save the EFG
efg = g.write(format='native')

with open("many_sim_gen.efg", "w") as file:
    file.write(efg)