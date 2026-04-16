import random
import copy


TILE_VALUES = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]


def new_board():
    board = [[0] * 4 for _ in range(4)]
    board = add_random_tile(board)
    board = add_random_tile(board)
    return board


def empty_cells(board):
    return [(r, c) for r in range(4) for c in range(4) if board[r][c] == 0]


def add_random_tile(board):
    empties = empty_cells(board)
    if not empties:
        return board
    r, c = random.choice(empties)
    board[r][c] = 4 if random.random() < 0.1 else 2
    return board


def slide_row_left(row):
    """Slide and merge a single row to the left. Returns (new_row, score_gained)."""
    tiles = [x for x in row if x != 0]
    score = 0
    merged = []
    i = 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            val = tiles[i] * 2
            merged.append(val)
            score += val
            i += 2
        else:
            merged.append(tiles[i])
            i += 1
    new_row = merged + [0] * (4 - len(merged))
    return new_row, score


def move_left(board):
    new_board = []
    score = 0
    for row in board:
        new_row, s = slide_row_left(row)
        new_board.append(new_row)
        score += s
    return new_board, score


def move_right(board):
    new_board = []
    score = 0
    for row in board:
        new_row, s = slide_row_left(row[::-1])
        new_board.append(new_row[::-1])
        score += s
    return new_board, score


def transpose(board):
    return [list(row) for row in zip(*board)]


def move_up(board):
    transposed, score = move_left(transpose(board))
    return transpose(transposed), score


def move_down(board):
    transposed, score = move_right(transpose(board))
    return transpose(transposed), score


MOVES = {
    "left":  move_left,
    "right": move_right,
    "up":    move_up,
    "down":  move_down,
}


def apply_move(board, direction):
    """Apply a move. Returns (new_board, score_gained, moved)."""
    fn = MOVES[direction]
    new_b, score = fn(copy.deepcopy(board))
    moved = new_b != board
    if moved:
        new_b = add_random_tile(new_b)
    return new_b, score, moved


def can_move(board):
    if empty_cells(board):
        return True
    for r in range(4):
        for c in range(4):
            val = board[r][c]
            if c < 3 and board[r][c + 1] == val:
                return True
            if r < 3 and board[r + 1][c] == val:
                return True
    return False


def is_won(board):
    return any(board[r][c] >= 2048 for r in range(4) for c in range(4))


def is_game_over(board):
    return not can_move(board)


def get_max_tile(board):
    return max(board[r][c] for r in range(4) for c in range(4))
