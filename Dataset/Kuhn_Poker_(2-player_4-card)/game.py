import pygambit as gbt

# Create the game with players in the correct order
g = gbt.Game.new_tree(players=["Player_One", "Player_Two"],
                      title="Four-card (A,K,Q,J) betting game")

# Define the 12 ordered allocations (Player_One card followed by Player_Two card)
allocations = ["AJ", "AK", "AQ",
               "JA", "JK", "JQ",
               "KA", "KJ", "KQ",
               "QA", "QJ", "QK"]

# Add chance move at the root for the 12 allocations
g.append_move(g.root, g.players.chance, allocations)

# Set equal probabilities 1/12 for each allocation
probs = [gbt.Rational(1, 12) for _ in allocations]
g.set_chance_probs(g.root.infoset, probs)

# Pre-create outcome objects (player order: ["Player_One", "Player_Two"])
Player_One_win_small = g.add_outcome([1, -1], label="Player_One wins +1")
Player_One_win_big   = g.add_outcome([2, -2], label="Player_One wins +2")
Player_Two_win_small   = g.add_outcome([-1, 1], label="Player_Two wins +1")
Player_Two_win_big     = g.add_outcome([-2, 2], label="Player_Two wins +2")

# Helper: ranking map for comparison
rank = {"A": 4, "K": 3, "Q": 2, "J": 1}

# Iterate over each allocation node and build the subtree
for idx, chance_child in enumerate(g.root.children):
    alloc = allocations[idx]
    Player_One_card = alloc[0]  # first character is Player_One's card (e.g., 'A' from "AJ")
    Player_Two_card = alloc[1]    # second character is Player_Two's card

    # 1) Player_One's decision: Check or Bet
    g.append_move(chance_child, "Player_One", ["Check", "Bet"])
    Player_One_check_node = chance_child.children[0]  # after "Check"
    Player_One_bet_node = chance_child.children[1]    # after "Bet"

    # --- Branch: Player_One checks ---
    # 2a) Player_Two's decision: Check or Bet
    g.append_move(Player_One_check_node, "Player_Two", ["Check", "Bet"])
    Player_Two_check_node = Player_One_check_node.children[0]  # Player_Two "Check" -> showdown small
    Player_Two_bet_node = Player_One_check_node.children[1]    # Player_Two "Bet" -> Player_One chooses Fold/Call

    # Player_Two checks -> showdown, higher card wins +1 / -1
    if rank[Player_One_card] > rank[Player_Two_card]:
        g.set_outcome(Player_Two_check_node, Player_One_win_small)
    else:
        g.set_outcome(Player_Two_check_node, Player_Two_win_small)

    # Player_Two bets -> Player_One: Fold or Call
    g.append_move(Player_Two_bet_node, "Player_One", ["Fold", "Call"])
    Player_One_folds_node = Player_Two_bet_node.children[0]  # Player_One "Fold" -> Player_Two takes pot (+1)
    Player_One_calls_node = Player_Two_bet_node.children[1]  # Player_One "Call" -> showdown big (+2)

    # Player_One folds -> Player_Two +1, Player_One -1
    g.set_outcome(Player_One_folds_node, Player_Two_win_small)

    # Player_One calls -> showdown: compare cards for +2 / -2
    if rank[Player_One_card] > rank[Player_Two_card]:
        g.set_outcome(Player_One_calls_node, Player_One_win_big)
    else:
        g.set_outcome(Player_One_calls_node, Player_Two_win_big)

    # --- Branch: Player_One bets ---
    # 2b) Player_Two's decision: Fold or Call
    g.append_move(Player_One_bet_node, "Player_Two", ["Fold", "Call"])
    Player_Two_folds_node = Player_One_bet_node.children[0]  # Player_Two "Fold" -> Player_One takes pot (+1)
    Player_Two_calls_node = Player_One_bet_node.children[1]  # Player_Two "Call" -> showdown big (+2)

    # Player_Two folds -> Player_One +1, Player_Two -1
    g.set_outcome(Player_Two_folds_node, Player_One_win_small)

    # Player_Two calls -> showdown: compare cards for +2 / -2
    if rank[Player_One_card] > rank[Player_Two_card]:
        g.set_outcome(Player_Two_calls_node, Player_One_win_big)
    else:
        g.set_outcome(Player_Two_calls_node, Player_Two_win_big)

