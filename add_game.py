# import pygambit as gbt

# # Create a new extensive-form game
# g = gbt.Game.new_tree(players=["Player 1", "Player 2", "Player 3"],
#                       title="Three Driver Road Choice Game")

# # Player 1 moves first (A or B)
# g.append_move(g.root, "Player 1", ["A", "B"])

# for move in g.root.children:
#     g.append_move(move, "Player 2", ["A", "B"])
#     for move2 in move.children:
#         g.append_move(move2, "Player 3", ["A", "B"])

# g.set_infoset(g.root.children[0], g.root.children[1].infoset)
# g.set_infoset(g.root.children[0].children[1], g.root.children[0].children[0].infoset)
# g.set_infoset(g.root.children[1].children[0], g.root.children[0].children[0].infoset)
# g.set_infoset(g.root.children[1].children[1], g.root.children[0].children[0].infoset)

# cost_on_each_path = [[3, 0], [2, 2], [2, 2], [1, 4], [2, 2], [1, 4], [1, 4], [0, 6]]

# k = 2

# wight_p1 = k
# wight_p2 = 2*k
# wight_p3 = k

# def calculate_phi(cost):
#     phi = []
#     for element in cost:
#         value = 0
#         for road in element:
#             value += road*wight_p1
#             value += road*wight_p2
#             value += road*wight_p3
#         phi.append(value)
#     return phi

# phi = calculate_phi(cost_on_each_path)
# final_payoffs = []
# for _, potential in enumerate(phi):
#     payoff = []
#     payoff.append(-wight_p1*potential)
#     payoff.append(-wight_p2*potential)
#     payoff.append(-wight_p3*potential)
#     final_payoffs.append(payoff)

# # Set the payoffs for each outcome
# g.set_outcome(g.root.children[0].children[0].children[0], g.add_outcome(final_payoffs[0]))
# g.set_outcome(g.root.children[0].children[0].children[1], g.add_outcome(final_payoffs[1]))
# g.set_outcome(g.root.children[0].children[1].children[0], g.add_outcome(final_payoffs[2]))
# g.set_outcome(g.root.children[0].children[1].children[1], g.add_outcome(final_payoffs[3]))
# g.set_outcome(g.root.children[1].children[0].children[0], g.add_outcome(final_payoffs[4]))
# g.set_outcome(g.root.children[1].children[0].children[1], g.add_outcome(final_payoffs[5]))
# g.set_outcome(g.root.children[1].children[1].children[0], g.add_outcome(final_payoffs[6]))
# g.set_outcome(g.root.children[1].children[1].children[1], g.add_outcome(final_payoffs[7]))

# g.to_efg("three_driver_game.efg")

import pygambit as gbt

# Create a new extensive-form game
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="A Two-Player Game")

g.append_move(g.root, "Player 1", ["A", "B", "C"])

for move in g.root.children:
    g.append_move(move, "Player 2", ["A", "B", "C"])

g.set_infoset(g.root.children[0], g.root.children[1].infoset)
g.set_infoset(g.root.children[2], g.root.children[1].infoset)

x = 2
y = 2

g.set_outcome(g.root.children[0].children[0], g.add_outcome([x, x]))
g.set_outcome(g.root.children[0].children[1], g.add_outcome([-x, 0]))
g.set_outcome(g.root.children[0].children[2], g.add_outcome([-2*x, -2*y]))

g.set_outcome(g.root.children[1].children[0], g.add_outcome([0, -x]))
g.set_outcome(g.root.children[1].children[1], g.add_outcome([0, 0]))
g.set_outcome(g.root.children[1].children[2], g.add_outcome([0, -y]))

g.set_outcome(g.root.children[2].children[0], g.add_outcome([-2*y, -2*x]))
g.set_outcome(g.root.children[2].children[1], g.add_outcome([-y, 0]))
g.set_outcome(g.root.children[2].children[2], g.add_outcome([y, y]))

g.to_efg("two_player_game.efg")
