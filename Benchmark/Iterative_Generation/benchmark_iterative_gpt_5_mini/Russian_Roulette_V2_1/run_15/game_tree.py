import pygambit as gbt

# Create new tree game with Player 1 acting first
g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                      title="Six-chamber Russian roulette")

def build(node, p_idx, remaining):
    """
    node: current tree node where player p_idx acts
    p_idx: 0 for Player 1, 1 for Player 2
    remaining: number of chambers not yet pulled (1..6)
    """
    player = g.players[p_idx]
    other_idx = 1 - p_idx

    # Current player chooses to Quit or Pull
    g.append_move(node, player, ["Quit", "Pull"])
    quit_child = node.children[0]   # "Quit" branch
    pull_child = node.children[1]   # "Pull" branch

    # Quit outcome: quitter gets 0, other gets +1
    quit_payoffs = [0, 0]
    quit_payoffs[p_idx] = 0
    quit_payoffs[other_idx] = 1
    g.set_outcome(quit_child, g.add_outcome(quit_payoffs, label=f"Quit by {player}"))

    # Pull: a chance node decides whether the gun fires.
    # If remaining == 1, only "Fires" with probability 1 (omit zero-probability branch).
    if remaining == 1:
        g.append_move(pull_child, g.players.chance, ["Fires"])
        # probability 1 for "Fires"
        g.set_chance_probs(pull_child.infoset, [gbt.Rational(1, 1)])
        fire_node = pull_child.children[0]
        # Shooter dies: shooter -1, other +1
        fire_payoffs = [0, 0]
        fire_payoffs[p_idx] = -1
        fire_payoffs[other_idx] = 1
        g.set_outcome(fire_node, g.add_outcome(fire_payoffs, label=f"Death of {player}"))
    else:
        # Both "Fires" and "Does not fire" have positive probability
        g.append_move(pull_child, g.players.chance, ["Fires", "Does not fire"])
        g.set_chance_probs(pull_child.infoset,
                           [gbt.Rational(1, remaining), gbt.Rational(remaining - 1, remaining)])
        fire_node = pull_child.children[0]
        click_node = pull_child.children[1]

        # Fire outcome: shooter dies
        fire_payoffs = [0, 0]
        fire_payoffs[p_idx] = -1
        fire_payoffs[other_idx] = 1
        g.set_outcome(fire_node, g.add_outcome(fire_payoffs, label=f"Death of {player}"))

        # Click (does not fire): continue with other player and remaining-1 chambers
        build(click_node, other_idx, remaining - 1)

# Build the game starting with Player 1 and 6 chambers
build(g.root, p_idx=0, remaining=6)

# Save to EFG file
g.to_efg("russian_roulette.efg")