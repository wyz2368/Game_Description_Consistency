import pygambit as gbt

# Create the game with the specified player order
g = gbt.Game.new_tree(players=["Country A", "Country B"],
                      title="Threat and crisis game (Country A vs Country B)")

# Root move: Country A chooses whether to Issue threat or Ignore
g.append_move(g.root, "Country A", ["Issue threat", "Ignore"])

# If Ignore (root.children[1]) -> terminal "ignore"
ignore_outcome = g.add_outcome([1, 1], label="ignore")  # A:1, B:1 (fits relative rankings)
g.set_outcome(g.root.children[1], ignore_outcome)

# If Issue threat (root.children[0]) -> Country B chooses Back down or Counter-threat
g.append_move(g.root.children[0], "Country B", ["Back down", "Counter-threat"])

# If Back down (root.children[0].children[0]) -> terminal "B backs down"
b_backs_down = g.add_outcome([2, -1], label="B backs down")  # A:2, B:-1 (B indifferent with mutual retreat)
g.set_outcome(g.root.children[0].children[0], b_backs_down)

# If Counter-threat (root.children[0].children[1]) -> crisis stage
crisis_node = g.root.children[0].children[1]

# Model the crisis stage sequentially (A then B) to avoid imperfect-information constructs
# Country A chooses Retreat or Detonate in the crisis
g.append_move(crisis_node, "Country A", ["Retreat", "Detonate"])

# For each of A's crisis choices, Country B chooses Retreat or Detonate
for a_crisis_child in crisis_node.children:
    g.append_move(a_crisis_child, "Country B", ["Retreat", "Detonate"])

# Define outcomes for the crisis terminal nodes:
# Path mapping:
# crisis_node.children[0] -> A chooses "Retreat"
#    .children[0] -> B chooses "Retreat"  => mutual retreat
#    .children[1] -> B chooses "Detonate" => B wins crisis
# crisis_node.children[1] -> A chooses "Detonate"
#    .children[0] -> B chooses "Retreat"  => A wins crisis
#    .children[1] -> B chooses "Detonate" => mutual detonation

mutual_retreat = g.add_outcome([0, -1], label="mutual retreat")  # A:0, B:-1 (B indifferent with B backs down)
b_wins_crisis = g.add_outcome([-10, 3], label="B wins crisis")   # A:-10, B:3
a_wins_crisis = g.add_outcome([3, -10], label="A wins crisis")   # A:3, B:-10
mutual_detonation = g.add_outcome([-100, -100], label="mutual detonation")  # specified worst outcome

# Assign outcomes to the correct nodes
# A Retreat -> B Retreat
g.set_outcome(crisis_node.children[0].children[0], mutual_retreat)
# A Retreat -> B Detonate
g.set_outcome(crisis_node.children[0].children[1], b_wins_crisis)
# A Detonate -> B Retreat
g.set_outcome(crisis_node.children[1].children[0], a_wins_crisis)
# A Detonate -> B Detonate
g.set_outcome(crisis_node.children[1].children[1], mutual_detonation)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['Issue threat'].children['Counter-threat'].children['Detonate'], g.root.children['Issue threat'].children['Counter-threat'].children['Retreat'].infoset)

# Save the EFG
g.to_efg("country_conflict.efg")