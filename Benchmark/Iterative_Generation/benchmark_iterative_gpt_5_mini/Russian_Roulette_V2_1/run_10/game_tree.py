import pygambit as gbt

def build_revolver_game(filename="revolver_game.efg", chambers=6):
    # Create the game with the two players
    g = gbt.Game.new_tree(players=["Player 1", "Player 2"],
                         title=f"Sequential revolver game ({chambers}-chamber)")

    def expand(node, player_index, n_remaining):
        """
        Recursively expand the node where player_index (0 or 1) chooses between Quit and Pull,
        with n_remaining chambers left (including the current chamber).
        """
        # Add the decision move for the current player at this node
        g.append_move(node, g.players[player_index], ["Quit", "Pull"])

        # Child 0: Quit -> terminal: quitter gets 0, other gets 1
        quit_child = node.children[0]
        if player_index == 0:
            # Player 1 quits
            outcome_quit = g.add_outcome([0, 1], label="Quit by P1")
        else:
            # Player 2 quits
            outcome_quit = g.add_outcome([1, 0], label="Quit by P2")
        g.set_outcome(quit_child, outcome_quit)

        # Child 1: Pull -> chance node
        pull_child = node.children[1]

        # Determine chance actions and probabilities
        if n_remaining > 1:
            chance_actions = ["Loaded", "Empty"]
            probs = [gbt.Rational(1, n_remaining), gbt.Rational(n_remaining - 1, n_remaining)]
        else:
            # n_remaining == 1: must be loaded
            chance_actions = ["Loaded"]
            probs = [gbt.Rational(1, 1)]

        # Append chance move at the pull child and set probabilities on its infoset
        g.append_move(pull_child, g.players.chance, chance_actions)
        g.set_chance_probs(pull_child.infoset, probs)

        # Handle chance outcomes
        # "Loaded" branch: shooter is killed -> shooter -1, other +1
        loaded_child = pull_child.children[0]
        if player_index == 0:
            outcome_loaded = g.add_outcome([-1, 1], label="P1 shot")
        else:
            outcome_loaded = g.add_outcome([1, -1], label="P2 shot")
        g.set_outcome(loaded_child, outcome_loaded)

        # "Empty" branch: if present, play continues with other player and one fewer chamber
        if len(chance_actions) == 2:
            empty_child = pull_child.children[1]
            # Recurse: other player's decision node, n_remaining - 1
            expand(empty_child, 1 - player_index, n_remaining - 1)

    # Start recursion from the root with Player 1 and full chambers
    expand(g.root, player_index=0, n_remaining=chambers)

    # Save EFG
    g.to_efg(filename)
    return g

if __name__ == "__main__":
    # Build and save the game with 6 chambers
    build_revolver_game("revolver_game.efg", chambers=6)