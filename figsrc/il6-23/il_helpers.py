"""Helpers for 6-23: run the book's record_drive.py / drive_net.py in the stand-in racecar_core (sim2d model),
with a 'human' that is the 6-18 course program plus a smooth wobble; train with the book's train_drive.py."""
import os, sys, math, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import wallsim, sim2d
from pid_book import PID
sys.path.insert(0, HERE)
import racecar_core as r

W, PTS = wallsim.full_course()
LOG = os.path.join(HERE, "drive_log.csv")
NET = os.path.join(HERE, "drive_net.npz")


class Human:
    """the 6-18 program + a smooth wobble (sigma: size of the wobble in angle); returns the joystick x"""
    def __init__(self, sigma=0.0, tau=0.5, seed=0):
        self.expert = wallsim.CourseBook(PID(0.04, 0.005, 0.04, i_zone=20))
        self.sigma, self.tau, self.rng, self.n = sigma, tau, np.random.default_rng(seed), 0.0
    def __call__(self, scan):
        a = self.expert(scan); dt = 1 / 60
        self.n += -self.n / self.tau * dt + self.sigma * math.sqrt(2 * dt / self.tau) * self.rng.normal()
        return max(-1.0, min(1.0, a + self.n))


def exec_prog(name, T, world, joy=None, script=()):
    r.WORLD = world; r.TOTAL = int(T * 60); r.QUIET = True; r.SCRIPT = list(script); r.JOY_FN = joy
    src = open(os.path.join(HERE, name)).read()
    cwd = os.getcwd(); os.chdir(HERE)
    try:
        exec(compile(src, name, "exec"), {"__name__": "__main__"})
    finally:
        os.chdir(cwd)


def fresh():
    for f in (LOG, NET):
        if os.path.exists(f): os.remove(f)


def record(sigma, seed, T=50):
    """drive one lap with the 'human' (RT held), B at the end: the lap is added to drive_log.csv"""
    w = sim2d.World(W, x=0, y=0, heading_deg=90, seed=seed, **wallsim.REAL)
    h = Human(sigma=sigma, seed=seed); frames = int(T * 60)
    exec_prog("record_drive.py", T, w, lambda f: (h(r._Lidar.cache), 0.0), script=[("RT", 1, frames), ("B", frames, frames)])
    return w


def teach(seed, T=50):
    """the network drives; the 'human' (no wobble) shows the angle with LB held; B every 2 seconds"""
    w = sim2d.World(W, x=0, y=0, heading_deg=90, seed=seed, **wallsim.REAL)
    h = Human(sigma=0.0, seed=seed + 100); frames = int(T * 60)
    exec_prog("drive_net.py", T, w, lambda f: (h(r._Lidar.cache), 0.0),
              script=[("LB", 1, frames)] + [("B", k, k) for k in range(120, frames + 1, 120)])
    return w


def train():
    return subprocess.run([sys.executable, "train_drive.py"], cwd=HERE, capture_output=True, text=True).stdout


def drive(seed, T=60):
    w = sim2d.World(W, x=0, y=0, heading_deg=90, seed=seed, **wallsim.REAL)
    exec_prog("drive_net.py", T, w)
    L = np.array(w.log); fin = np.where(L[:, 2] > 2450)[0]
    return w, (L[fin[0], 0] if len(fin) else None)


def rows():
    return len(np.loadtxt(LOG, delimiter=","))


def offset(L):
    """signed distance (cm) of each logged position from the centre line of the course (+: right of the line)"""
    P = np.array(PTS, float); out = []
    for x, y in L[:, 1:3]:
        best, sgn = 1e9, 1.0
        for a, b in zip(P[:-1], P[1:]):
            ab = b - a; t = np.clip(((x - a[0]) * ab[0] + (y - a[1]) * ab[1]) / (ab @ ab), 0, 1)
            q = a + t * ab; d = math.hypot(x - q[0], y - q[1])
            if d < best:
                best = d; sgn = 1.0 if (ab[0] * (y - a[1]) - ab[1] * (x - a[0])) < 0 else -1.0
        out.append(sgn * best)
    return np.array(out)
