import pygambit as gbt

# Create game
g = gbt.Game.new_tree(players=["Player One", "Player Two"],
                      title="Three-card (K/Q/J) sequential betting game")

# Card labels and ranking
cards = ["King", "Queen", "Jack"]
rank = {"King": 3, "Queen": 2, "Jack": 1}

# Initial chance: deal to Player One
g.append_move(g.root, g.players.chance, cards)
# Set equal probabilities 1/3 each
g.set_chance_probs(g.root.infoset, [gbt.Rational(1, 3),
                                    gbt.Rational(1, 3),
                                    gbt.Rational(1, 3)])

# Outcomes (payoff vectors aligned with players=["Player One","Player Two"])
p1_win_small = g.add_outcome([1, -1], label="P1 wins small (pot 2 or fold to bettor)")
p1_win_big   = g.add_outcome([2, -2], label="P1 wins big (pot 4)")
p2_win_small = g.add_outcome([-1, 1], label="P2 wins small (pot 2 or fold to bettor)")
p2_win_big   = g.add_outcome([-2, 2], label="P2 wins big (pot 4)")

# For each card dealt to Player One
for p1_card, p1_card_node in zip(cards, g.root.children):
    # Player One chooses Check or Bet
    g.append_move(p1_card_node, "Player One", ["Check", "Bet"])

    # For each Player One action node (Check then Bet)
    for p1_action_idx, p1_action_node in enumerate(p1_card_node.children):
        p1_action = ["Check", "Bet"][p1_action_idx]

        # Determine remaining cards to deal to Player Two
        remaining = [c for c in cards if c != p1_card]

        # Chance deals one of the remaining cards to Player Two
        g.append_move(p1_action_node, g.players.chance, remaining)
        # Set equal probabilities 1/2 each for this chance node
        g.set_chance_probs(p1_action_node.infoset, [gbt.Rational(1, 2),
                                                    gbt.Rational(1, 2)])

        # For each possible card to Player Two
        for p2_card, p2_card_node in zip(remaining, p1_action_node.children):
            # If Player One checked: Player Two chooses Check or Bet
            if p1_action == "Check":
                g.append_move(p2_card_node, "Player Two", ["Check", "Bet"])
                # Player Two checks -> showdown for pot 2 (small)
                # The "Check" child is index 0
                if rank[p1_card] > rank[p2_card]:
                    g.set_outcome(p2_card_node.children[0], p1_win_small)
                else:
                    g.set_outcome(p2_card_node.children[0], p2_win_small)

                # Player Two bets -> Player One chooses Fold or Call
                # The "Bet" child is index 1
                g.append_move(p2_card_node.children[1], "Player One", ["Fold", "Call"])
                # If Player One folds -> Player Two wins pot 3 (small)
                g.set_outcome(p2_card_node.children[1].children[0], p2_win_small)
                # If Player One calls -> showdown for pot 4 (big)
                if rank[p1_card] > rank[p2_card]:
                    g.set_outcome(p2_card_node.children[1].children[1], p1_win_big)
                else:
                    g.set_outcome(p2_card_node.children[1].children[1], p2_win_big)

            # If Player One bet: Player Two chooses Fold or Call
            else:  # p1_action == "Bet"
                g.append_move(p2_card_node, "Player Two", ["Fold", "Call"])
                # If Player Two folds -> Player One wins pot 3 (small)
                g.set_outcome(p2_card_node.children[0], p1_win_small)
                # If Player Two calls -> showdown for pot 4 (big)
                if rank[p1_card] > rank[p2_card]:
                    g.set_outcome(p2_card_node.children[1], p1_win_big)
                else:
                    g.set_outcome(p2_card_node.children[1], p2_win_big)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['King'].children['Check'].children['Jack'].children['Bet'], g.root.children['King'].children['Check'].children['Queen'].children['Bet'].infoset)
    g.set_infoset(g.root.children['Queen'].children['Check'].children['Jack'], g.root.children['King'].children['Check'].children['Jack'].infoset)
    g.set_infoset(g.root.children['Queen'].children['Check'].children['Jack'].children['Bet'], g.root.children['Queen'].children['Check'].children['King'].children['Bet'].infoset)
    g.set_infoset(g.root.children['Queen'].children['Bet'].children['Jack'], g.root.children['King'].children['Bet'].children['Jack'].infoset)
    g.set_infoset(g.root.children['Jack'].children['Check'].children['King'], g.root.children['Queen'].children['Check'].children['King'].infoset)
    g.set_infoset(g.root.children['Jack'].children['Check'].children['Queen'], g.root.children['King'].children['Check'].children['Queen'].infoset)
    g.set_infoset(g.root.children['Jack'].children['Check'].children['Queen'].children['Bet'], g.root.children['Jack'].children['Check'].children['King'].children['Bet'].infoset)
    g.set_infoset(g.root.children['Jack'].children['Bet'].children['King'], g.root.children['Queen'].children['Bet'].children['King'].infoset)
    g.set_infoset(g.root.children['Jack'].children['Bet'].children['Queen'], g.root.children['King'].children['Bet'].children['Queen'].infoset)

replay_infosets(g)

# Save the EFG
g.to_efg("three_card_poker.efg")