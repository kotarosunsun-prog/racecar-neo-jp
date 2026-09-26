"""Run the book's chapter 7 programs (copies in this folder) in the stand-in racecar_core (sim2d model)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import wallsim, sim2d                      # wallsim puts the racecar library on the path
sys.path.insert(0, HERE)
import racecar_core as r


def run(prog, world, T, script=(), subs=(), joy=None, trig=None, image=None, on_frame=None, stop_on_crash=True):
    """exec prog (a file in this folder) for T seconds; returns (world, prints) with prints = [(frame, text)]"""
    r.WORLD = world; r.TOTAL = int(round(T * 60)); r.QUIET = True; r.SCRIPT = list(script)
    r.JOY_FN, r.TRIG_FN, r.IMAGE_FN, r.ON_FRAME = joy, trig, image, on_frame
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


def box(cx, cy, w, h):
    """a rectangular obstacle (w wide in x, h tall in y) as wall segments"""
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    return [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]


def drive(prog, W, T, subs=(), seed=0, x=0.0, y=0.0, heading=90.0, **kw):
    """run prog on walls W with the realistic LIDAR (wallsim.REAL); returns (log array, prints, crashed)"""
    world = sim2d.World(W, x=x, y=y, heading_deg=heading, seed=seed, **dict(wallsim.REAL, **kw))
    world, out = run(prog, world, T, subs=subs)
    return np.array(world.log), out, world.crashed


def closest_to_walls(W, L, n=None, step=3):
    """smallest distance from the car centre to the walls over the first n logged frames"""
    Wn = np.array(W, float); a = Wn[:, :2]; b = Wn[:, 2:]; ab = b - a
    best = 1e9
    for px, py in L[:n:step, 1:3]:
        p = np.array([px, py]); t = np.clip(((p - a) * ab).sum(1) / (ab * ab).sum(1), 0, 1)
        best = min(best, float(np.min(np.linalg.norm(a + ab * t[:, None] - p, axis=1))))
    return best


def draw_walls(ax, W, **kw):
    for x1, y1, x2, y2 in W:
        ax.plot([x1, x2], [y1, y2], color=kw.get("color", "#495057"), lw=kw.get("lw", 1.8), solid_capstyle="round")


# the settings at the top of gap_follow.py as printed in the book (the final ones, 7-11)
DEFAULTS = dict(THRESHOLD="150.0", PICK='"widest"', AIM='"center"', BUBBLE="20.0", HALF_WIDTH="20.0", JUMP="50.0",
                MIN_SPEED="0.4", MAX_SPEED="1.0", KV="0.004")
# 7-7 .. 7-10 compare methods at a constant speed 0.5, with the bubble and the disparity extender off unless asked for
PLAIN = dict(BUBBLE="0.0", HALF_WIDTH="0.0", MIN_SPEED="0.5", MAX_SPEED="0.5")


def settings(base="plain", **kw):
    """substitutions for the settings at the top of gap_follow.py: base "plain" starts from PLAIN, "final" from the file"""
    want = dict(PLAIN, **kw) if base == "plain" else dict(kw)
    return [(f"{k} = {DEFAULTS[k]} ", f"{k} = {v} ") for k, v in want.items() if v != DEFAULTS[k]]
