# Word Search Solver

- Solves word search grids, all eight directions
- Python 3.12, standard library only, no NumPy, nothing to install
- `searchsolve.py` is both the solver and the web server (`http.server`), so no build step

## Run

```
python searchsolve.py
```

- Open http://127.0.0.1:8000

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
from searchsolve import parse_grid, find_word, solve

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

- `POST /api/solve` with `{"grid": "<text>", "words": ["cat", ...]}`
- Returns `{"grid": [[...]], "results": [{"word", "matches"}]}`

## How it works

- Each direction is a small function: takes a start `(row, col)` and a step count, returns where it lands
- `letter_at` does the bounds checking for all eight in one place
- That's what stops a negative index from wrapping to the far edge of the grid
- X and Y are flipped throughout, so the notation is `(row, col)`, not `(x, y)`
