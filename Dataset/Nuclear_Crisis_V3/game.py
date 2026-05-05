import pygambit as gbt

# Create game with the specified player order
g = gbt.Game.new_tree(players=["Country A", "Country B"],
                      title="Threat-counterthreat-crisis game")

# Root: Country A decides whether to issue a threat or ignore
g.append_move(g.root, "Country A", ["Issue threat", "Ignore"])

# If A ignores -> terminal "ignore"
ignore_outcome = g.add_outcome([3, 5], label="ignore")
g.set_outcome(g.root.children[1], ignore_outcome)

# If A issues a threat -> Country B decides to back down or counter-threat
g.append_move(g.root.children[0], "Country B", ["Back down", "Counter-threat"])

# If B backs down -> terminal "B backs down"
b_backs_down_outcome = g.add_outcome([5, 2], label="B backs down")
g.set_outcome(g.root.children[0].children[0], b_backs_down_outcome)

# If B counter-threats -> crisis subgame (implemented as sequential moves)
counter_node = g.root.children[0].children[1]

# Country A's crisis move: Retreat or Detonate
g.append_move(counter_node, "Country A", ["Retreat", "Detonate"])

# For each A crisis action, Country B chooses Retreat or Detonate
for a_crisis_node in counter_node.children:
    g.append_move(a_crisis_node, "Country B", ["Retreat", "Detonate"])

# Define crisis outcomes and attach them in the order consistent with the tree:
# counter_node.children[0] corresponds to A chooses "Retreat"
#   -> children[0].children[0]: B "Retreat"  => mutual retreat
#   -> children[0].children[1]: B "Detonate" => B wins crisis
# counter_node.children[1] corresponds to A chooses "Detonate"
#   -> children[1].children[0]: B "Retreat"  => A wins crisis
#   -> children[1].children[1]: B "Detonate" => mutual detonation

mutual_retreat_outcome = g.add_outcome([1, 2], label="mutual retreat")
b_wins_crisis_outcome = g.add_outcome([-5, 10], label="B wins crisis")
a_wins_crisis_outcome = g.add_outcome([10, -10], label="A wins crisis")
mutual_detonation_outcome = g.add_outcome([-100, -100], label="mutual detonation")

# Attach outcomes
g.set_outcome(counter_node.children[0].children[0], mutual_retreat_outcome)
g.set_outcome(counter_node.children[0].children[1], b_wins_crisis_outcome)
g.set_outcome(counter_node.children[1].children[0], a_wins_crisis_outcome)
g.set_outcome(counter_node.children[1].children[1], mutual_detonation_outcome)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['Issue threat'].children['Counter-threat'].children['Detonate'], g.root.children['Issue threat'].children['Counter-threat'].children['Retreat'].infoset)


# Save the EFG
g.to_efg("country_conflict.efg")