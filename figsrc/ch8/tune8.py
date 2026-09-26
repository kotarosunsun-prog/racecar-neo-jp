"""8-2: run grand_prix.py with one setting over 5 seeds and store one row per run in tune8/NAME.json.
Usage: python3 tune8.py NAME '{"WALL_SPEED": "0.8"}'"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "ch7"))
import ch8run as C
import course8 as K
from ch7run import closest_to_walls

OUT = os.path.join(HERE, "tune8")
SEEDS = range(5)


def one(kw, seed):
    L, out, crashed, _ = C.gp(T=180, seed=seed, subs=C.settings(**kw) if kw else ())
    def first(cond):
        i = np.where(cond)[0]
        return round(float(L[i[0], 0]), 1) if len(i) else None
    stop = [f / 60 for f, t in out if t.startswith("FINISH へ")]
    turn = [f / 60 for f, t in out if t.startswith("TURN へ")]
    line_end = [f / 60 for f, t in out if t.startswith("WALL へ（線が見えなくなった）")]
    return dict(seed=seed, crashed=bool(crashed), stop=round(stop[0], 1) if stop else None,
                line_end=round(line_end[0], 1) if line_end else None,   # LINE -> WALL (the end of the line)
                turn=round(turn[0], 1) if turn else None,        # started to turn at the T junction
                hall=first(L[:, 2] > 2600),                      # entered the hall
                closest=round(closest_to_walls(K.gp_walls(), L, None, 3), 1),
                end=L[-1, 1:3].round().tolist())


if __name__ == "__main__":
    name, kw = sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    rows = [dict(name=name, settings=kw, **one(kw, s)) for s in SEEDS]
    for r in rows:
        print(json.dumps(r, ensure_ascii=False), flush=True)
    os.makedirs(OUT, exist_ok=True)
    json.dump(rows, open(os.path.join(OUT, name + ".json"), "w"), ensure_ascii=False, indent=1)
