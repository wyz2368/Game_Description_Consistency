import pygambit


def node_path(node):
    path = []
    while node.parent is not None:
        path.append(str(node.prior_action.label))
        node = node.parent
    return tuple(reversed(path))


def node_payoff(node, game):
    if node.outcome is None:
        return None
    return tuple(node.outcome[player] for player in game.players)


def terminal_payoffs(game):
    infos = []
    for node in game.nodes:
        if node.is_terminal:
            infos.append((node_path(node), node_payoff(node, game)))
    return infos


def check_payoffs(reference_efg, input_efg):
    reference_game = pygambit.read_efg(reference_efg)
    input_game = pygambit.read_efg(input_efg)

    reference_payoffs = dict(terminal_payoffs(reference_game))
    # print(reference_payoffs)
    input_payoffs = dict(terminal_payoffs(input_game))
    # print(input_payoffs)

    if reference_payoffs.keys() != input_payoffs.keys():
        return False

    for path, reference_payoff in reference_payoffs.items():
        if input_payoffs[path] != reference_payoff:
            return False

    return True
