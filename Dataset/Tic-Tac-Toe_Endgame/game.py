import pygambit as gbt
from copy import deepcopy

# Initial board (rows 0..2, cols 0..2)
# e = empty, x = X's mark, o = O's mark
initial_board = [
    ['e', 'x', 'e'],
    ['x', 'e', 'o'],
    ['x', 'e', 'o']
]

# Create game with player order matching payoff vectors: ["X", "O"]
g = gbt.Game.new_tree(players=["X", "O"],
                      title="Tic-tac-toe subtree (O to move)")

# Add common outcomes once and reuse
x_win_outcome = g.add_outcome([1, -1], label="X wins")
o_win_outcome = g.add_outcome([-1, 1], label="O wins")
draw_outcome = g.add_outcome([0, 0], label="Draw")

def check_winner(board):
    """Return 'X' if X has three in a row, 'O' if O has three in a row, else None.
       Board uses 'x' and 'o' for marks."""
    lines = []
    # rows
    for i in range(3):
        lines.append([board[i][0], board[i][1], board[i][2]])
    # cols
    for j in range(3):
        lines.append([board[0][j], board[1][j], board[2][j]])
    # diagonals
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])
    for line in lines:
        if line[0] == line[1] == line[2] and line[0] in ('x', 'o'):
            return 'X' if line[0] == 'x' else 'O'
    return None

def available_positions(board):
    """Return list of (r,c) positions that are empty, in row-major order."""
    positions = []
    for r in range(3):
        for c in range(3):
            if board[r][c] == 'e':
                positions.append((r, c))
    return positions

def action_label(pos):
    return f"Place at ({pos[0]},{pos[1]})"

def build_subtree(node, board, next_player):
    """
    Recursively expand the game tree at node given the current board and the player to move.
    next_player is either 'O' or 'X' (matching player names in g).
    """
    # If board is already terminal, set outcome and stop
    winner = check_winner(board)
    if winner is not None:
        g.set_outcome(node, x_win_outcome if winner == 'X' else o_win_outcome)
        return

    empties = available_positions(board)
    if not empties:
        # Draw
        g.set_outcome(node, draw_outcome)
        return

    # Deterministic action ordering: row-major
    empties_sorted = sorted(empties)

    # Build action labels and append move for this single node
    actions = [action_label(pos) for pos in empties_sorted]
    g.append_move(node, next_player, actions)

    # For each action/child, apply the move and either set outcome or recurse
    for idx, pos in enumerate(empties_sorted):
        child = node.children[idx]
        new_board = deepcopy(board)
        # place the appropriate mark on the new board
        mark = 'o' if next_player == 'O' else 'x'
        new_board[pos[0]][pos[1]] = mark

        # Check for terminal after the move
        winner_after = check_winner(new_board)
        if winner_after is not None:
            g.set_outcome(child, x_win_outcome if winner_after == 'X' else o_win_outcome)
            continue

        empties_after = available_positions(new_board)
        if not empties_after:
            g.set_outcome(child, draw_outcome)
            continue

        # Otherwise, recurse with the other player
        other_player = 'X' if next_player == 'O' else 'O'
        build_subtree(child, new_board, other_player)

# Build from the specified initial board; Player O moves first as stated
build_subtree(g.root, initial_board, 'O')

# Save the EFG
g.to_efg("tic_tac_toe_subgame.efg")