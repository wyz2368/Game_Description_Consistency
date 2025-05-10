from Tree import NodeType, EFGParser, compare_information_sets

"""
Consider a game with two players, Alice and Bob, where Alice makes the first move. 
At the start, Alice has two piles of coins in front of her: one pile with 4 coins and another with 1 coin. 
Each player has two options on their turn: they can either take the larger pile, giving the smaller pile to the other player, or they can push both piles to the other player. 
Whenever the piles are pushed across the table, the number of coins in each pile doubles. 
For instance, if Alice chooses to push on her first turn, the piles of 1 and 4 coins are handed over to Bob, increasing to 2 and 8 coins. 
Bob can then decide either to take the pile of 8 coins and leave 2 for Alice or to push the piles back to Alice, further doubling them to 4 and 16 coins. 
If neither player takes the coins by the end of the game, Alice will receive the pile with the higher value, and Bob will get the one with the lower value. 
The game has four moves in total: Alice moves (take or push), Bob moves (take or push, where the final push also doubles the piles before the game ends), Alice moves again, and finally, Bob moves. 
All actions are visible to both players.
"""

# Constraints:
# Explicit payoffs are correct

paths_to_check = [
    (['take'], [4, 1]),
    (['push', 'take'], [2, 8]),
    (['push', 'push', 'take'], [16, 4]),
    (['push', 'push', 'push', 'take'], [8, 32]),
    (['push', 'push', 'push', 'push'], [64, 16])
]

def check_first_player(game):
    players = game.players

    if 0 not in game.level_to_nodes:
        print("Level 2 not found in the game tree.")
        return False

    level_0_nodes = game.level_to_nodes[0]

    player_node = next((node for node in level_0_nodes if node.node_type == NodeType.PLAYER), None)
    
    if not player_node:
        print("No PLAYER node found at level 2. Cannot verify player order.")
        return False
    
    expected_player = players[0]  # Alice
    actual_player = players[player_node.player - 1]  # Adjust for 0-based index
    

    if actual_player != expected_player:
        print(f"Expected {expected_player} to move first, but got {actual_player}.")
        return False
    return True

def check_payoffs(game):
    """
    The game start with one pile with 4 coins and another with 1 coin so the payoff are explicitly defined.
    Then, we need to check all the payoffs in the game tree.
    """

    if not check_first_player(game):
        print("First player check failed.")
        return False
    
    def traverse_path(node, path):
        current = node
        for action in path:
            if action not in current.children:
                return None
            current = current.children[action]
        return current if current.node_type == NodeType.TERMINAL else None

    any_correct = False  # Start assuming none are correct

    for path, expected_payoff in paths_to_check:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            print(f"Path {path} does not lead to a terminal node.")
            return False
        elif terminal_node.payoffs != expected_payoff:
            print(f"Path {path} leads to payoff {terminal_node.payoffs}, expected {expected_payoff}.")
            return False
        
        any_correct = True

    if any_correct:
        print("All path leads to the correct expected payoff.")
        return True
    else:
        print("No path matched the expected payoffs.")
        return False

#========Test Functions Below===================================================================================

# after_switch_game_path ="Output/Perfect_Information_Games/Centipede/3.efg"

# parser_gen = EFGParser()

# gen_game = parser_gen.parse_file(after_switch_game_path)

# def test_payoffs():
#     print("Checking payoffs...")
#     check_payoffs(gen_game)
#     assert check_payoffs(gen_game) == True

def test_constraints(ref_game_path, output_game_path, original_game_path):

    parser_ref = EFGParser()
    parser_gen = EFGParser()
    parser_orig = EFGParser()

    ref_game = parser_ref.parse_file(ref_game_path)
    gen_game = parser_gen.parse_file(output_game_path)
    orig_game = parser_orig.parse_file(original_game_path)


    if not compare_information_sets(ref_game, gen_game):
        print("Information sets do not match between reference and generated game.")
        return False

    if not check_payoffs(gen_game):
        return False

    return True