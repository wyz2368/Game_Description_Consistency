import pygambit as gbt

def build_russian_roulette_efg(n_chambers=6, filename=None):
    """
    Build a finite alternating Russian-roulette-style game with n_chambers
    and save it to an EFG file.

    - n_chambers: number of chambers in the cylinder with one bullet. Must be >= 1.
    - filename: if provided, saves the game to that file in EFG format.
    """
    if n_chambers < 1:
        raise ValueError("n_chambers must be >= 1")

    players = ["Player 1", "Player 2"]

    g = gbt.Game.new_tree(
        players=players,
        title=f"Alternating Russian Roulette (N={n_chambers})"
    )

    # Payoff encoding: L = -1, D = 0, W = +1
    quit_p1 = g.add_outcome([0, 1], label="P1 quits (P1=D, P2=W)")
    quit_p2 = g.add_outcome([1, 0], label="P2 quits (P2=D, P1=W)")

    fire_p1 = g.add_outcome([-1, 1], label="P1 shot (P1=L, P2=W)")
    fire_p2 = g.add_outcome([1, -1], label="P2 shot (P2=L, P1=W)")

    def build(node, acting_idx, pulls_survived):
        """
        Recursively build from 'node' with the player indexed by acting_idx to move,
        given pulls_survived previous pulls that survived.
        """
        player_name = players[acting_idx]

        # Acting player chooses Quit or Pull
        g.append_move(node, player_name, ["Quit", "Pull"])

        quit_child = node.children[0]
        pull_child = node.children[1]

        # Quit outcome
        if acting_idx == 0:
            g.set_outcome(quit_child, quit_p1)
        else:
            g.set_outcome(quit_child, quit_p2)

        remaining = n_chambers - pulls_survived

        # Final chamber: pulling means certain fire.
        # No need to add a chance node with probabilities 1 and 0.
        if remaining == 1:
            if acting_idx == 0:
                g.set_outcome(pull_child, fire_p1)
            else:
                g.set_outcome(pull_child, fire_p2)
            return

        # Otherwise, chance determines Fire or Survive
        g.append_move(pull_child, g.players.chance, ["Fire", "Survive"])

        prob_fire = gbt.Rational(1, remaining)
        prob_survive = gbt.Rational(remaining - 1, remaining)

        g.set_chance_probs(pull_child.infoset, [prob_fire, prob_survive])

        fire_child = pull_child.children[0]
        survive_child = pull_child.children[1]

        # Fire outcome
        if acting_idx == 0:
            g.set_outcome(fire_child, fire_p1)
        else:
            g.set_outcome(fire_child, fire_p2)

        # Survive: continue with the other player
        next_acting_idx = 1 - acting_idx
        build(survive_child, next_acting_idx, pulls_survived + 1)

    build(g.root, acting_idx=0, pulls_survived=0)

    outname = filename or f"russian_roulette_n{n_chambers}.efg"
    g.to_efg(outname)

    return g


if __name__ == "__main__":
    game = build_russian_roulette_efg(
        n_chambers=6,
        filename="russian_roulette_n6.efg"
    )
    print("Saved EFG to russian_roulette_n6.efg")