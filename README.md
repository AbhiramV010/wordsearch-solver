# Word Search Solver

- Solves word search grids, all eight directions
- Python, standard library only, no NumPy, nothing to install
- `solver.py` holds the algorithm and is the only copy of it
- `searchsolve.py` serves the page locally, no build step

## Run

```
python searchsolve.py
```

- Open http://127.0.0.1:8000

## Deployed

- The site is static, so the host runs no Python of its own
- Instead the page loads Pyodide, which is CPython built for WebAssembly, and runs `solver.py` in the browser
- So the deployed solver is the same Python file, not a rewrite in JavaScript
- The interpreter is fetched on the first solve only, then cached by the browser
- Nothing is uploaded anywhere, the grid never leaves the page
- The Pyodide version is pinned in `app.js`, so an upstream release cannot change what the site runs

## Using it

- Grid: one row per line, spaces optional, so `abcd` and `a b c d` are the same row
- Ragged rows get padded to the widest row
- Words: one per line, or comma separated
- Ctrl+Enter (Cmd+Enter) solves from either box
- One colour per word, reused past 8 words
- Where two words cross, the cell takes the colour of the first one drawn
- Checkboxes in the legend and results toggle what's drawn, either a whole word or one placement
- Clear wipes both boxes and the output

## Solver on its own

- No I/O in the algorithm, so it imports clean

```python
from solver import parse_grid, find_word, solve

grid = parse_grid("cats\norea\nwndy")
find_word(grid, "cat")   # [{'direction': 'right', 'start': (0, 0), 'path': [...]}]
solve(grid, ["cat", "dog"])
```

- `parse_grid(text)` → list of rows, lowercased, whitespace stripped
- `find_word(grid, word)` → every placement, checking all 8 directions from each starting letter
- `solve(grid, words)` → same for a list, input order kept
- Match shape: `{"direction", "start": (row, col), "path": [(row, col), ...]}`
- A one-letter word matches once, not eight times

## API

- `solve_json(grid_text, words_json)` → JSON string, the entry point the browser calls
- Both arguments are plain strings, so nothing depends on how JS values cross into Python
- `POST /api/solve` with `{"grid": "<text>", "words": ["cat", ...]}` still works while `searchsolve.py` is running
- Both return `{"grid": [[...]], "results": [{"word", "matches"}]}`

## How it works

- Each direction is a small function: takes a start `(row, col)` and a step count, returns where it lands
- `letter_at` does the bounds checking for all eight in one place
- That's what stops a negative index from wrapping to the far edge of the grid
- X and Y are flipped throughout, so the notation is `(row, col)`, not `(x, y)`
