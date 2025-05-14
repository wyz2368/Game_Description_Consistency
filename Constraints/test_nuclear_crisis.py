from Tree import NodeType, EFGParser, compare_information_sets

"""
After Country B provokes Country A, a sequence of decisions unfolds. Country A must first decide to either escalate (E) the situation or ignore it (I) and end the game. If Country A ignores the provocation, both countries receive a small positive payoff.
If Country A escalates (E), Country B then faces the choice to either back down (B) with a small payoff loss while Country A gains a small payoff or to escalate further (E). 
If both Country A and Country B choose to escalate (E), this brings about a nuclear crisis. Country A then chooses first between retreating (R) and losing credibility or detonating (D). Country B, unaware of Country A’s decision, then decides to retreat (R) and lose credibility or detonate (D).
If one country detonates while the other retreats, the detonating country gains a large positive payoff, while the retreating country incurs a large negative payoff. 
However, if neither country retreats, retaliation follows the first nuclear strike, resulting in a catastrophic nuclear disaster, yielding a very large negative payoff for both countries. 
If both countries retreat, they each suffer a small negative payoff.
"""

# Constraints:
# Payoffs (Only check the negative and positive are correct)
# Player order

paths_to_check = [
    ['Escalate', 'Back Down'],
    ['Escalate', 'Escalate', 'Retreat', 'Retreat'],
    ['Escalate', 'Escalate', 'Retreat', 'Detonate'],
    ['Escalate', 'Escalate', 'Detonate', 'Retreat'],
    ['Escalate', 'Escalate', 'Detonate', 'Detonate'],
    ['Ignore']
]

def check_payoffs(game):
    """
    We need to first check the negative and positive are correct.
    Then we need to check that the payoffs are in the right order (small, large, very large).
    """
    def traverse_path(node, path):
        current = node
        for action in path:
            if action not in current.children:
                return None
            current = current.children[action]
        return current if current.node_type == NodeType.TERMINAL else None

    outcomes = {}

    for path in paths_to_check:
        terminal_node = traverse_path(game.root, path)
        if terminal_node is None:
            print(f"Path {path} does not lead to a terminal node.")
            return False
        outcomes[tuple(path)] = terminal_node.payoffs

    # Constraint 1: If Country A ignores → both get small positive payoff
    ignore = outcomes.get(('Ignore',))
    if not (ignore[0] > 0 and ignore[1] > 0):
        print(f"Constraint failed: 'Ignore' path should yield small positive payoffs. Got {ignore}")
        return False

    # Constraint 2: Escalate → Back down → A gains small, B loses small
    back_down = outcomes.get(('Escalate', 'Back Down'))
    if not (back_down[0] > 0 and back_down[1] < 0):
        print(f"Constraint failed: 'Back down' should give A small gain, B small loss. Got {back_down}")
        return False

    # Constraint 3: Escalate → Escalate → Retreat + Retreat = both small negative
    rr = outcomes.get(('Escalate', 'Escalate', 'Retreat', 'Retreat'))
    if not (rr[0] < 0 and rr[1] < 0):
        print(f"Constraint failed: 'Retreat + Retreat' should yield small negative for both. Got {rr}")
        return False

    # Constraint 4: A Retreats, B Detonates → B big gain, A big loss
    rd = outcomes.get(('Escalate', 'Escalate', 'Retreat', 'Detonate'))
    if not (rd[0] < 0 and rd[1] > 0):
        print(f"Constraint failed: A retreats, B detonates → A big loss, B big gain. Got {rd}")
        return False

    # Constraint 5: A Detonates, B Retreats → A big gain, B big loss
    dr = outcomes.get(('Escalate', 'Escalate', 'Detonate', 'Retreat'))
    if not (dr[0] > 0 and dr[1] < 0):
        print(f"Constraint failed: A detonates, B retreats → A big gain, B big loss. Got {dr}")
        return False

    # Constraint 6: Detonate + Detonate → both very large negative
    dd = outcomes.get(('Escalate', 'Escalate', 'Detonate', 'Detonate'))
    if not (dd[0] < 0 and dd[1] < 0):
        print(f"Constraint failed: Detonate + Detonate → catastrophic loss for both. Got {dd}")
        return False


    print("All crisis escalation payoff constraints are satisfied.")
    return True



def check_player_order(game):
    """
    At level 2, ensure the PLAYER node (representing the first move in the nuclear crisis)
    is assigned to Country A.
    """
    players = game.players

    if 2 not in game.level_to_nodes:
        print("Level 2 not found in the game tree.")
        return False

    level_2_nodes = game.level_to_nodes[2]

    # Find the PLAYER node at level 2
    player_node = next((node for node in level_2_nodes if node.node_type == NodeType.PLAYER), None)
    
    if not player_node:
        print("No PLAYER node found at level 2. Cannot verify player order.")
        return False

    expected_player = players[0]  # Country A
    actual_player = players[player_node.player - 1]  # Adjust for 0-based index

    if actual_player != expected_player:
        print(f"Expected {expected_player} to move first in the crisis, but got {actual_player}.")
        return False

    print(f"{expected_player} correctly moves first in the nuclear crisis.")
    return True


#========Test Functions Below===================================================================================

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
    
    if not check_player_order(orig_game):
        return False
    
    return True