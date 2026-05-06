import pygambit as gbt


def same_reduced_strategies(candidate_path, ref_path):
    candidate_efg = gbt.read_efg(candidate_path)
    ref_efg = gbt.read_efg(ref_path)

    for cand_player, ref_player in zip(candidate_efg.players, ref_efg.players):
        if cand_player.is_chance:
            continue

        cand_strategies = sorted(s.label for s in cand_player.strategies)
        ref_strategies = sorted(s.label for s in ref_player.strategies)

        if cand_strategies != ref_strategies:
            return False

    return True