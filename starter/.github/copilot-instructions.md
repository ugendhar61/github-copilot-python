# Copilot Instructions for Sudoku Refactor Project

## Project Structure
- `app.py` — Flask routes only. Keep route handlers thin; delegate logic to `sudoku_logic.py`.
- `sudoku_logic.py` — All puzzle generation, validation, solving, and difficulty logic lives here.
- `static/main.js` — Frontend game logic (board rendering, timer, hints, check, dark mode, scoreboard).
- `static/styles.css` — All styling, including 3x3 alternating colors and responsive/dark mode rules.
- `templates/index.html` — Page structure only; no inline logic.

## Code Style (Python)
- Follow PEP8.
- Use type hints on function signatures.
- Add a docstring to every function describing purpose, parameters, and return value.
- Prefer small, single-responsibility functions over large ones.
- Use explicit error handling (try/except with meaningful messages) instead of silent failures.
- Avoid global mutable state where possible; pass data explicitly between functions.

## Code Style (JavaScript)
- Use modern ES6+ syntax (const/let, arrow functions, template literals).
- Keep DOM manipulation, game state, and API calls in clearly separated functions/modules.
- Comment any non-obvious logic (e.g., unique-solution validation, timer logic).

## Testing
- Use pytest for backend tests.
- Every new feature (difficulty levels, hint, check, scoreboard) should have at least one test.
- Run `pytest` before and after every refactor step to confirm nothing breaks.

## General
- When Copilot suggests code, prefer clarity over cleverness.
- Flag any suggestion that duplicates existing logic instead of reusing it.
- Explain any unfamiliar library, pattern, or Flask feature before using it.