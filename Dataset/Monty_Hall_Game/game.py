import pygambit as gbt

# Create the game with Player first, then Host (so payoffs are [Player, Host])
g = gbt.Game.new_tree(players=["Player", "Host"],
                      title="Adversarial Monty Hall game (Host chooses hiding place)")

# Host hides the car behind one of three doors
g.append_move(g.root, "Host", ["Hide behind door 1", "Hide behind door 2", "Hide behind door 3"])

# Pre-create outcome objects for reuse: player win (+1) and player lose (-1)
player_win = g.add_outcome([1, -1], label="Player wins")
player_lose = g.add_outcome([-1, 1], label="Player loses")

# For each host hiding choice (children of root)
for hide_index, hide_node in enumerate(g.root.children, start=1):
    # Player chooses a door (note: we create separate choice nodes under each hide_node;
    # we do NOT set any infosets)
    for i in range(1):  # single call per hide_node to append the three actions on that node
        g.append_move(hide_node, "Player", [f"Choose door {d}" for d in (1, 2, 3)])
    # For each possible player choice under this hide_node
    for choose_index, player_choice_node in enumerate(hide_node.children, start=1):
        chosen = choose_index        # door chosen by Player (1..3)
        car = hide_index             # door hiding the car (1..3)
        # Determine host's available actions based on whether player's chosen door has the car
        if chosen == car:
            # Player picked the car: both other doors contain goats
            other_doors = [d for d in (1, 2, 3) if d != chosen]
            host_actions = ["Keep closed",
                            f"Open door {other_doors[0]}",
                            f"Open door {other_doors[1]}"]
        else:
            # Player picked a goat: among the two unchosen doors, one is car and one is goat.
            # Host can only open the unchosen goat door.
            goat_door = [d for d in (1, 2, 3) if d != chosen and d != car][0]
            host_actions = ["Keep closed", f"Open door {goat_door}"]

        # Append the Host's decision at this node (one node at a time)
        g.append_move(player_choice_node, "Host", host_actions)

        # Process each Host action child
        for h_action_index, host_action_node in enumerate(player_choice_node.children):
            action_label = host_actions[h_action_index]
            if action_label == "Keep closed":
                # Terminal: open player's original door
                if chosen == car:
                    g.set_outcome(host_action_node, player_win)
                else:
                    g.set_outcome(host_action_node, player_lose)
            else:
                # Host opened a goat door; determine which door was opened and which remains unopened
                # Parse opened door number from action_label "Open door X"
                opened_str = action_label.split()[-1]
                opened_door = int(opened_str)
                remaining_unopened = [d for d in (1, 2, 3) if d != chosen and d != opened_door][0]

                # Player chooses to Stick or Switch after observing opened door
                g.append_move(host_action_node, "Player", ["Stick", "Switch"])

                # Stick: player's original door is revealed
                if chosen == car:
                    g.set_outcome(host_action_node.children[0], player_win)
                else:
                    g.set_outcome(host_action_node.children[0], player_lose)

                # Switch: player takes the remaining unopened door
                if remaining_unopened == car:
                    g.set_outcome(host_action_node.children[1], player_win)
                else:
                    g.set_outcome(host_action_node.children[1], player_lose)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['Hide behind door 2'], g.root.children['Hide behind door 1'].infoset)
    g.set_infoset(g.root.children['Hide behind door 2'].children['Choose door 1'].children['Open door 3'], g.root.children['Hide behind door 1'].children['Choose door 1'].children['Open door 3'].infoset)
    g.set_infoset(g.root.children['Hide behind door 2'].children['Choose door 2'].children['Open door 3'], g.root.children['Hide behind door 1'].children['Choose door 2'].children['Open door 3'].infoset)
    g.set_infoset(g.root.children['Hide behind door 3'], g.root.children['Hide behind door 1'].infoset)
    g.set_infoset(g.root.children['Hide behind door 3'].children['Choose door 1'].children['Open door 2'], g.root.children['Hide behind door 1'].children['Choose door 1'].children['Open door 2'].infoset)
    g.set_infoset(g.root.children['Hide behind door 3'].children['Choose door 2'].children['Open door 1'], g.root.children['Hide behind door 2'].children['Choose door 2'].children['Open door 1'].infoset)
    g.set_infoset(g.root.children['Hide behind door 3'].children['Choose door 3'].children['Open door 1'], g.root.children['Hide behind door 2'].children['Choose door 3'].children['Open door 1'].infoset)
    g.set_infoset(g.root.children['Hide behind door 3'].children['Choose door 3'].children['Open door 2'], g.root.children['Hide behind door 1'].children['Choose door 3'].children['Open door 2'].infoset)

# Save the EFG to file
g.to_efg("adversarial_monty_hall.efg")