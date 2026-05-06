import pygambit as gbt

def build_russian_roulette_efg(n_chambers=6, filename=None):
    """
    Build a finite alternating Russian-roulette-style game with n_chambers and save it to an EFG file.
    - n_chambers: number of chambers in the cylinder (one bullet). Must be >= 1.
    - filename: if provided, saves the game to that file (EFG format).
    """
    if n_chambers < 1:
        raise ValueError("n_chambers must be >= 1")

    players = ["Player 1", "Player 2"]
    g = gbt.Game.new_tree(players=players,
                          title=f"Alternating Russian Roulette (N={n_chambers})")

    # Payoff encoding: L = -1, D = 0, W = +1
    # Pre-add outcomes that depend on which player is acting:
    # Quit outcomes
    quit_p1 = g.add_outcome([0, 1], label="P1 quits (P1=D, P2=W)")
    quit_p2 = g.add_outcome([1, 0], label="P2 quits (P2=D, P1=W)")
    # Fire outcomes (acting player shoots self)
    fire_p1 = g.add_outcome([-1, 1], label="P1 shot (P1=L, P2=W)")
    fire_p2 = g.add_outcome([1, -1], label="P2 shot (P2=L, P1=W)")
    # Fallback neutral outcome for impossible-zero-prob branches
    neutral = g.add_outcome([0, 0], label="Neutral (zero-probability branch)")

    def build(node, acting_idx, pulls_survived):
        """
        Recursively build from 'node' with the player indexed by acting_idx to move,
        given pulls_survived previous pulls that survived.
        """
        player_name = players[acting_idx]
        # Add the decision move for the acting player with two actions: "Quit" and "Pull"
        g.append_move(node, player_name, ["Quit", "Pull"])

        # Node.children[0] corresponds to "Quit"
        if acting_idx == 0:
            g.set_outcome(node.children[0], quit_p1)
        else:
            g.set_outcome(node.children[0], quit_p2)

        # Node.children[1] corresponds to "Pull": chance acts after pull
        pull_node = node.children[1]
        # Add chance move "Fire" / "Survive" on the pull_node
        g.append_move(pull_node, g.players.chance, ["Fire", "Survive"])

        remaining = n_chambers - pulls_survived
        # Probability of fire = 1 / remaining, survive = (remaining - 1) / remaining
        # Use Rational; if remaining == 1 then survive probability numerator will be 0
        prob_fire = gbt.Rational(1, remaining)
        prob_survive = gbt.Rational(max(0, remaining - 1), remaining)
        g.set_chance_probs(pull_node.infoset, [prob_fire, prob_survive])

        # Chance child 0 = Fire -> acting player dies (L), other wins (W)
        if acting_idx == 0:
            g.set_outcome(pull_node.children[0], fire_p1)
        else:
            g.set_outcome(pull_node.children[0], fire_p2)

        # Chance child 1 = Survive -> if further pulls possible, continue with other player
        survive_child = pull_node.children[1]
        if pulls_survived + 1 < n_chambers:
            # Continue the game with the other player
            next_acting_idx = 1 - acting_idx
            build(survive_child, next_acting_idx, pulls_survived + 1)
        else:
            # No further pulls possible (this survive branch has probability 0 when remaining==1).
            # Set a neutral terminal outcome so the tree is well-formed. It is zero-probability and does not affect expected values.
            g.set_outcome(survive_child, neutral)

    # Start recursion from the root with Player 1 to move and 0 pulls survived
    build(g.root, acting_idx=0, pulls_survived=0)

    # Save EFG if filename provided else pick a default name
    outname = filename or f"russian_roulette_n{n_chambers}.efg"
    g.to_efg(outname)
    return g

# Example usage: build and save a 6-chamber game
if __name__ == "__main__":
    game = build_russian_roulette_efg(n_chambers=6, filename="russian_roulette_n6.efg")
    print("Saved EFG to russian_roulette_n6.efg")