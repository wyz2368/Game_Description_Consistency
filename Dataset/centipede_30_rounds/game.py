import pygambit as gbt

# Create the game with the specified player order
g = gbt.Game.new_tree(players=["Alice", "Bob"],
                      title="Take-or-Push piles game (4 and 1), 30 rounds / 60 moves")

# Total number of moves: 30 rounds * 2 moves per round = 60 moves
TOTAL_MOVES = 60

# Frontier of nodes to expand and mapping node -> number of pushes (k) so far.
frontier = [g.root]
k_map = {g.root: 0}

for move_index in range(TOTAL_MOVES):
    player = "Alice" if (move_index % 2 == 0) else "Bob"
    next_frontier = []
    next_k_map = {}
    for node in frontier:
        k = k_map[node]
        # Add the move for this single node (do not append multiple nodes at once)
        g.append_move(node, player, ["Take larger pile", "Push piles"])
        # Children correspond to actions in the same order
        take_child = node.children[0]
        push_child = node.children[1]

        # Compute payoffs depending on who takes and how many pushes have occurred (k)
        pow2k = 1 << k  # 2**k, using bitshift for exact integers
        if player == "Alice":
            # Alice takes the large pile, Bob gets small
            alice_payoff = 4 * pow2k
            bob_payoff = 1 * pow2k
            label = f"Alice takes at k={k}"
            outcome = g.add_outcome([alice_payoff, bob_payoff], label=label)
            g.set_outcome(take_child, outcome)
        else:
            # Bob takes the large pile, Alice gets small
            alice_payoff = 1 * pow2k
            bob_payoff = 4 * pow2k
            label = f"Bob takes at k={k}"
            outcome = g.add_outcome([alice_payoff, bob_payoff], label=label)
            g.set_outcome(take_child, outcome)

        # For the push action, update pushes count and continue
        next_frontier.append(push_child)
        next_k_map[push_child] = k + 1

    # Advance to next move
    frontier = next_frontier
    k_map = next_k_map

# After all moves, any remaining frontier nodes represent the path where all moves were pushes.
# Set the final no-take outcome: Alice gets the larger pile, Bob gets the smaller pile.
for node in frontier:
    k_final = k_map[node]
    pow2k = 1 << k_final
    alice_final = 4 * pow2k
    bob_final = 1 * pow2k
    outcome = g.add_outcome([alice_final, bob_final], label=f"No take by end (k={k_final})")
    g.set_outcome(node, outcome)

# Save the EFG
g.to_efg("take_or_push_piles_game.efg")