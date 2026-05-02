import pygambit as gbt

# Create the game
g = gbt.Game.new_tree(players=["Player One", "Player Two"],
                      title="Three-card sequential bet game (K>Q>J)")

# Helper: card order and ranks
cards = ["K", "Q", "J"]
rank = {"K": 3, "Q": 2, "J": 1}

# 1) Root chance: deal Player One a card uniformly from {K,Q,J}
g.append_move(g.root, g.players.chance, cards)
# Set equal probabilities 1/3 each
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 3), gbt.Rational(1, 3), gbt.Rational(1, 3)])

# Helper to produce outcome labels and add outcomes (caches duplicates by payoff tuple)
_outcome_cache = {}
def outcome_for(payoffs, label=None):
    key = tuple(payoffs)
    if key not in _outcome_cache:
        lbl = label if label is not None else f"payoff_{payoffs[0]}_{payoffs[1]}"
        _outcome_cache[key] = g.add_outcome(payoffs, label=lbl)
    return _outcome_cache[key]

# For each possible Player One card
for i_p1, p1_card in enumerate(cards):
    p1_card_node = g.root.children[i_p1]  # node after dealing P1's card

    # 2) Second-stage chance: deal Player Two one of the remaining two cards
    remaining = [c for c in cards if c != p1_card]
    g.append_move(p1_card_node, g.players.chance, remaining)
    # Set equal probs 1/2, 1/2 for these two actions
    g.set_chance_probs(p1_card_node.infoset, [gbt.Rational(1, 2), gbt.Rational(1, 2)])

    # For each possible Player Two card given this P1 card
    for j_p2, p2_card in enumerate(remaining):
        p2_card_node = p1_card_node.children[j_p2]  # node after dealing P2's card

        # 3) Player One decision: Check or Bet
        g.append_move(p2_card_node, "Player One", ["Check", "Bet"])

        # Child for "Check"
        p1_check_node = p2_card_node.children[0]
        # Player Two decision after P1 checks: Check or Bet
        g.append_move(p1_check_node, "Player Two", ["Check", "Bet"])

        # If Player Two "Check" -> showdown for pot of 2 (winner +1, loser -1)
        p2_check_node = p1_check_node.children[0]
        if rank[p1_card] > rank[p2_card]:
            payoff = [1, -1]
            label = f"Showdown pot=2: P1({p1_card}) beats P2({p2_card})"
        else:
            payoff = [-1, 1]
            label = f"Showdown pot=2: P2({p2_card}) beats P1({p1_card})"
        g.set_outcome(p2_check_node, outcome_for(payoff, label))

        # If Player Two "Bet" after P1 checked -> P1 chooses Fold or Call
        p2_bet_node = p1_check_node.children[1]
        g.append_move(p2_bet_node, "Player One", ["Fold", "Call"])

        # P1 folds -> Player Two takes pot of 3 (Player Two +1, Player One -1)
        p1_folds_node = p2_bet_node.children[0]
        g.set_outcome(p1_folds_node, outcome_for([-1, 1], "P1 folds after P2 bet: P2 takes pot=3"))

        # P1 calls -> showdown for pot of 4 (winner +2, loser -2)
        p1_calls_node = p2_bet_node.children[1]
        if rank[p1_card] > rank[p2_card]:
            payoff = [2, -2]
            label = f"Showdown pot=4: P1({p1_card}) beats P2({p2_card})"
        else:
            payoff = [-2, 2]
            label = f"Showdown pot=4: P2({p2_card}) beats P1({p1_card})"
        g.set_outcome(p1_calls_node, outcome_for(payoff, label))

        # Child for "Bet" (P1 bets immediately)
        p1_bet_node = p2_card_node.children[1]
        # Player Two chooses Fold or Call
        g.append_move(p1_bet_node, "Player Two", ["Fold", "Call"])

        # P2 folds -> Player One takes pot of 3 (P1 +1, P2 -1)
        p2_folds_node = p1_bet_node.children[0]
        g.set_outcome(p2_folds_node, outcome_for([1, -1], "P2 folds to P1 bet: P1 takes pot=3"))

        # P2 calls -> showdown for pot of 4 (winner +2, loser -2)
        p2_calls_node = p1_bet_node.children[1]
        if rank[p1_card] > rank[p2_card]:
            payoff = [2, -2]
            label = f"Showdown pot=4: P1({p1_card}) beats P2({p2_card})"
        else:
            payoff = [-2, 2]
            label = f"Showdown pot=4: P2({p2_card}) beats P1({p1_card})"
        g.set_outcome(p2_calls_node, outcome_for(payoff, label))

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['K'].children['J'], g.root.children['K'].children['Q'].infoset)
    g.set_infoset(g.root.children['K'].children['J'].children['Check'].children['Bet'], g.root.children['K'].children['Q'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['Q'].children['J'], g.root.children['Q'].children['K'].infoset)
    g.set_infoset(g.root.children['Q'].children['J'].children['Check'], g.root.children['K'].children['J'].children['Check'].infoset)
    g.set_infoset(g.root.children['Q'].children['J'].children['Check'].children['Bet'], g.root.children['Q'].children['K'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['Q'].children['J'].children['Bet'], g.root.children['K'].children['J'].children['Bet'].infoset)
    g.set_infoset(g.root.children['J'].children['K'].children['Check'], g.root.children['Q'].children['K'].children['Check'].infoset)
    g.set_infoset(g.root.children['J'].children['K'].children['Bet'], g.root.children['Q'].children['K'].children['Bet'].infoset)
    g.set_infoset(g.root.children['J'].children['Q'], g.root.children['J'].children['K'].infoset)
    g.set_infoset(g.root.children['J'].children['Q'].children['Check'], g.root.children['K'].children['Q'].children['Check'].infoset)
    g.set_infoset(g.root.children['J'].children['Q'].children['Check'].children['Bet'], g.root.children['J'].children['K'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['J'].children['Q'].children['Bet'], g.root.children['K'].children['Q'].children['Bet'].infoset)

replay_infosets(g)

# Save EFG
g.to_efg("three_card_game.efg")