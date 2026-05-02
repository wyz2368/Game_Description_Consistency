import pygambit as gbt

# Create the game with a single decision-maker "Player"
g = gbt.Game.new_tree(
    players=["Player"],
    title="Monty Hall single-player decision problem"
)

doors = [1, 2, 3]

# 1) Nature chooses car location uniformly
g.append_move(
    g.root,
    g.players.chance,
    [f"Car in door {d}" for d in doors]
)

g.set_chance_probs(
    g.root.infoset,
    [gbt.Rational(1, 3) for _ in doors]
)

# Keep references so we can set information sets later
first_pick_nodes = {}
final_decision_nodes = {}

# 2) For each car location, player picks a door
for car_idx, car_node in enumerate(g.root.children):
    car_door = doors[car_idx]

    g.append_move(
        car_node,
        "Player",
        [f"Pick door {d}" for d in doors]
    )

    first_pick_nodes[car_door] = car_node

    # 3) After the host opens a goat door, the player chooses Stick or Switch.
    # The host's opening is not modeled as a chance move.
    for pick_idx, pick_node in enumerate(car_node.children):
        pick_door = doors[pick_idx]

        g.append_move(
            pick_node,
            "Player",
            ["Stick", "Switch"]
        )

        final_decision_nodes[(car_door, pick_door)] = pick_node

        # 4) Terminal outcomes
        for final_idx, final_node in enumerate(pick_node.children):
            final_action = ["Stick", "Switch"][final_idx]

            if final_action == "Stick":
                payoff = 1 if pick_door == car_door else 0
            else:
                # Switching wins exactly when the initial pick was wrong.
                payoff = 1 if pick_door != car_door else 0

            outcome = g.add_outcome(
                [payoff],
                label=f"Payoff: {payoff}"
            )
            g.set_outcome(final_node, outcome)

# 5) Information sets

# The player does not observe nature's choice when making the first pick.
g.set_infoset(
    first_pick_nodes[2],
    first_pick_nodes[1].infoset
)
g.set_infoset(
    first_pick_nodes[3],
    first_pick_nodes[1].infoset
)

# At the final decision, the player knows their initial pick,
# but not the car location. Since the host's move is collapsed out,
# final decisions are grouped by the player's original pick.
for pick_door in doors:
    reference_infoset = final_decision_nodes[(1, pick_door)].infoset

    for car_door in doors:
        if car_door != 1:
            g.set_infoset(
                final_decision_nodes[(car_door, pick_door)],
                reference_infoset
            )

# Save the EFG after information sets are assigned
g.to_efg("monty_hall.efg")