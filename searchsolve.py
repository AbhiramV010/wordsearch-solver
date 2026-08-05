"""
    Word search solver
    Searches a grid in all eight directions, standard library only
    Run this file to serve the web front end
    In this program, X and Y are flipped, so instead of X,Y the notation is Y,X
"""

import json
import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent
HOST = "127.0.0.1"
PORT = 8000

mimetypes.add_type("font/ttf", ".ttf")  # not in every platform's mime table


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


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path.rstrip("/") != "/api/solve":
            self.send_error(404, "unknown endpoint")
            return

        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_error(400, "expected a JSON body")
            return

        grid = parse_grid(payload.get("grid") or "")
        words = [w for w in (payload.get("words") or []) if isinstance(w, str)]
        self.send_json({"grid": grid, "results": solve(grid, words)})

    def send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")  # so edits show up on refresh
        super().end_headers()

    def log_message(self, *_args):
        pass  # the server does not need to narrate every request


if __name__ == "__main__":
    print("Running at https://localhost:8000")
    with ThreadingHTTPServer((HOST, PORT), Handler) as httpd:
        httpd.serve_forever()
