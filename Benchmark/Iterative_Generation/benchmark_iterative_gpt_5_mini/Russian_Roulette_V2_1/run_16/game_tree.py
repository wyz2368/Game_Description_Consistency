import pygambit as gbt

# Create the game with Player 1 starting
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber alternate Russian roulette")

players = ["Player 1", "Player 2"]

def expand(node, remaining_chambers, current_idx):
    """
    Expand a decision node where the player with index current_idx
    (0 for Player 1, 1 for Player 2) chooses between "Quit" and "Pull".
    remaining_chambers is the number of chambers not yet pulled.
    """
    # Append the player's decision at this node
    g.append_move(node, players[current_idx], ["Quit", "Pull"])
    # Children: [0] = Quit, [1] = Pull
    quit_node = node.children[0]
    pull_node = node.children[1]

    # Outcome for quitting: quitting player gets 0, other gets 1
    pay_quit = [0, 0]
    pay_quit[current_idx] = 0
    pay_quit[1 - current_idx] = 1
    outcome_quit = g.add_outcome(pay_quit, label=f"{players[current_idx]} quits")
    g.set_outcome(quit_node, outcome_quit)

    # Handle the pull action: add a chance move with appropriate actions and probabilities
    if remaining_chambers == 1:
        # Certain firing: only one action with probability 1; do NOT include zero-prob actions
        g.append_move(pull_node, g.players.chance, ["Fires"])
        g.set_chance_probs(pull_node.infoset, [gbt.Rational(1, 1)])
        fires_node = pull_node.children[0]
        # Outcome for firing: shooter gets -1, other gets +1
        pay_fire = [0, 0]
        pay_fire[current_idx] = -1
        pay_fire[1 - current_idx] = 1
        outcome_fire = g.add_outcome(pay_fire, label=f"{players[current_idx]} fired (last chamber)")
        g.set_outcome(fires_node, outcome_fire)
    else:
        # Two possible chance outcomes: Fires with prob 1/m, Clicks with prob (m-1)/m
        m = remaining_chambers
        g.append_move(pull_node, g.players.chance, ["Fires", "Clicks"])
        g.set_chance_probs(pull_node.infoset, [gbt.Rational(1, m), gbt.Rational(m - 1, m)])
        fires_node = pull_node.children[0]
        clicks_node = pull_node.children[1]
        # Outcome for firing
        pay_fire = [0, 0]
        pay_fire[current_idx] = -1
        pay_fire[1 - current_idx] = 1
        outcome_fire = g.add_outcome(pay_fire, label=f"{players[current_idx]} fired (m={m})")
        g.set_outcome(fires_node, outcome_fire)
        # If click, continue with remaining_chambers-1 and the other player's turn
        expand(clicks_node, remaining_chambers - 1, 1 - current_idx)

# Build the game starting from the root: Player 1 moves first, 6 chambers initially
expand(g.root, remaining_chambers=6, current_idx=0)

# Save the EFG
g.to_efg("russian_roulette.efg")