

This program efficiently solves word search puzzles.

Written in Python 3.12, it uses user-defined functions and methods to get the job done.
I made it so it does **not** use any external modules such as NumPy, because I wanted a challenge

## Running it

```
python searchsolve.py
```

Then open http://127.0.0.1:8000

`searchsolve.py` is both the solver and the web server. The server is `http.server` from the
standard library, so there is still nothing to install and no build step.

Type the grid one row per line — spaces between letters are optional, so `abcd` and `a b c d` are
the same row. List the words one per line (or comma separated) and hit **Solve**. Every word gets
its own colour on the grid, cells where two words cross are split between both colours, and
clicking a word in the legend or a row in the results isolates it. Ctrl+Enter solves from either
box.

## Using the solver on its own

The algorithm has no I/O in it, so it imports cleanly:

```python
from searchsolve import parse_grid, find_word, solve

grid = parse_grid("cats\norea\nwndy")
find_word(grid, "cat")   # [{'direction': 'right', 'start': (0, 0), 'path': [...]}]
solve(grid, ["cat", "dog"])
```

`find_word` returns every placement of a word, checking all eight directions from each starting
letter. `solve` does the same for a list of words, keeping the order they were given in.

## How it works

Each of the eight directions is a small function that takes a starting `(row, col)` and a step
count and returns the coordinate it lands on. `letter_at` does the bounds checking for all of them
in one place, which is what keeps a negative index from silently wrapping around to the far edge of
the grid.

Note that X and Y are flipped throughout: the notation is `(row, col)`, not `(x, y)`.
