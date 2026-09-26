"""A made-up Edge TPU for 9-5 (illustrative only): stop signs seen by a pinhole camera on the sim2d car.
A new answer comes every 4 frames (15 times a second) and stays until the next one.
Far (small) signs are often missed, and now and then a 'stop sign' is reported where there is none."""
import math
import numpy as np
import racecar_core as r

F = 466.0              # focal length (pixels) of the 640x480 colour camera, as in the chapter 6 models
HALF_FOV = math.radians(34.5)
SIGN = 20.0            # height of the sign (cm)


class MockVision:
    def __init__(self, world, signs, seed=0, p_false=0.01, every=4):
        self.world, self.signs, self.every = world, signs, every
        self.rng = np.random.default_rng(seed)
        self.p_false = p_false
        self.last = []
        self.last_frame = None
        self.log = []          # (frame, kind, height) for every answer: kind "true" or "false"

    def __call__(self, frame):
        if frame % self.every == 0 and frame != self.last_frame:     # the program may ask several times in one frame
            self.last = self._infer(frame)
            self.last_frame = frame
        return self.last

    def _infer(self, frame):
        w, out = self.world, []
        for sx, sy in self.signs:
            dx, dy = sx - w.x, sy - w.y
            b = w.psi - math.atan2(dy, dx)                       # bearing, clockwise (right) positive
            b = (b + math.pi) % (2 * math.pi) - math.pi
            fwd = math.hypot(dx, dy) * math.cos(b)
            if fwd < 20 or abs(b) > HALF_FOV:
                continue
            h = F * SIGN / fwd
            if h < 15:                                           # too small to be found at all
                continue
            p = 0.9 if h >= 30 else 0.35                         # small (far) signs are often missed
            if self.rng.random() < p:
                score = float(np.clip(0.5 + 0.35 * min(h / 80, 1) + self.rng.normal(0, 0.05), 0.4, 0.99))
                cx = 320 + F * math.tan(b)
                out.append(r.Detection("stop sign", score, (round(cx), 200, round(h), round(h))))
                self.log.append((frame, "true", h))
        if self.rng.random() < self.p_false:                     # a wrong answer (something that looks a little like a sign)
            h = float(self.rng.uniform(60, 110))
            out.append(r.Detection("stop sign", float(self.rng.uniform(0.5, 0.62)),
                                   (round(self.rng.uniform(100, 540)), 220, round(h), round(h))))
            self.log.append((frame, "false", h))
        return out
