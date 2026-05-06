import pygambit as gbt

# Create game with player order matching payoff vectors below
g = gbt.Game.new_tree(players=["Country A", "Country B"],
                      title="Threat and crisis game (Country A vs Country B)")

# Root: Country A decides whether to issue a threat or ignore
g.append_move(g.root, "Country A", ["Issue threat", "Ignore"])

# If Country A issues a threat, Country B chooses to Back down or Counter-threat
g.append_move(g.root.children[0], "Country B", ["Back down", "Counter-threat"])

# Define outcomes (payoffs must match players = ["Country A", "Country B"])
ignore = g.add_outcome([3, 4], label="ignore")                 # A:3, B:4
b_backs_down = g.add_outcome([4, 3], label="B backs down")     # A:4, B:3
a_wins = g.add_outcome([5, 2], label="A wins crisis")          # A:5, B:2
b_wins = g.add_outcome([1, 5], label="B wins crisis")          # A:1, B:5
mutual_retreat = g.add_outcome([2, 3], label="mutual retreat") # A:2, B:3
mutual_detonation = g.add_outcome([0, 0], label="mutual detonation") # A:0, B:0

# Set outcomes for branches that end immediately
g.set_outcome(g.root.children[1], ignore)                       # Country A chose "Ignore"
g.set_outcome(g.root.children[0].children[0], b_backs_down)    # Country B chose "Back down"

# Crisis subgame: represent simultaneous moves sequentially (A then B)
# At the Counter-threat node, Country A chooses Retreat or Detonate
g.append_move(g.root.children[0].children[1], "Country A", ["Retreat", "Detonate"])

# For each of Country A's crisis choices, Country B then chooses Retreat or Detonate
for node in g.root.children[0].children[1].children:
    g.append_move(node, "Country B", ["Retreat", "Detonate"])

# Set outcomes for the four crisis terminals:
# - A Retreat, B Retreat -> mutual retreat
g.set_outcome(g.root.children[0].children[1].children[0].children[0], mutual_retreat)
# - A Retreat, B Detonate -> B wins crisis
g.set_outcome(g.root.children[0].children[1].children[0].children[1], b_wins)
# - A Detonate, B Retreat -> A wins crisis
g.set_outcome(g.root.children[0].children[1].children[1].children[0], a_wins)
# - A Detonate, B Detonate -> mutual detonation
g.set_outcome(g.root.children[0].children[1].children[1].children[1], mutual_detonation)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['Issue threat'].children['Counter-threat'].children['Detonate'], g.root.children['Issue threat'].children['Counter-threat'].children['Retreat'].infoset)

# Save the EFG
g.to_efg("threat_crisis_game.efg")