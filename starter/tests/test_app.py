import pytest

import app as app_module
import sudoku_logic


@pytest.fixture()
def client():
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as client:
        yield client


def test_flask_app_starts_and_index_route_works(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.content_type.startswith("text/html")


def test_new_game_route_returns_a_valid_puzzle(client):
    response = client.get("/new?difficulty=medium")

    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload["puzzle"], list)
    assert len(payload["puzzle"]) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in payload["puzzle"])
    assert app_module.CURRENT["puzzle"] is not None
    assert app_module.CURRENT["solution"] is not None


def test_sudoku_logic_helpers_work_as_expected():
    empty_board = sudoku_logic.create_empty_board()
    assert len(empty_board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in empty_board)
    assert empty_board[0][0] == sudoku_logic.EMPTY
    assert sudoku_logic.is_safe(empty_board, 0, 0, 1) is True

    puzzle, solution = sudoku_logic.generate_puzzle("medium")
    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert any(cell == sudoku_logic.EMPTY for row in puzzle for cell in row)
    assert not any(cell == sudoku_logic.EMPTY for row in solution for cell in row)


def test_unique_solution_counting_and_difficulty_levels():
    puzzle, solution = sudoku_logic.generate_puzzle("medium")
    assert sudoku_logic.count_solutions(solution, limit=2) == 1
    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1

    easy_puzzle, _ = sudoku_logic.generate_puzzle(difficulty="easy")
    medium_puzzle, _ = sudoku_logic.generate_puzzle(difficulty="medium")
    hard_puzzle, _ = sudoku_logic.generate_puzzle(difficulty="hard")

    easy_clues = sum(cell != sudoku_logic.EMPTY for row in easy_puzzle for cell in row)
    medium_clues = sum(cell != sudoku_logic.EMPTY for row in medium_puzzle for cell in row)
    hard_clues = sum(cell != sudoku_logic.EMPTY for row in hard_puzzle for cell in row)

    assert easy_clues >= 36
    assert medium_clues >= 31
    assert hard_clues <= 30

    with pytest.raises(ValueError):
        sudoku_logic.generate_puzzle("impossible")


def test_check_and_hint_routes(client):
    client.get("/new?difficulty=medium")

    board = [
        [cell if cell != 0 else 0 for cell in row]
        for row in app_module.CURRENT["puzzle"]
    ]

    response = client.post(
        "/check",
        json={"board": board},
    )
    payload = response.get_json()
    assert response.status_code == 200
    assert isinstance(payload["incorrect"], list)
    assert isinstance(payload["complete"], bool)

    hint_response = client.post(
        "/hint",
        json={"board": board},
    )
    hint_payload = hint_response.get_json()
    assert hint_response.status_code == 200
    assert hint_payload["value"] == app_module.CURRENT["solution"][hint_payload["row"]][hint_payload["col"]]
    assert app_module.CURRENT["hints_used"] == 1
