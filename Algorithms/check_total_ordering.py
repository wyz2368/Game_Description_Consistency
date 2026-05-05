import pygambit as gbt


def read_game(path):
    return gbt.read_efg(path)


def terminal_path(node):
    path = []
    while node.parent is not None:
        path.append(str(node.prior_action.label))
        node = node.parent
    return tuple(reversed(path))


def terminal_payoffs(game):
    players = list(game.players)
    data = {}

    for node in game.nodes:
        if not node.is_terminal:
            continue

        path = terminal_path(node)

        if node.outcome is None:
            payoffs = tuple(0 for _ in players)
        else:
            payoffs = tuple(node.outcome[p] for p in players)

        data[path] = payoffs

    return data


def sign_relation(a, b):
    if a < b:
        return "<"
    if a > b:
        return ">"
    return "="


def check_total_order_matching(reference_efg, candidate_efg):
    ref = terminal_payoffs(read_game(reference_efg))
    cand = terminal_payoffs(read_game(candidate_efg))

    if set(ref) != set(cand):
        return False

    n_players = len(next(iter(ref.values())))
    paths = list(ref.keys())

    for player in range(n_players):
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                x = paths[i]
                y = paths[j]

                ref_rel = sign_relation(ref[x][player], ref[y][player])
                cand_rel = sign_relation(cand[x][player], cand[y][player])

                if ref_rel != cand_rel:
                    return False

    return True