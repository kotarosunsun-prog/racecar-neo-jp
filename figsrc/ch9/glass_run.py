"""9-3: safety_stop.py (7-1) with a LIDAR like the physical car's (720 points, about 10 turns a second), in a hallway
with a pane across it -- once as a wall the LIDAR can see, once as clear glass it cannot. Writes data/glass.json.
Run from this folder:  python3 glass_run.py   (uses the chapter 7 stand-in, because safety_stop.py is a chapter 7 program)"""
import builtins, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ch7")); sys.path.insert(0, os.path.join(HERE, ".."))
P0 = builtins.print
import ch7run as C, wallsim, sim2d
import numpy as np
from sim_real import GlassWorld

WALLS = [(-75, -100, -75, 1200), (75, -100, 75, 1200), (-75, -100, 75, -100), (-75, 1200, 75, 1200)]
PANE = [(-75, 500, 75, 500)]

if __name__ == "__main__":
    res = {}
    for name in ("wall", "glass"):
        kw = dict(wallsim.REAL, spin_hz=10)
        if name == "glass":
            w = GlassWorld(WALLS, PANE, x=0, y=0, heading_deg=90, seed=0, **kw)
        else:
            w = sim2d.World(WALLS + PANE, x=0, y=0, heading_deg=90, seed=0, **kw)
        w, out = C.run("safety_stop.py", w, 8, subs=[("MAX_SPEED = 1.0 ", "MAX_SPEED = 0.5 ")],
                       trig=lambda f, t: 1.0 if t == 1 else 0.0, joy=lambda f: (0.0, 0.0))
        L = np.array(w.log)
        P0(name, "crashed", w.crashed, "final y", round(float(L[-1, 2]), 1))
        for f, t in out:
            P0(f"   {f / 60:5.2f} {t}")
        res[name] = dict(t=L[:, 0].tolist(), y=L[:, 2].tolist(), crashed=bool(w.crashed),
                         prints=[(f, t) for f, t in out])
    json.dump(res, open(os.path.join(HERE, "data", "glass.json"), "w"), ensure_ascii=False)
