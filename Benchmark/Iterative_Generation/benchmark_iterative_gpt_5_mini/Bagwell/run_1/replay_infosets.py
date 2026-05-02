def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['S'].children['Signal C'], g.root.children['C'].children['Signal C'].infoset)
    g.set_infoset(g.root.children['S'].children['Signal S'], g.root.children['C'].children['Signal S'].infoset)
