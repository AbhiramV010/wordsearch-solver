# Brag plan: Word Search Solver

**What it is:** A website that finds every word in a word search grid, checking all 8 directions.
**For:** Anyone stuck on a puzzle, plus developers who like a neat trick.
**What sets it apart:** The deployed site runs the real Python solver (`solver.py`) in the browser through Pyodide. No server, no JS rewrite, and the grid never leaves the page.
**Most impressive claim:** Real CPython, compiled to WebAssembly, solving puzzles on a static Netlify page.
**Visual hook:** A dense letter grid where PYTHON lights up along a diagonal.
**Real UI shown:** The site's own header copy, input panel, Solve button, colour palette, legend and results rows, all built from `styles.css` and `app.js` values. Grid and answers come from running `solver.py` on the demo grid.
**Tone:** `default` (punchy, clean). Site's dark-theme tokens.
**Share caption:** see `share-copy.txt`.

## Identity
- Font: Stack Sans Notch (shipped with the site), DejaVu Sans Mono for code
- Colours: bg `#14171b`, panel `#1c2026`, line `#2e343d`, accent `#5b8cff`, word colours from `app.js` COLORS
- Logo: `favicon.svg` (papyrus grid + magnifier)

## Storyboard (20.0s, 30fps)

| # | Time | Scene | On-screen text | Sound |
|---|---|---|---|---|
| 1 | 0.0–3.2 | Hook. 10×10 grid pops in, scan sweeps, PYTHON lights diagonally | "Somewhere in here is PYTHON." | Pad + kick enters, rising chime on hit |
| 2 | 3.2–8.0 | Reveal. Site window slides in, grid rows typed, words typed, cursor clicks Solve | "Paste the grid. List the words." | Soft key clicks, button click |
| 3 | 8.0–12.6 | Result. Grid + results list, six words light up in turn with their real directions | "Every word. All 8 directions." | One chime per word, in key |
| 4 | 12.6–16.6 | Highlight. `find_word` code card + pipeline solver.py → Pyodide → browser | "Real Python. In your browser." / "No server. Your grid never leaves the page." | Music full |
| 5 | 16.6–20.0 | Outro. Logo, name, URL, credit | "Word Search Solver" / searchsolver.netlify.app / Built by Abhiram Vadali | Resolve chord, tail |

Transitions dip through the background (old out, then new in) to avoid double exposures.
No personal data beyond the author credit already in the site footer.
