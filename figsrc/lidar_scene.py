"""Synthetic LIDAR scan (illustrative): the car in a hallway, 720 samples, clockwise from the front, cm."""
import numpy as np

SEGMENTS = [  # wall segments in cm, x to the right, y forward (car at the origin)
    ((-80, -150), (-80, 350)),     # left wall
    ((70, -150), (70, 120)),       # right wall (ends: an opening to the right)
    ((70, 120), (250, 120)),       # right corridor, near side
    ((70, 220), (250, 220)),       # right corridor, far side
    ((70, 220), (70, 350)),        # right wall after the opening
    ((-80, 350), (70, 350)),       # front wall
    ((-45, 60), (-25, 60)), ((-45, 60), (-45, 80)), ((-25, 60), (-25, 80)), ((-45, 80), (-25, 80)),  # small box ahead-left
]
MAX_RANGE = 1000

def ray(theta_deg):
    th = np.radians(theta_deg)
    dx, dy = np.sin(th), np.cos(th)
    best = 0.0
    for (x1, y1), (x2, y2) in SEGMENTS:
        ex, ey = x2 - x1, y2 - y1
        den = dx * (-ey) - dy * (-ex)
        if abs(den) < 1e-9: continue
        t = (x1 * (-ey) - y1 * (-ex)) / den
        u = (dx * y1 - dy * x1) / den
        if t > 0 and 0 <= u <= 1 and (best == 0 or t < best): best = t
    return best if best <= MAX_RANGE else 0.0

def make_scan(seed=0, n=720, dropout=0.02, noise=1.0):
    rng = np.random.default_rng(seed)
    scan = np.array([ray(i * 360 / n) for i in range(n)], dtype=np.float32)
    scan[scan > 0] += rng.normal(0, noise, (scan > 0).sum()).astype(np.float32)
    scan[rng.random(n) < dropout] = 0.0           # a few samples with no data
    scan[(np.arange(n) > 330) & (np.arange(n) < 390)] = 0.0   # open space behind the car (nothing within range)
    return scan
