"""9-5: detect_stop.py in a straight hallway with two stop signs, using the made-up Edge TPU in mock_vision.py
and a LIDAR like the physical car's. "naive" stops as soon as one near sign is reported (no CONFIRM_TIME).
Writes data/stop.json.  Run from this folder:  python3 stop_run.py"""
import builtins, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
P0 = builtins.print
import ch9run as C, sim2d
import numpy as np
from mock_vision import MockVision

WALLS = [(-75, -100, -75, 4000), (75, -100, 75, 4000), (-75, -100, 75, -100)]
SIGNS = [(60, 900), (60, 1800)]
NAIVE = [("        if seen_time >= CONFIRM_TIME:", "        if near_sign() is not None:")]
T = 60

if __name__ == "__main__":
    res = {}
    for tag, subs in (("filtered", []), ("naive", NAIVE)):
        for seed in range(5):
            w = sim2d.World(WALLS, x=0, y=0, heading_deg=90, seed=seed, **C.REAL_LIDAR)
            mv = MockVision(w, SIGNS, seed=seed)
            w, out = C.run("detect_stop.py", w, T, subs=subs, vision=mv)
            L = np.array(w.log)
            states = [(f / 60, t) for f, t in out if t.endswith("へ")]
            stops = [(t, float(np.interp(t, L[:, 0], L[:, 2]))) for t, s in states if s == "STOP へ"]
            good = [any(sy - 200 <= y <= sy for _, sy in SIGNS) for _, y in stops]
            missed = sum(1 for _, sy in SIGNS if not any(sy - 200 <= y <= sy for _, y in stops))
            P0(tag, seed, "at signs", sum(good), "elsewhere", len(good) - sum(good), "signs passed without stopping", missed, "crashed", w.crashed, "stops (time, y):", [(round(a, 1), round(b)) for a, b in stops],
               "wrong answers:", sum(1 for x in mv.log if x[1] == "false"), flush=True)
            res[f"{tag}{seed}"] = dict(stops=stops)
            if seed == 0:
                res[tag] = dict(t=L[::6, 0].tolist(), y=L[::6, 2].tolist(), states=states, vlog=mv.log,
                                prints=[(f, t) for f, t in out])
    json.dump(res, open(os.path.join(HERE, "data", "stop.json"), "w"), ensure_ascii=False)
