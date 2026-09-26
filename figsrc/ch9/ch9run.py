"""Run the book's chapter 9 programs (copies in this folder) in the stand-in racecar_core (sim2d model).
"real-like" worlds use a LIDAR with 1080 points spinning 10 times a second (the physical car's RPLIDAR)."""
import math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import wallsim, sim2d                      # wallsim puts the racecar library on the path
from sim_real import GlassWorld, real_like
sys.path.insert(0, HERE)
import racecar_core as r


def run(prog, world, T, subs=(), image=None, phys=None, vision=None, on_frame=None, stop_on_crash=True, chdir=HERE, has_vision=True, script=()):
    """exec prog (a file in chdir) for T seconds; returns (world, prints) with prints = [(frame, text)]"""
    r.WORLD = world; r.TOTAL = int(round(T * 60)); r.QUIET = True; r.SCRIPT = list(script)
    r.JOY_FN, r.TRIG_FN, r.IMAGE_FN, r.ON_FRAME, r.STOP_FN = None, None, image, on_frame, None
    r.PHYS_FN, r.VISION_FN, r.HAS_VISION = phys, vision, has_vision
    r.STOP_ON_CRASH = stop_on_crash
    r.OUT.clear(); r.TELEMETRY_ROWS.clear(); r._Telemetry.names = None
    src = open(os.path.join(chdir, prog)).read()
    for a, b in subs:
        assert a in src, a
        src = src.replace(a, b)
    cwd = os.getcwd(); os.chdir(chdir)
    sys.path.insert(0, chdir)
    try:
        exec(compile(src, prog, "exec"), {"__name__": "__main__"})
    finally:
        os.chdir(cwd); sys.path.remove(chdir)
    return world, list(r.OUT)


REAL_LIDAR = dict(wallsim.REAL, spin_hz=10)   # the physical car's LIDAR turns about 10 times a second
