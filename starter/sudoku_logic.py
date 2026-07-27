import copy
import random
from typing import List, Optional, Tuple

SIZE = 9
EMPTY = 0
Board = List[List[int]]

DIFFICULTY_CLUES = {
    "easy": 40,
    "medium": 32,
    "hard": 28,
}


def deep_copy(board: Board) -> Board:
    """Return a deep copy of a Sudoku board."""
    return copy.deepcopy(board)


def create_empty_board() -> Board:
    """Create an empty 9x9 Sudoku board."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board: Board, row: int, col: int, num: int) -> bool:
    """Return True if placing num at (row, col) is valid."""
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def is_valid_board(board: Board) -> bool:
    """Return True if the board is internally consistent so far."""
    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                continue
            board[row][col] = EMPTY
            if not is_safe(board, row, col, value):
                board[row][col] = value
                return False
            board[row][col] = value
    return True


def find_empty_cell(board: Board) -> Optional[Tuple[int, int]]:
    """Return the first empty cell location, if any."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None


def fill_board(board: Board) -> bool:
    """Fill a board with a valid Sudoku solution using backtracking."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def count_solutions(board: Board, limit: int = 2) -> int:
    """Count valid Sudoku solutions up to the provided limit."""
    if limit <= 0:
        return 0

    working_board = deep_copy(board)
    if not is_valid_board(working_board):
        return 0

    solutions = 0

    def backtrack(current_board: Board) -> None:
        nonlocal solutions
        if solutions >= limit:
            return

        empty_cell = find_empty_cell(current_board)
        if empty_cell is None:
            solutions += 1
            return

        row, col = empty_cell
        for candidate in range(1, SIZE + 1):
            if is_safe(current_board, row, col, candidate):
                current_board[row][col] = candidate
                backtrack(current_board)
                if solutions >= limit:
                    return
                current_board[row][col] = EMPTY

    backtrack(working_board)
    return solutions


def remove_cells(board: Board, clues: int) -> None:
    """Remove cells from the board while preserving a unique solution."""
    target_empty_cells = max(0, SIZE * SIZE - clues)
    if target_empty_cells == 0:
        return

    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)

    removed = 0
    for row, col in positions:
        if removed >= target_empty_cells:
            break
        if board[row][col] == EMPTY:
            continue

        original_value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) == 1:
            removed += 1
        else:
            board[row][col] = original_value

# NOTE: Copilot's first version of this function accepted both a raw
# `clues` integer and a `difficulty` string with a helper (_resolve_clue_count)
# to reconcile them. This was rejected as unnecessarily complex for this
# project's actual use case (only difficulty is ever passed in from app.py),
# so it was simplified to take a single `difficulty` parameter.

def generate_puzzle(difficulty: str = "medium") -> Tuple[Board, Board]:
    """Generate a Sudoku puzzle and its solved board for the requested difficulty."""
    normalized_difficulty = difficulty.lower()
    if normalized_difficulty not in DIFFICULTY_CLUES:
        raise ValueError("difficulty must be one of: easy, medium, hard")

    clue_count = DIFFICULTY_CLUES[normalized_difficulty]
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clue_count)
    puzzle = deep_copy(board)
    return puzzle, solution
