import pygambit as gbt
from copy import deepcopy

# Helper functions
def check_winner(board):
    # returns 'o' or 'x' if someone has three in a row, otherwise None
    lines = []
    # rows
    for r in range(3):
        lines.append([board[r][0], board[r][1], board[r][2]])
    # cols
    for c in range(3):
        lines.append([board[0][c], board[1][c], board[2][c]])
    # diagonals
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])
    for line in lines:
        if line[0] != 'e' and line[0] == line[1] == line[2]:
            return line[0]
    return None

def is_full(board):
    for r in range(3):
        for c in range(3):
            if board[r][c] == 'e':
                return False
    return True

# Map positions to semantic labels (row-major)
pos_labels = {
    (0,0): "Top-left",
    (0,1): "Top-center",
    (0,2): "Top-right",
    (1,0): "Middle-left",
    (1,1): "Center",
    (1,2): "Middle-right",
    (2,0): "Bottom-left",
    (2,1): "Bottom-center",
    (2,2): "Bottom-right",
}

# Initial board state from the prompt
initial_board = [
    ['e', 'x', 'e'],
    ['x', 'e', 'o'],
    ['x', 'e', 'o']
]

# Create the game: "o" moves first from this state
g = gbt.Game.new_tree(players=["o", "x"], title="Tic-tac-toe subgame from given state")

# Pre-create outcomes to reuse
o_win = g.add_outcome([1, -1], label="o wins")
x_win = g.add_outcome([-1, 1], label="x wins")
draw = g.add_outcome([0, 0], label="draw")

# Map nodes to (board, current_player)
node_info = {g.root: (initial_board, "o")}
queue = [g.root]

while queue:
    node = queue.pop(0)
    board, player = node_info[node]

    # Check terminal conditions
    winner = check_winner(board)
    if winner is not None:
        outcome = o_win if winner == 'o' else x_win
        g.set_outcome(node, outcome)
        continue
    if is_full(board):
        g.set_outcome(node, draw)
        continue

    # Collect available actions in row-major order
    actions = []
    action_positions = []
    for r in range(3):
        for c in range(3):
            if board[r][c] == 'e':
                actions.append(pos_labels[(r,c)])
                action_positions.append((r,c))

    # Append the move for the current node (one call per node)
    g.append_move(node, player, actions)

    # For each child, build the new board state and enqueue it
    # The child order matches the order of actions above
    for i, child in enumerate(node.children):
        r, c = action_positions[i]
        new_board = deepcopy(board)
        new_board[r][c] = player
        next_player = "x" if player == "o" else "o"
        node_info[child] = (new_board, next_player)
        queue.append(child)

# Save the EFG
g.to_efg("tic_tac_toe_subgame.efg")