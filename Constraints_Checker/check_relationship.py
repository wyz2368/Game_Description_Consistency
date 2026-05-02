import json
import operator
import pygambit as gbt


OPS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "=": operator.eq,
    "!=": operator.ne,
}


def steps(payoff_spec):
    return [
        payoff_spec[k]
        for k in sorted((x for x in payoff_spec if x.isdigit()), key=int)
    ]


def player_index(payoff_spec):
    return int(payoff_spec["Player order"]) - 1


def norm(s):
    return str(s).strip()


def find_terminal(root, payoff_spec):
    node = root

    for step in steps(payoff_spec):
        want_action = norm(step["action"])
        matches = [
            child for child in node.children
            if child.prior_action is not None
            and norm(child.prior_action.label) == want_action
        ]

        if not matches:
            raise ValueError(f"Action not found from current node: {want_action}")

        if len(matches) > 1:
            raise ValueError(f"Ambiguous action label from current node: {want_action}")

        node = matches[0]

    if not node.is_terminal:
        raise ValueError(
            f"Path ended before a terminal node: {[s['action'] for s in steps(payoff_spec)]}"
        )

    return node


def payoff(game, node, pidx):
    player = list(game.players)[pidx]
    outcome = node.outcome

    for key in (player, pidx, pidx + 1):
        try:
            return float(outcome[key])
        except Exception:
            pass

    raise ValueError(f"Could not read payoff for player {pidx + 1}")


def payoff_value(game, constraint, key):
    spec = constraint[key]
    node = find_terminal(game.root, spec)
    return payoff(game, node, player_index(spec))


def payoff_keys(constraint):
    return [
        k for k in constraint
        if k.startswith("P") and "Payoff" in k
    ]


def check_payoff_relation(efg_file, json_file):
    game = gbt.read_efg(efg_file)

    with open(json_file, "r", encoding="utf-8") as f:
        c = json.load(f)

    if int(c["Cst Type"]) != 3:
        raise ValueError("Only Cst Type 3 is supported")

    rel = c["Relationship"]

    if rel not in OPS:
        raise ValueError(f"Unsupported relationship: {rel}")

    keys = payoff_keys(c)

    if len(keys) == 1:
        left = payoff_value(game, c, keys[0])
        right = float(c["Threshold"])
        detail = f"{keys[0]} {rel} Threshold  ->  {left} {rel} {right}"

    elif len(keys) == 2:
        left = payoff_value(game, c, keys[0])
        right = payoff_value(game, c, keys[1])
        detail = f"{keys[0]} {rel} {keys[1]}  ->  {left} {rel} {right}"

    else:
        raise ValueError(f"Expected 1 or 2 payoff entries, found: {keys}")

    ok = OPS[rel](left, right)

    print("PASS" if ok else "FAIL")
    print(detail)

    return ok