def replay_infosets(g):
    """Replays g.set_infoset(...) calls."""
    g.set_infoset(g.root.children['AK'], g.root.children['AJ'].infoset)
    g.set_infoset(g.root.children['AK'].children['Check'].children['Bet'], g.root.children['AJ'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['AQ'], g.root.children['AJ'].infoset)
    g.set_infoset(g.root.children['AQ'].children['Check'].children['Bet'], g.root.children['AJ'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['JK'], g.root.children['JA'].infoset)
    g.set_infoset(g.root.children['JK'].children['Check'], g.root.children['AK'].children['Check'].infoset)
    g.set_infoset(g.root.children['JK'].children['Check'].children['Bet'], g.root.children['JA'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['JK'].children['Bet'], g.root.children['AK'].children['Bet'].infoset)
    g.set_infoset(g.root.children['JQ'], g.root.children['JA'].infoset)
    g.set_infoset(g.root.children['JQ'].children['Check'], g.root.children['AQ'].children['Check'].infoset)
    g.set_infoset(g.root.children['JQ'].children['Check'].children['Bet'], g.root.children['JA'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['JQ'].children['Bet'], g.root.children['AQ'].children['Bet'].infoset)
    g.set_infoset(g.root.children['KA'].children['Check'], g.root.children['JA'].children['Check'].infoset)
    g.set_infoset(g.root.children['KA'].children['Bet'], g.root.children['JA'].children['Bet'].infoset)
    g.set_infoset(g.root.children['KJ'], g.root.children['KA'].infoset)
    g.set_infoset(g.root.children['KJ'].children['Check'], g.root.children['AJ'].children['Check'].infoset)
    g.set_infoset(g.root.children['KJ'].children['Check'].children['Bet'], g.root.children['KA'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['KJ'].children['Bet'], g.root.children['AJ'].children['Bet'].infoset)
    g.set_infoset(g.root.children['KQ'], g.root.children['KA'].infoset)
    g.set_infoset(g.root.children['KQ'].children['Check'], g.root.children['AQ'].children['Check'].infoset)
    g.set_infoset(g.root.children['KQ'].children['Check'].children['Bet'], g.root.children['KA'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['KQ'].children['Bet'], g.root.children['AQ'].children['Bet'].infoset)
    g.set_infoset(g.root.children['QA'].children['Check'], g.root.children['JA'].children['Check'].infoset)
    g.set_infoset(g.root.children['QA'].children['Bet'], g.root.children['JA'].children['Bet'].infoset)
    g.set_infoset(g.root.children['QJ'], g.root.children['QA'].infoset)
    g.set_infoset(g.root.children['QJ'].children['Check'], g.root.children['AJ'].children['Check'].infoset)
    g.set_infoset(g.root.children['QJ'].children['Check'].children['Bet'], g.root.children['QA'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['QJ'].children['Bet'], g.root.children['AJ'].children['Bet'].infoset)
    g.set_infoset(g.root.children['QK'], g.root.children['QA'].infoset)
    g.set_infoset(g.root.children['QK'].children['Check'], g.root.children['AK'].children['Check'].infoset)
    g.set_infoset(g.root.children['QK'].children['Check'].children['Bet'], g.root.children['QA'].children['Check'].children['Bet'].infoset)
    g.set_infoset(g.root.children['QK'].children['Bet'], g.root.children['AK'].children['Bet'].infoset)

replay_infosets(g)

# Save the EFG
g.to_efg("four_card_betting_game.efg")