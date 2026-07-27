// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const SCOREBOARD_KEY = 'sudoku-scoreboard';
let puzzle = [];
let timerSeconds = 0;
let timerInterval = null;
let elapsedSeconds = 0;
let hintsUsed = 0;

function applyTheme(isDarkMode) {
  document.body.classList.toggle('dark-mode', isDarkMode);
  localStorage.setItem('sudoku-dark-mode', isDarkMode ? 'true' : 'false');
  const themeButton = document.getElementById('theme-toggle');
  if (themeButton) {
    themeButton.innerText = isDarkMode ? 'Light Mode' : 'Dark Mode';
  }
}

function toggleTheme() {
  const isDarkMode = document.body.classList.toggle('dark-mode');
  applyTheme(isDarkMode);
}

function updateTimerDisplay() {
  const minutes = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
  const seconds = String(elapsedSeconds % 60).padStart(2, '0');
  document.getElementById('timer').innerText = `Time: ${minutes}:${seconds}`;
}

function startTimer() {
  clearInterval(timerInterval);
  elapsedSeconds = 0;
  updateTimerDisplay();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
}

function formatTime(seconds) {
  const minutes = String(Math.floor(seconds / 60)).padStart(2, '0');
  const remainingSeconds = String(seconds % 60).padStart(2, '0');
  return `${minutes}:${remainingSeconds}`;
}

function getScoreboardEntries() {
  const stored = localStorage.getItem(SCOREBOARD_KEY);
  if (!stored) {
    return [];
  }
  try {
    return JSON.parse(stored);
  } catch (error) {
    return [];
  }
}

function saveScoreboardEntry(entry) {
  const entries = getScoreboardEntries();
  entries.push(entry);
  entries.sort((a, b) => a.elapsedSeconds - b.elapsedSeconds);
  const topEntries = entries.slice(0, 10);
  localStorage.setItem(SCOREBOARD_KEY, JSON.stringify(topEntries));
  return topEntries;
}

function renderScoreboard() {
  const scoreboardDiv = document.getElementById('scoreboard');
  const entries = getScoreboardEntries();

  // Clear the scoreboard
  scoreboardDiv.innerHTML = '';

  if (!entries.length) {
    const emptyMsg = document.createElement('p');
    emptyMsg.textContent = 'No scores yet.';
    scoreboardDiv.appendChild(emptyMsg);
    return;
  }

  const ol = document.createElement('ol');
  entries.forEach((entry, index) => {
    const li = document.createElement('li');
    
    const rank = document.createElement('strong');
    rank.textContent = `#${index + 1}`;
    li.appendChild(rank);
    
    li.appendChild(document.createTextNode(' '));
    
    // Player name is safely set with textContent
    const nameSpan = document.createElement('span');
    nameSpan.textContent = entry.playerName;
    li.appendChild(nameSpan);
    
    li.appendChild(document.createTextNode(` — ${formatTime(entry.elapsedSeconds)} — ${entry.difficulty} — hints: ${entry.hintsUsed}`));
    
    ol.appendChild(li);
  });

  scoreboardDiv.appendChild(ol);
}

function toggleScoreboard() {
  const scoreboardDiv = document.getElementById('scoreboard');
  const isHidden = scoreboardDiv.hidden;
  scoreboardDiv.hidden = !isHidden;
  if (!scoreboardDiv.hidden) {
    renderScoreboard();
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const difficultySelect = document.getElementById('difficulty-select');
  const difficulty = difficultySelect.value;
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  hintsUsed = 0;
  startTimer();
}

function getBoardFromInputs() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

async function checkSolution() {
  const board = getBoardFromInputs();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }

  if (data.complete) {
    stopTimer();
    const playerName = window.prompt('Enter your name for the scoreboard:');
    if (playerName && playerName.trim()) {
      const difficultySelect = document.getElementById('difficulty-select');
      saveScoreboardEntry({
        playerName: playerName.trim(),
        elapsedSeconds,
        difficulty: difficultySelect.value,
        hintsUsed
      });
      renderScoreboard();
    }
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function requestHint() {
  const board = getBoardFromInputs();
  const msg = document.getElementById('message');
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();

  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const idx = data.row * SIZE + data.col;
  const inp = inputs[idx];
  inp.value = data.value;
  inp.disabled = true;
  inp.className = 'sudoku-cell hint-cell';
  hintsUsed = data.hints_used;
  msg.style.color = '#1976d2';
  msg.innerText = 'Hint revealed.';
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('scoreboard-toggle').addEventListener('click', toggleScoreboard);

  const storedTheme = localStorage.getItem('sudoku-dark-mode');
  const prefersDarkMode = storedTheme === 'true' || (!storedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches);
  applyTheme(prefersDarkMode);
  renderScoreboard();

  // initialize
  newGame();
});