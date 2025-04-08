from Tree import NodeType

"""
After Country B provokes Country A, a sequence of decisions unfolds. Country A must first decide to either escalate (E) the situation or ignore it (I) and end the game. If Country A ignores the provocation, both countries receive a small positive payoff.
If Country A escalates (E), Country B then faces the choice to either back down (B) with a small payoff loss while Country A gains a small payoff or to escalate further (E). 
If both Country A and Country B choose to escalate (E), this brings about a nuclear crisis. Country A then chooses first between retreating (R) and losing credibility or detonating (D). Country B, unaware of Country A’s decision, then decides to retreat (R) and lose credibility or detonate (D).
If one country detonates while the other retreats, the detonating country gains a large positive payoff, while the retreating country incurs a large negative payoff. 
However, if neither country retreats, retaliation follows the first nuclear strike, resulting in a catastrophic nuclear disaster, yielding a very large negative payoff for both countries. 
If both countries retreat, they each suffer a small negative payoff.
"""

paths_to_check = [
    ['Escalate', 'Back down'],
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
            raise ValueError(f"Path {path} does not lead to a terminal node.")
        outcomes[tuple(path)] = terminal_node.payoffs

    # Constraint 1: If Country A ignores → both get small positive payoff
    ignore = outcomes.get(('Ignore',))
    if not (ignore[0] > 0 and ignore[1] > 0):
        raise ValueError(f"Constraint failed: 'Ignore' path should yield small positive payoffs. Got {ignore}")

    # Constraint 2: Escalate → Back down → A gains small, B loses small
    back_down = outcomes.get(('Escalate', 'Back down'))
    if not (back_down[0] > 0 and back_down[1] < 0):
        raise ValueError(f"Constraint failed: 'Back down' should give A small gain, B small loss. Got {back_down}")

    # Constraint 3: Escalate → Escalate → Retreat + Retreat = both small negative
    rr = outcomes.get(('Escalate', 'Escalate', 'Retreat', 'Retreat'))
    if not (rr[0] < 0 and rr[1] < 0):
        raise ValueError(f"Constraint failed: 'Retreat + Retreat' should yield small negative for both. Got {rr}")

    # Constraint 4: A Retreats, B Detonates → B big gain, A big loss
    rd = outcomes.get(('Escalate', 'Escalate', 'Retreat', 'Detonate'))
    if not (rd[0] < 0 and rd[1] > 0):
        raise ValueError(f"Constraint failed: A retreats, B detonates → A big loss, B big gain. Got {rd}")

    # Constraint 5: A Detonates, B Retreats → A big gain, B big loss
    dr = outcomes.get(('Escalate', 'Escalate', 'Detonate', 'Retreat'))
    if not (dr[0] > 0 and dr[1] < 0):
        raise ValueError(f"Constraint failed: A detonates, B retreats → A big gain, B big loss. Got {dr}")

    # Constraint 6: Detonate + Detonate → both very large negative
    dd = outcomes.get(('Escalate', 'Escalate', 'Detonate', 'Detonate'))
    if not (dd[0] < 0 and dd[1] < 0):
        raise ValueError(f"Constraint failed: Detonate + Detonate → catastrophic loss for both. Got {dd}")
    
    # Check the payoff relationships
    small_payoff = [abs(ignore[0]), abs(ignore[1]), abs(back_down[0]), abs(back_down[1]), abs(rr[0]), abs(rr[1])]
    large_payoff = [abs(rd[0]), abs(rd[1]), abs(dr[0]), abs(dr[1])]
    very_large_payoff = [abs(dd[0]), abs(dd[1])]

    # small < large < very_large
    # Ensure all small < all large
    if not all(s < l for s in small_payoff for l in large_payoff):
        raise ValueError(f"Constraint failed: Not all small payoffs are less than large ones.\nSmall: {small_payoff}\nLarge: {large_payoff}")

    # Ensure all large < all very large
    if not all(l < v for l in large_payoff for v in very_large_payoff):
        raise ValueError(f"Constraint failed: Not all large payoffs are less than very large ones.\nLarge: {large_payoff}\nVery large: {very_large_payoff}")

    print("All crisis escalation payoff constraints are satisfied.")
    return True



def check_player_order(game):
    """
    Check that if Country A chooses "Escalate" and Country B also chooses "Escalate",
    then Country A moves first in the nuclear crisis.
    """
    players = game.players

    next_node = game.root.children["Escalate"]
    crisis_node = next_node.children["Escalate"]

    if crisis_node is None:
        raise ValueError("Crisis path not found: Could not trace Escalate → Escalate → Crisis.")

    if crisis_node.node_type != NodeType.PLAYER:
        raise ValueError("Expected a PLAYER node at the start of the crisis, found something else.")

    expected_player = players[0]  # Country A is expected to move first in the crisis
    actual_player = players[crisis_node.player-1] # Adjust for 0-based index

    if actual_player != expected_player:
        print(f"Expected {expected_player} to move first in the crisis, but got {actual_player}.")
        return False

    print(f"{expected_player} correctly moves first in the nuclear crisis.")

    return True
