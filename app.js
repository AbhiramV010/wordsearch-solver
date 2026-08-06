const gridInput = document.getElementById("grid-input");
const wordsInput = document.getElementById("words-input");
const outputEl = document.getElementById("output");
const legendEl = document.getElementById("legend");
const gridEl = document.getElementById("grid");
const resultsEl = document.getElementById("results");
const statusEl = document.getElementById("status");

// one colour per word, reused when words outnumber colours
const COLORS = [
  "#4c9aff", "#ffab00", "#57d9a3", "#ff8f73",
  "#b18cff", "#79e2f2", "#f78fb3", "#c0ca33",
];

let grid = [];
let results = [];
let selected = new Set(); // "wordIndex:matchIndex" keys currently drawn on the grid

const colorOf = (i) => COLORS[i % COLORS.length];

const keyOf = (wordIndex, matchIndex) => `${wordIndex}:${matchIndex}`;

// every match in the current results, as selection keys
function allKeys() {
  const keys = [];
  results.forEach((result, wordIndex) => {
    result.matches.forEach((_, matchIndex) => keys.push(keyOf(wordIndex, matchIndex)));
  });
  return keys;
}

const keysOfWord = (wordIndex) =>
  results[wordIndex].matches.map((_, matchIndex) => keyOf(wordIndex, matchIndex));

function setSelected(keys, on) {
  for (const key of keys) {
    if (on) selected.add(key);
    else selected.delete(key);
  }
  render();
}

// checkbox that reflects a group: checked when all on, indeterminate when some
function groupBox(keys) {
  const box = document.createElement("input");
  box.type = "checkbox";
  const on = keys.filter((key) => selected.has(key)).length;
  box.checked = keys.length > 0 && on === keys.length;
  box.indeterminate = on > 0 && on < keys.length;
  box.addEventListener("change", () => setSelected(keys, box.checked));
  return box;
}

function parseWords(text) {
  return text.split(/[\s,]+/).filter(Boolean);
}

function status(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}

// Pyodide is CPython built for WebAssembly, so solver.py runs as Python in the
// browser. That is what lets a static host serve this with no back end at all.
// Pinned, so an upstream release can never change what the site runs
const PYODIDE_URL = "https://cdn.jsdelivr.net/npm/pyodide@314.0.3/";

let pythonPromise = null; // the interpreter is fetched once, then reused

function startPython() {
  if (!pythonPromise) {
    pythonPromise = loadPython();
    // a preload that fails is reported when a solve asks for it, not on an empty page
    pythonPromise.catch(() => {});
  }
  return pythonPromise;
}

async function loadPython() {
  const { loadPyodide } = await import(`${PYODIDE_URL}pyodide.mjs`);
  const pyodide = await loadPyodide({ indexURL: PYODIDE_URL });

  const response = await fetch("solver.py");
  if (!response.ok) throw new Error(`could not load solver.py (${response.status})`);
  pyodide.runPython(await response.text());

  console.log(`Python ${pyodide.runPython("import sys; sys.version")} via Pyodide ${pyodide.version}`);
  return pyodide.globals.get("solve_json"); // strings in, JSON string out
}

async function requestSolve() {
  const gridText = gridInput.value;
  const words = parseWords(wordsInput.value);

  if (!gridText.trim()) return status("Enter a grid first.", true);
  if (words.length === 0) return status("Enter at least one word.", true);

  status("Solving…");

  let data;
  try {
    const solveJson = await startPython();
    data = JSON.parse(solveJson(gridText, JSON.stringify(words)));
  } catch (err) {
    pythonPromise = null; // a failed load should not poison every later attempt
    return status(`Could not start the Python solver: ${err.message}`, true);
  }

  grid = data.grid;
  // a word that is not in the grid is dropped here, so nothing downstream lists it
  results = data.results.filter((result) => result.matches.length > 0);
  selected = new Set(allKeys()); // start with everything shown
  render();

  status(results.length === 0
    ? "No words found."
    : `${results.length} word${results.length > 1 ? "s" : ""} found.`);
}

// which colour lands on each cell, given the ticked checkboxes
function highlightMap() {
  const map = new Map();

  results.forEach((result, wordIndex) => {
    result.matches.forEach((match, matchIndex) => {
      if (!selected.has(keyOf(wordIndex, matchIndex))) return;

      for (const [r, c] of match.path) {
        const key = `${r},${c}`;
        if (!map.has(key)) map.set(key, wordIndex); // where words cross, the first one keeps the cell
      }
    });
  });

  return map;
}

