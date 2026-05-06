import pygambit as gbt

# Create the game with the correct player order
g = gbt.Game.new_tree(players=["Alice", "Bob"],
                      title="Take-away game from piles (2,2,1)")

# Pre-create consistent outcomes: winner gets +1, loser gets -1
alice_wins = g.add_outcome([1, -1], label="Alice wins")
bob_wins = g.add_outcome([-1, 1], label="Bob wins")

# Helper to expand the game tree recursively
def expand(node, state, current_player_index):
    # state is a tuple/list of three integers (pile1, pile2, pile3)
    if sum(state) == 0:
        # Terminal: the previous player (who moved last) is the winner
        winner = 1 - current_player_index
        if winner == 0:
            g.set_outcome(node, alice_wins)
        else:
            g.set_outcome(node, bob_wins)
        return

    # Build actions and corresponding next states in the same order
    actions = []
    next_states = []
    for pile_idx, pile_size in enumerate(state):
        if pile_size <= 0:
            continue
        for remove in range(1, pile_size + 1):
            actions.append(f"Remove {remove} from pile {pile_idx + 1}")
            new_state = list(state)
            new_state[pile_idx] -= remove
            next_states.append(tuple(new_state))

    # Determine current player's name as used in Game.new_tree
    player_name = ["Alice", "Bob"][current_player_index]

    # Append move for this single node (do not pass a list of nodes)
    g.append_move(node, player_name, actions)

    # children are created in the same order as actions; expand each child
    for idx, child in enumerate(node.children):
        expand(child, next_states[idx], 1 - current_player_index)

# Start expansion from the root with initial piles (2,2,1) and Alice to move
initial_state = (2, 2, 1)
expand(g.root, initial_state, current_player_index=0)

# Save the EFG
g.to_efg("take_away_2_2_1.efg")