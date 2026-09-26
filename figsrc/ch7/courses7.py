"""Courses for chapter 7 (sim2d model)."""
import numpy as np
import wallsim
from ch7run import box


def corner_course():
    """course A: the 6-18 course (walls only)"""
    W, _ = wallsim.full_course()
    return W


def obstacle_course():
    """course B: an L-shaped corridor (260 cm wide) with boxes"""
    pts = [(0, -100), (0, 1000), (800, 1000), (800, 2100)]
    W = wallsim.corridor(pts, [260, 260, 260], close_start=True, close_end=False)
    W += box(-60, 350, 60, 60) + box(70, 700, 60, 60) + box(400, 1060, 60, 80) + box(760, 1500, 50, 50) + box(870, 1800, 50, 50)
    return W


def posts_hall(seed=3, y0=0.0, closed=True):
    """course C: a hall 600 cm wide with square posts (30 cm) in staggered rows"""
    W = [(-300, y0 - 100, -300, y0 + 2300), (300, y0 - 100, 300, y0 + 2300)]
    if closed:
        W.append((-300, y0 - 100, 300, y0 - 100))
    rng = np.random.default_rng(seed)
    for k, y in enumerate(range(300, 2100, 250)):
        xs = [-150, 0, 150] if k % 2 == 0 else [-225, -75, 75, 225]
        for x in xs:
            if rng.random() < 0.7:
                W += box(x + rng.uniform(-30, 30), y0 + y + rng.uniform(-30, 30), 30, 30)
    return W


def mixed_course():
    """course D: the 6-17 corridor with openings (0 .. 2600), then a hall with posts (2600 .. 4700)"""
    W = list(wallsim.openings_course())
    W += [(75, 2600, 300, 2600), (-75, 2600, -300, 2600)]
    W += [w for w in posts_hall(seed=3, y0=2600, closed=False)]
    return W


BLUE_BGR = (205, 120, 40)      # blue cone (pass on its left)
OTHER_BGR = (180, 50, 200)     # the model's second colour (purple; red in Lab H) -- pass on its right


def slalom_cones(kind="straight", n=6, gap=150.0):
    """cones (x, y, colour) for 7-4: every other cone is blue"""
    cones = []
    for k in range(n):
        y = 250 + k * gap
        x = 0.0 if kind == "straight" else 120 * np.sin(k * 0.9)
        cones.append((x, y, "blue" if k % 2 == 0 else "other"))
    return cones