function renderGrid() {
  const map = highlightMap();
  const cols = grid[0] ? grid[0].length : 0;

  gridEl.innerHTML = "";
  gridEl.style.gridTemplateColumns = `repeat(${cols}, minmax(28px, 38px))`;

  grid.forEach((line, r) => {
    line.forEach((letter, c) => {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.textContent = letter;

      const hit = map.get(`${r},${c}`);
      if (hit !== undefined) {
        cell.classList.add("hit");
        cell.style.background = colorOf(hit); // word 0 is a valid index, so check for undefined
      }

      gridEl.appendChild(cell);
    });
  });
}

function renderLegend() {
  legendEl.innerHTML = "";

  const every = allKeys();
  if (every.length === 0) return; // nothing found, so nothing to tick

  const head = document.createElement("div");
  head.className = "legend-head";

  const master = document.createElement("label");
  master.className = "check master";
  const masterBox = groupBox(every);
  masterBox.dataset.focusKey = "all";
  master.append(masterBox, Object.assign(document.createElement("span"), {
    textContent: "All words",
  }));

  const note = document.createElement("span");
  note.className = "legend-note";
  note.textContent = `${selected.size} of ${every.length} shown`;

  head.append(master, note);
  legendEl.appendChild(head);

  const list = document.createElement("div");
  list.className = "legend-list";

  results.forEach((result, wordIndex) => {
    const count = result.matches.length;
    const chip = document.createElement("label");
    chip.className = "check chip";

    const box = groupBox(keysOfWord(wordIndex));
    box.dataset.focusKey = `word:${wordIndex}`;
    chip.appendChild(box);

    const swatch = document.createElement("span");
    swatch.className = "swatch";
    swatch.style.background = colorOf(wordIndex);

    const label = document.createElement("span");
    label.textContent = count === 1 ? result.word : `${result.word} ×${count}`;

    chip.append(swatch, label);
    list.appendChild(chip);
  });

  legendEl.appendChild(list);
}

function renderResults() {
  resultsEl.innerHTML = "";

  if (results.length === 0) {
    resultsEl.innerHTML = '<p class="empty">None of those words are in this grid.</p>';
    return;
  }

  const hint = document.createElement("p");
  hint.className = "count";
  hint.textContent = "Tick a word above, or a single placement below, to show it on the grid.";
  resultsEl.appendChild(hint);

  results.forEach((result, wordIndex) => {
    result.matches.forEach((match, matchIndex) => {
      const key = keyOf(wordIndex, matchIndex);
      const row = document.createElement("label");
      row.className = "result check";
      row.classList.toggle("active", selected.has(key));
      row.style.borderLeftColor = colorOf(wordIndex);

      const box = groupBox([key]);
      box.dataset.focusKey = `match:${key}`;

      const where = `Row ${match.start[0] + 1}, Col ${match.start[1] + 1}`;
      // a one-letter word sits in all eight directions
      const dir = match.path.length > 1 ? `going ${match.direction}` : "single letter";
      const body = document.createElement("span");
      body.className = "result-body";
      body.innerHTML = `<span class="word">${result.word}</span>
                        <span>${where}</span>
                        <span class="dir">${dir}</span>`;

      row.append(box, body);
      resultsEl.appendChild(row);
    });
  });
}

function render() {
  // re-rendering replaces the checkbox that was just clicked, so put focus back
  const focusKey = document.activeElement && document.activeElement.dataset
    ? document.activeElement.dataset.focusKey
    : null;

  outputEl.hidden = false;
  renderLegend();
  renderGrid();
  renderResults();

  if (focusKey) {
    const restored = outputEl.querySelector(`[data-focus-key="${focusKey}"]`);
    if (restored) restored.focus();
  }
}

document.getElementById("solve").addEventListener("click", requestSolve);

document.getElementById("clear").addEventListener("click", () => {
  gridInput.value = "";
  wordsInput.value = "";
  grid = [];
  results = [];
  selected = new Set();
  outputEl.hidden = true;
  status("");
  gridInput.focus();
});

// ctrl/cmd+enter solves from either box
for (const box of [gridInput, wordsInput]) {
  box.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      requestSolve();
    }
  });
}

// the interpreter starts downloading while the grid is still being typed, so by
// the time Solve is pressed it is usually already there, with nothing to announce
startPython();
