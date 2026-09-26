"""Run the book's chapter 8 programs (copies in this folder) in the stand-in racecar_core (sim2d model)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import wallsim, sim2d                      # wallsim puts the racecar library on the path
sys.path.insert(0, HERE)
import racecar_core as r
import course8 as K


def run(prog, world, T, subs=(), image=None, on_frame=None, stop_fn=None, stop_on_crash=True):
    """exec prog (a file in this folder) for T seconds; returns (world, prints) with prints = [(frame, text)]"""
    r.WORLD = world; r.TOTAL = int(round(T * 60)); r.QUIET = True; r.SCRIPT = []
    r.JOY_FN, r.TRIG_FN, r.IMAGE_FN, r.ON_FRAME, r.STOP_FN = None, None, image, on_frame, stop_fn
    r.STOP_ON_CRASH = stop_on_crash
    r.OUT.clear()
    src = open(os.path.join(HERE, prog)).read()
    for a, b in subs:
        assert a in src, a
        src = src.replace(a, b)
    cwd = os.getcwd(); os.chdir(HERE)
    try:
        exec(compile(src, prog, "exec"), {"__name__": "__main__"})
    finally:
        os.chdir(cwd)
    return world, list(r.OUT)


def gp(prog="grand_prix.py", T=150, subs=(), seed=0, walls=None, **kw):
    """drive prog on the book's grand-prix course; returns (log array, prints, crashed, finish time or None)"""
    W = K.gp_walls() if walls is None else walls
    world = sim2d.World(W, x=0, y=0, heading_deg=90, seed=seed, **dict(wallsim.REAL, **kw))
    cam = K.GPCamera(); rng = np.random.default_rng(seed)
    image = lambda f: cam.render(world, f, rng=rng)
    stopped = {"n": 0}
    def stop_fn():                           # end the run once the car has stood still for 2 s past the hall
        if world.y > K.FINISH_Y and abs(world.v) < 0.5: stopped["n"] += 1
        else: stopped["n"] = 0
        return stopped["n"] > 120
    world, out = run(prog, world, T, subs=subs, image=image, stop_fn=stop_fn)
    L = np.array(world.log)
    fin = np.where(L[:, 2] > K.FINISH_Y)[0]
    return L, out, world.crashed, (float(L[fin[0], 0]) if len(fin) else None)


def settings(**kw):
    """substitutions for the constants at the top of grand_prix.py, e.g. settings(LINE_SPEED="0.7")"""
    src = open(os.path.join(HERE, "grand_prix.py")).read().split("\n")
    subs = []
    for k, v in kw.items():
        line = next(l for l in src if l.startswith(k + " = "))
        value = line.split("#")[0][len(k) + 3:].rstrip()
        subs.append((line + "\n", line.replace(f"{k} = {value}", f"{k} = {v}", 1) + "\n"))
    return subs
