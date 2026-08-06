import json


# each direction returns the coordinate i steps away

def up(tup, i): return (tup[0] - i, tup[1]) # this works, i is for loop iterator so we know how much to push off
def down(tup, i): return (tup[0] + i, tup[1]) # this works
def left(tup, i): return (tup[0], tup[1] - i) # this works
def right(tup, i): return (tup[0], tup[1] + i) # this works
def updiagl(tup, i): return (tup[0] - i, tup[1] - i) #this works
def updiagr(tup, i): return (tup[0] - i, tup[1] + i) # this works
def downdiagl(tup, i): return (tup[0] + i, tup[1] - i) # this works
def downdiagr(tup, i): return (tup[0] + i, tup[1] + i) # this works

DIRECTIONS = [
    ("up", up),
    ("down", down),
    ("left", left),
    ("right", right),
    ("top left", updiagl),
    ("top right", updiagr),
    ("bottom left", downdiagl),
    ("bottom right", downdiagr),
]


def letter_at(grid, coord): # the letter at coord, or None if off grid
    row, col = coord
    if row < 0 or col < 0: return None  # a negative index would wrap around
    try: return grid[row][col]
    except IndexError: return None


def parse_grid(text): # one row per line, spaces optional
    rows = []
    for line in text.splitlines():
        letters = [ch.lower() for ch in line if not ch.isspace()]
        if letters: rows.append(letters)

    width = max((len(row) for row in rows), default=0)
    for row in rows:
        row.extend([""] * (width - len(row)))  # pad ragged rows so the grid stays square
    return rows


def get_2d_coords(lst, tgt):#lst is the search, tgt is the target as a string
    cod = []
    for x in range(len(lst)):
        for p in range(len(lst[x])):
            if lst[x][p] == tgt: cod.append((x, p))
    return cod


def find_word(grid, word): # every placement of one word
    query = [ch for ch in word.lower() if not ch.isspace()]
    if not query: return []

    matches = []
    for start in get_2d_coords(grid, query[0]):
        for name, step in DIRECTIONS:
            path = [start]
            for i in range(1, len(query)):
                coord = step(start, i)
                if letter_at(grid, coord) != query[i]: break
                path.append(coord)
            else:
                matches.append({"direction": name, "start": start, "path": path})
                if len(query) == 1: break  # a single letter sits in every direction at once
    return matches


def solve(grid, words): # several words at once, order kept
    return [{"word": word, "matches": find_word(grid, word)} for word in words]


def solve_payload(grid_text, words): # the whole answer, shaped the way the page wants it
    grid = parse_grid(grid_text)
    return {"grid": grid, "results": solve(grid, words)}


def solve_json(grid_text, words_json): # the entry point the browser calls
    # strings in and a string out, so nothing depends on how JS values cross into Python
    words = [w for w in json.loads(words_json) if isinstance(w, str)]
    return json.dumps(solve_payload(grid_text, words))
