import pygambit as gbt

# Create the game
g = gbt.Game.new_tree(players=["Player One", "Player Two"],
                      title="Three-card poker (K,Q,J)")

# Cards and all ordered deals (no replacement)
cards = ["K", "Q", "J"]
deals = [(c1, c2) for c1 in cards for c2 in cards if c1 != c2]
deal_actions = [f"P1:{c1} P2:{c2}" for c1, c2 in deals]

# Chance move: dealing the two cards
g.append_move(g.root, g.players.chance, deal_actions)
# Set equal probabilities for the 6 deals
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, len(deal_actions)) for _ in deal_actions])

# Outcomes (reuse common payoff objects)
p1_wins_small = g.add_outcome([1, -1], label="P1 wins small")   # pot 2 or pot 3 => +1 / -1
p2_wins_small = g.add_outcome([-1, 1], label="P2 wins small")
p1_wins_big = g.add_outcome([2, -2], label="P1 wins big")      # pot 4 => +2 / -2
p2_wins_big = g.add_outcome([-2, 2], label="P2 wins big")

# Rank map for determining winner
ranks = {"K": 3, "Q": 2, "J": 1}

# Build the decision tree for each deal
for idx, deal_node in enumerate(g.root.children):
    p1_card, p2_card = deals[idx]

    # Player One: Check or Bet
    g.append_move(deal_node, "Player One", ["Check", "Bet"])

    # If Player One checks:
    check_node = deal_node.children[0]
    # Player Two: Check or Bet
    g.append_move(check_node, "Player Two", ["Check", "Bet"])

    # Player Two checks -> showdown for pot 2
    if ranks[p1_card] > ranks[p2_card]:
        g.set_outcome(check_node.children[0], p1_wins_small)
    else:
        g.set_outcome(check_node.children[0], p2_wins_small)

    # Player Two bets after P1 checked -> P1 can Fold or Call
    p2bet_node = check_node.children[1]
    g.append_move(p2bet_node, "Player One", ["Fold", "Call"])

    # If P1 folds -> P2 wins pot 3
    g.set_outcome(p2bet_node.children[0], p2_wins_small)

    # If P1 calls -> showdown for pot 4
    if ranks[p1_card] > ranks[p2_card]:
        g.set_outcome(p2bet_node.children[1], p1_wins_big)
    else:
        g.set_outcome(p2bet_node.children[1], p2_wins_big)

    # If Player One bets initially:
    bet_node = deal_node.children[1]
    # Player Two: Fold or Call
    g.append_move(bet_node, "Player Two", ["Fold", "Call"])

    # If P2 folds -> P1 wins pot 3
    g.set_outcome(bet_node.children[0], p1_wins_small)

    # If P2 calls -> showdown for pot 4
    if ranks[p1_card] > ranks[p2_card]:
        g.set_outcome(bet_node.children[1], p1_wins_big)
    else:
        g.set_outcome(bet_node.children[1], p2_wins_big)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['P1:K P2:J'], g.root.children['P1:K P2:Q'].infoset)
    g.set_infoset(g.root.children['P1:K P2:J'].children['Check'].children['Bet'], g.root.children['P1:K P2:Q'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['P1:Q P2:J'], g.root.children['P1:Q P2:K'].infoset)
    g.set_infoset(g.root.children['P1:Q P2:J'].children['Check'], g.root.children['P1:K P2:J'].children['Check'].infoset)
    g.set_infoset(g.root.children['P1:Q P2:J'].children['Check'].children['Bet'], g.root.children['P1:Q P2:K'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['P1:Q P2:J'].children['Bet'], g.root.children['P1:K P2:J'].children['Bet'].infoset)
    g.set_infoset(g.root.children['P1:J P2:K'].children['Check'], g.root.children['P1:Q P2:K'].children['Check'].infoset)
    g.set_infoset(g.root.children['P1:J P2:K'].children['Bet'], g.root.children['P1:Q P2:K'].children['Bet'].infoset)
    g.set_infoset(g.root.children['P1:J P2:Q'], g.root.children['P1:J P2:K'].infoset)
    g.set_infoset(g.root.children['P1:J P2:Q'].children['Check'], g.root.children['P1:K P2:Q'].children['Check'].infoset)
    g.set_infoset(g.root.children['P1:J P2:Q'].children['Check'].children['Bet'], g.root.children['P1:J P2:K'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['P1:J P2:Q'].children['Bet'], g.root.children['P1:K P2:Q'].children['Bet'].infoset)

replay_infosets(g)

# Save the EFG
g.to_efg("three_card_poker.efg")