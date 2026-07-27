from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints_used': 0,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium')
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hints_used'] = 0
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] == 0:
                continue
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])

    has_empty_cells = any(cell == 0 for row in board for cell in row)
    complete = len(incorrect) == 0 and not has_empty_cells
    return jsonify({'incorrect': incorrect, 'complete': complete})


@app.route('/hint', methods=['POST'])
def get_hint():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None or board is None:
        return jsonify({'error': 'No game in progress'}), 400

    empty_positions = [
        (i, j) for i in range(sudoku_logic.SIZE)
        for j in range(sudoku_logic.SIZE)
        if board[i][j] == 0
    ]
    if not empty_positions:
        return jsonify({'error': 'No empty cells left'}), 400

    row, col = empty_positions[0]
    CURRENT['hints_used'] += 1
    return jsonify({
        'row': row,
        'col': col,
        'value': solution[row][col],
        'hints_used': CURRENT['hints_used'],
    })

if __name__ == '__main__':
    app.run(debug=True)