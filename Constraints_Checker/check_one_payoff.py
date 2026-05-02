import json
import math
import pygambit as gbt


def same_payoff(a, b, tol=1e-9):
    return math.isclose(float(a), float(b), abs_tol=tol)


def is_chance_node(node):
    p = node.player

    if hasattr(p, "is_chance") and p.is_chance:
        return True

    if "ChancePlayer" in type(p).__name__:
        return True

    return False


def get_player_name(node):
    p = node.player

    if is_chance_node(node):
        return "Chance"

    if hasattr(p, "label"):
        return str(p.label)

    return str(p)


def get_action_name(action):
    if hasattr(action, "label"):
        return str(action.label)

    return str(action)


def find_child_by_action(node, action_name):
    action_name = str(action_name).strip()

    for child in node.children:
        child_action = get_action_name(child.prior_action).strip()

        if child_action == action_name:
            return child

    available = [get_action_name(child.prior_action) for child in node.children]
    print(f"Action {action_name!r} not found.")
    print(f"Available actions are: {available}")

    return None


def get_outcome_payoff(outcome, player_name):
    """
    Find payoff by exact player label from the .efg file.
    """
    try:
        return outcome[player_name]
    except Exception:
        raise KeyError(f"Player {player_name!r} not found in outcome")


def check_efg_json(efg_file, json_file):
    game = gbt.read_efg(efg_file)

    with open(json_file, "r") as f:
        cst = json.load(f)

    node = game.root

    for step_id in sorted(cst["Path"], key=lambda x: int(x)):
        step = cst["Path"][step_id]

        if node.is_terminal:
            print("Path error: reached terminal node too early")
            return False

        expected_type = step.get("type")
        expected_player = step.get("player")
        expected_action = step["action"]

        # Check node type first
        if expected_type == "Chance":
            if not is_chance_node(node):
                print(f"Type mismatch at step {step_id}: expected Chance, got Decision")
                return False

            # For chance nodes, ignore player name.
            # So Chance, Chance1, Chance2 are all accepted.
        else:
            if is_chance_node(node):
                print(f"Type mismatch at step {step_id}: expected Decision, got Chance")
                return False

            actual_player = get_player_name(node)

            if actual_player != expected_player:
                print(
                    f"Player mismatch at step {step_id}: "
                    f"expected {expected_player}, got {actual_player}"
                )
                return False

        next_node = find_child_by_action(node, expected_action)

        if next_node is None:
            print(
                f"Action mismatch at step {step_id}: "
                f"action {expected_action} not found"
            )
            return False

        node = next_node

    if not node.is_terminal:
        print("Path error: path does not end at a terminal node")
        return False

    outcome = node.outcome
    if outcome is None:
        print("Payoff error: terminal node has no outcome")
        return False

    for player_name, expected_payoff in cst["Payoffs"].items():
        if expected_payoff is None:
            continue

        try:
            actual_payoff = get_outcome_payoff(outcome, player_name)
        except KeyError as e:
            print(e)
            return False

        if not same_payoff(actual_payoff, expected_payoff):
            print(
                f"Payoff mismatch for {player_name}: "
                f"expected {expected_payoff}, got {actual_payoff}"
            )
            return False

    return True