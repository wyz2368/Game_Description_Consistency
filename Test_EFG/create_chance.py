import pygambit as gbt

g = gbt.Game.new_tree(players=["Alice", "Bob"], title="Two-player card game")

g.append_move(g.root, g.players.chance, ["A", "B"])

g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 2)] * 2)


g.append_move(g.root.children[0], "Alice", ['A', 'B'])

g.append_move(g.root.children[1], "Bob", ['C', 'D'])

outcome_1 = g.add_outcome([1, 2], label="")
outcome_2 = g.add_outcome([2, 1], label="")
outcome_3 = g.add_outcome([0, 0], label="")
outcome_4 = g.add_outcome([3, 2], label="")

g.set_outcome(g.root.children[0].children[0], outcome_1)
g.set_outcome(g.root.children[0].children[1], outcome_2)
g.set_outcome(g.root.children[1].children[0], outcome_3)
g.set_outcome(g.root.children[1].children[1], outcome_4)

efg = g.write(format='native')

with open("new.efg", "w") as file:
    file.write(efg)