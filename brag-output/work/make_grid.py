import json, random, sys
sys.path.insert(0, "/home/user/wordsearch-solver")
from solver import parse_grid, solve
random.seed(7)
N = 10
words = [("python",(1,1),(1,1)), ("search",(8,8),(0,-1)), ("grid",(2,8),(1,0)), ("solve",(9,0),(-1,1)), ("wasm",(0,3),(0,1)), ("find",(4,0),(1,0))]
g = [[None]*N for _ in range(N)]
for w,(r,c),(dr,dc) in words:
    for i,ch in enumerate(w):
        rr,cc = r+dr*i, c+dc*i
        assert g[rr][cc] in (None,ch), (w,rr,cc,g[rr][cc])
        g[rr][cc] = ch
for attempt in range(500):
    gg = [[ch or random.choice("abcdefghiklmnoprstuvwy") for ch in row] for row in g]
    text = "\n".join("".join(r) for r in gg)
    res = solve(parse_grid(text), [w for w,_,_ in words])
    if all(len(r["matches"])==1 for r in res): break
else: raise SystemExit("no clean grid")
print(text)
json.dump({"text": text, "results": res}, open("solved.json","w"))
for r in res: print(r["word"], r["matches"][0]["direction"])
