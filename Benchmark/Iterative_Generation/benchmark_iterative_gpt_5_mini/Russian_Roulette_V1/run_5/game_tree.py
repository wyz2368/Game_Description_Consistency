import pygambit as gbt

# Create game with two players: Player 1 starts
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber revolver alternation (Russian roulette style)")

# Chance at the root: which chamber (0..5) contains the bullet
g.append_move(g.root, g.players.chance, [f"Chamber {i}" for i in range(6)])
# Set equal probabilities 1/6 for each chamber
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 6) for _ in range(6)])


def expand(node, loaded_chamber, current_chamber, current_player):
    """
    Recursively expand the decision node for the current player.
    - node: Node to append the move to.
    - loaded_chamber: fixed index (0..5) chosen by chance at root.
    - current_chamber: index (0..5) that will be checked if the player Pulls now.
    - current_player: 0 for Player 1, 1 for Player 2.
    """
    player_name = "Player 1" if current_player == 0 else "Player 2"
    other_player = 1 - current_player

    # Add the player's move: Pull or Quit
    g.append_move(node, player_name, ["Pull", "Quit"])

    # Child 0 corresponds to "Pull"
    pull_child = node.children[0]
    # Child 1 corresponds to "Quit"
    quit_child = node.children[1]

    # If the player quits: quitting player gets 0, other gets 1
    if current_player == 0:
        quit_payoff = [0, 1]
    else:
        quit_payoff = [1, 0]
    g.set_outcome(quit_child, g.add_outcome(quit_payoff, label=f"{player_name} quits"))

    # If the player pulls and the current chamber is the loaded one -> shooter dies
    if current_chamber == loaded_chamber:
        if current_player == 0:
            pull_payoff = [-1, 1]  # Player 1 dies
        else:
            pull_payoff = [1, -1]  # Player 2 dies
        g.set_outcome(pull_child, g.add_outcome(pull_payoff, label=f"{player_name} pulls and dies"))
    else:
        # Safe pull: no immediate payoff; pass to the other player with chamber advanced
        next_chamber = (current_chamber + 1) % 6
        # Recurse to expand the other player's decision node on this child
        expand(pull_child, loaded_chamber, next_chamber, other_player)


# For each possible loaded chamber chosen by chance, expand the subtree
for i in range(6):
    # Each chance branch corresponds to g.root.children[i]
    start_node = g.root.children[i]
    # Start with current chamber = 0 and Player 1 to move
    expand(start_node, loaded_chamber=i, current_chamber=0, current_player=0)

# Save the EFG
g.to_efg("revolver.efg")