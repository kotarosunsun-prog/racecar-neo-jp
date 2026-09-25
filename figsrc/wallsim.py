"""wallsim.py -- helpers for the chapter 6 wall-following figures (illustrative sim2d model, NOT the RACECAR simulator).
The controllers below do exactly what the book's programs do (wall_follow_p.py, wall_follow_pd.py, wall_follow_angle.py),
and simulate() calls them in the same order as the simulator loop: read LIDAR -> update() -> the car moves one frame."""
import os, sys, math, struct
import numpy as np
import sim2d
sys.path.insert(0, os.environ.get("RACECAR_LIBRARY", "../../racecar-neo-library/library"))
import racecar_utils as rc_utils

DT = struct.unpack("f", struct.pack("f", 1 / 60))[0]      # rc.get_delta_time() at 60 frames per second
# "realistic" LIDAR: 2 % noise (like the simulator's Realism setting), a scan that spins 6 times a second, 1 frame late
REAL = dict(lidar_noise=0.0, lidar_rel_noise=0.02, spin_hz=6, delay_frames=1)
IDEAL = dict(lidar_noise=0.0, delay_frames=0)               # exact, up-to-date LIDAR
NO_LAG = dict(lidar_noise=0.0, delay_frames=0, tau_steer=1 / 60, tau_v=1 / 60)   # ... and no steering / speed lag


def right_wall_distance(scan, max_wall=300.0):
    """6-6: closest point on the right, then the average of the nearby samples that are close to it"""
    closest_angle, closest = rc_utils.get_lidar_closest_point(scan, (45, 135))
    if closest > max_wall:
        return None
    center = round(closest_angle * len(scan) / 360)
    near = [d for d in scan[center - 10: center + 11] if 0 < d < closest + 5]
    return sum(near) / len(near)


def right_wall(scan, theta=30):
    """6-10: wall direction (deg) and distance from two rays (90 - theta and 90 degrees)"""
    a = rc_utils.get_lidar_average_distance(scan, 90 - theta)
    b = rc_utils.get_lidar_average_distance(scan, 90)
    if a == 0.0 or b == 0.0:
        return None, None
    t = math.radians(theta)
    alpha = math.atan2(a * math.cos(t) - b, a * math.sin(t))
    return math.degrees(alpha), b * math.cos(alpha)


class P:
    def __init__(self, kp, target=50.0):
        self.kp, self.target = kp, target
    def __call__(self, scan):
        d = right_wall_distance(scan); self.d = d
        return 0.0 if d is None else rc_utils.clamp(self.kp * (d - self.target), -1.0, 1.0)


class PD:
    def __init__(self, kp, kd, rate_frames=10, target=50.0):
        self.kp, self.kd, self.n, self.target = kp, kd, rate_frames, target
        self.errors = []; self.rate = 0.0
    def __call__(self, scan):
        d = right_wall_distance(scan); self.d = d
        if d is None:
            self.errors.clear(); return 0.0
        e = d - self.target
        self.errors.append(e)
        if len(self.errors) > self.n + 1:
            self.errors.pop(0)
        self.rate = 0.0
        if len(self.errors) >= 2:
            self.rate = (self.errors[-1] - self.errors[0]) / ((len(self.errors) - 1) * DT)
        return rc_utils.clamp(self.kp * e + self.kd * self.rate, -1.0, 1.0)


class Angle:
    def __init__(self, kp, ka, theta=30, target=50.0):
        self.kp, self.ka, self.theta, self.target = kp, ka, theta, target
    def __call__(self, scan):
        al, d = right_wall(scan, self.theta); self.d, self.al = d, al
        return 0.0 if d is None else rc_utils.clamp(self.kp * (d - self.target) + self.ka * al, -1.0, 1.0)


def simulate(walls, ctrl, speed, T, x=0.0, y=0.0, heading=90.0, kw=REAL, seed=0, v0=0.0, extra=None):
    """returns rows (t, x, y, heading_deg, angle_cmd, measured distance, wall distance) and crashed"""
    w = sim2d.World(walls, x=x, y=y, heading_deg=heading, seed=seed, **kw)
    w.v = v0
    w.scan()                                    # the LIDAR is read once before start()
    rows = []
    for f in range(int(round(T * 60))):
        scan = w.scan()
        ang = ctrl(scan)
        w.step(DT, speed, ang)
        rows.append((w.t, w.x, w.y, math.degrees(w.psi), ang,
                     np.nan if getattr(ctrl, "d", None) is None else ctrl.d, w.wall_distance())
                    + (tuple(extra(ctrl)) if extra else ()))
        if w.crashed:
            break
    return np.array(rows), w.crashed


class PIA:
    """6-11: distance error (P) + integral of the error (I) + wall direction (like wall_follow_i.py)"""
    def __init__(self, kp, ki, ka, theta=30, target=50.0):
        self.kp, self.ki, self.ka, self.theta, self.target = kp, ki, ka, theta, target
        self.integral = 0.0
    def __call__(self, scan):
        al, d = right_wall(scan, self.theta); self.d, self.al = d, al
        if d is None:
            return 0.0
        e = d - self.target
        self.integral += e * DT
        return rc_utils.clamp(self.kp * e + self.ki * self.integral + self.ka * al, -1.0, 1.0)


def circle(radius, n=360, cx=0.0, cy=0.0):
    """a round wall made of n straight pieces"""
    pts = [(cx + radius * math.cos(2 * math.pi * i / n), cy + radius * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
    return [(x1, y1, x2, y2) for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:])]


def simulate_front_stop(kp, ki, start, T, target=50.0, deadband=0.0, kw=None):
    """6-1 / 6-11: drive straight at a wall and stop TARGET cm before it (stop_at_wall.py, stop_at_wall_pi.py)"""
    w = sim2d.World([(-200, 300, 200, 300)], x=0, y=300 - start, heading_deg=90, speed_deadband=deadband, **(kw or {}))
    w.scan()
    integral = 0.0; rows = []
    for f in range(int(round(T * 60))):
        _, front = rc_utils.get_lidar_closest_point(w.scan(), (350, 10))
        e = front - target
        integral += e * DT
        speed = rc_utils.clamp(kp * e + ki * integral, -1.0, 1.0)
        w.step(DT, speed, 0.0)
        rows.append((w.t, 300 - w.y, speed, ki * integral))
        if w.crashed:
            break
    return np.array(rows), w.crashed


class WallPID:
    """6-12: wall_follow_pid.py -- the book's PID class, with the wall direction given as the rate for D"""
    def __init__(self, pid, theta=30, target=50.0):
        self.pid, self.theta, self.target = pid, theta, target
    def __call__(self, scan):
        al, d = right_wall(scan, self.theta); self.d, self.al = d, al
        if d is None:
            return 0.0
        return self.pid.update(d - self.target, DT, rate=al)


def log_rows(o):
    """rows of wall_log.csv (time, distance, error, angle) as the book's logging programs write them"""
    rows = []; t = 0.0
    for r in o:
        t += DT
        if not np.isnan(r[5]):
            rows.append((float(f"{t:.3f}"), float(f"{r[5]:.2f}"), float(f"{r[5] - 50.0:.2f}"), float(f"{r[4]:.3f}")))
    return rows


def metrics(rows, target=50.0, band=2.5):
    """the same numbers as evaluate_log.py (6-13)"""
    times = [r[0] for r in rows]; dists = [r[1] for r in rows]; angles = [r[3] for r in rows]
    step = dists[0] - target
    ratio = [(d - target) / step for d in dists]
    t90 = next(t for t, r in zip(times, ratio) if r <= 0.9)
    t10 = next((t for t, r in zip(times, ratio) if r <= 0.1), None)
    rise = None if t10 is None else t10 - t90
    overshoot = max(0.0, -min(ratio)) * abs(step)
    outside = [t for t, d in zip(times, dists) if abs(d - target) > band]
    settle = outside[-1] if outside else 0.0
    last = [d - target for t, d in zip(times, dists) if t > times[-1] - 2.0]
    steady = sum(last) / len(last)
    moves = sum(abs(a1 - a0) for a0, a1 in zip(angles[:-1], angles[1:]))
    activity = moves / (times[-1] - times[0])
    return dict(step=step, rise=rise, overshoot=overshoot, settle=settle, steady=steady, activity=activity)


def corridor(points, widths, close_start=True, close_end=False):
    """walls of a corridor along the centre line `points`, with widths[i] for the piece points[i] -> points[i+1].
    Width changes are only allowed where the centre line goes straight on."""
    P = np.asarray(points, float)
    def offset(i, side):                     # side +1: right wall, -1: left wall (seen when driving along the line)
        d = P[i + 1] - P[i]; d = d / np.linalg.norm(d)
        n = np.array([d[1], -d[0]]) * side   # right-hand normal
        h = widths[i] / 2
        return P[i] + n * h, P[i + 1] + n * h
    def meet(a1, a2, b1, b2):
        da, db = a2 - a1, b2 - b1
        den = da[0] * db[1] - da[1] * db[0]
        if abs(den) < 1e-9:
            return None
        t = ((b1[0] - a1[0]) * db[1] - (b1[1] - a1[1]) * db[0]) / den
        return a1 + t * da
    walls = []
    for side in (1, -1):
        pieces = [list(offset(i, side)) for i in range(len(P) - 1)]
        for i in range(len(pieces) - 1):
            a1, a2 = pieces[i]; b1, b2 = pieces[i + 1]
            m = meet(a1, a2, b1, b2)
            if m is None:                    # straight on: a width step
                walls.append((a2[0], a2[1], b1[0], b1[1]))
            else:
                pieces[i][1] = m; pieces[i + 1][0] = m
        walls += [(a[0], a[1], b[0], b[1]) for a, b in pieces]
    if close_start:
        (r1, _), (l1, _) = offset(0, 1), offset(0, -1); walls.append((r1[0], r1[1], l1[0], l1[1]))
    if close_end:
        n = len(P) - 2; (_, r2), (_, l2) = offset(n, 1), offset(n, -1); walls.append((r2[0], r2[1], l2[0], l2[1]))
    return walls


class Ahead:
    """6-15: wall_follow_ahead.py -- right wall with the PID class, plus turning left when a wall comes close in front"""
    def __init__(self, pid, front_limit=200, kf=0.02, target=50.0):
        self.pid, self.flim, self.kf, self.target = pid, front_limit, kf, target
    def __call__(self, scan):
        al, d = right_wall(scan); self.d, self.al = d, al
        _, self.front = rc_utils.get_lidar_closest_point(scan, (350, 10))
        angle = 0.0
        if d is not None:
            angle = self.pid.update(d - self.target, DT, rate=al)
        if self.front < self.flim:
            angle -= self.kf * (self.flim - self.front)
        return rc_utils.clamp(angle, -1.0, 1.0)


import walls_book as _walls


class Center:
    """6-16: wall_follow_center.py -- the middle between the left and right walls"""
    def __init__(self, pid):
        self.pid = pid; self.d = None
    def __call__(self, scan):
        ra, r = _walls.side_wall(scan, "right"); la, l = _walls.side_wall(scan, "left")
        self.d = r
        if r is None or l is None:
            return 0.0
        return self.pid.update((r - l) / 2, DT, rate=(ra - la) / 2)


class States:
    """6-17: wall_follow_states.py -- BOTH / RIGHT / LEFT / NONE with a HOLD-frame switch"""
    NAMES = ("BOTH", "RIGHT", "LEFT", "NONE")
    def __init__(self, pid, hold=10):
        self.pid, self.hold = pid, hold
        self.state = self.candidate = 0; self.count = 0
        self.target_right = self.target_left = 50.0; self.d = None
    @staticmethod
    def seen(r, l):
        return 0 if (r is not None and l is not None) else 1 if r is not None else 2 if l is not None else 3
    def switch(self, r, l):
        s = self.seen(r, l)
        if s == self.state:
            self.count = 0
        else:
            if s == self.candidate:
                self.count += 1
            else:
                self.candidate, self.count = s, 1
            if self.count >= self.hold:
                self.state, self.count = s, 0
                self.pid.reset()
                if s == 1: self.target_right = r
                if s == 2: self.target_left = l
    def steer(self, ra, r, la, l):
        st = self.state
        if st == 0 and r is not None and l is not None:
            return self.pid.update((r - l) / 2, DT, rate=(ra - la) / 2)
        if st == 1 and r is not None:
            return self.pid.update(r - self.target_right, DT, rate=ra)
        if st == 2 and l is not None:
            return self.pid.update(self.target_left - l, DT, rate=-la)
        return 0.0
    def __call__(self, scan):
        ra, r = _walls.side_wall(scan, "right"); la, l = _walls.side_wall(scan, "left")
        self.d = r
        self.switch(r, l)
        return self.steer(ra, r, la, l)


def openings_course():
    """6-17: a 150 cm corridor whose left wall, right wall, or both walls are missing in places"""
    R, L = 75, -75
    W = []
    for y1, y2 in [(-100, 1200), (1500, 1800), (2100, 2600)]: W.append((R, y1, R, y2))
    for y1, y2 in [(-100, 400), (800, 1800), (2100, 2600)]: W.append((L, y1, L, y2))
    W += [(L, 400, -450, 400), (-450, 400, -450, 800), (-450, 800, L, 800)]
    W += [(R, 1200, 450, 1200), (450, 1200, 450, 1500), (450, 1500, R, 1500)]
    W += [(R, 1800, 600, 1800), (600, 1800, 600, 2100), (600, 2100, R, 2100),
          (L, 1800, -600, 1800), (-600, 1800, -600, 2100), (-600, 2100, L, 2100)]
    W.append((L, -100, R, -100))
    return W


class CourseBook(States):
    """6-18: wall_follow_course.py -- 6-17 plus turning toward the open side when a wall comes close in front"""
    def __init__(self, pid, hold=10, front_limit=200, kf=0.02):
        super().__init__(pid, hold)
        self.flim, self.kf = front_limit, kf
        self.turning = False; self.front = 1e6; self.events = []
    @staticmethod
    def open_side(scan):
        r = rc_utils.get_lidar_average_distance(scan, 45, 10)
        l = rc_utils.get_lidar_average_distance(scan, 315, 10)
        if r == 0.0: r = 1000.0
        if l == 0.0: l = 1000.0
        return 1 if r > l else -1
    def __call__(self, scan):
        angle = super().__call__(scan)
        self.front = _walls.front_distance(scan)
        if self.front < self.flim:
            side = self.open_side(scan)
            angle += side * self.kf * (self.flim - self.front)
            if not self.turning:
                self.events.append(side)
            self.turning = True
        else:
            self.turning = False
        return rc_utils.clamp(angle, -1.0, 1.0)


def full_course():
    """6-18 .. 6-20: a 45 degree bend, 90 degree corners both ways, a narrow part (90 cm) and a wide part (300 cm)"""
    pts = [(0, -100), (0, 500), (300, 800), (300, 1100), (-200, 1100), (-200, 1500), (-200, 1800), (-200, 2200), (300, 2200), (300, 2700)]
    widths = [150, 150, 150, 150, 150, 90, 300, 150, 150]
    return corridor(pts, widths), pts


FAST = dict(REAL, vmax=300, grip=500)    # 6-19, 6-20: a car that goes 3 m/s at speed 1.0, with tyres that slide above 5 m/s^2 sideways


class SpeedBook(CourseBook):
    """6-19: wall_follow_speed.py -- speed from the front distance (PID) and steering gains scaled by speed"""
    def __init__(self, max_speed=1.0, min_speed=0.3, front_target=60, kpv=0.005, base=0.5, schedule=True,
                 gains=(0.04, 0.005, 0.04), front_limit=200, kf=0.02):
        from pid_book import PID as _PID
        super().__init__(_PID(*gains, i_zone=20), front_limit=front_limit, kf=kf)
        self.k0 = gains; self.base, self.schedule = base, schedule
        self.front_target = front_target
        self.speed_pid = _PID(kpv, 0.0, 0.0, out_min=min_speed, out_max=max_speed)
        self.speed = min_speed
    def __call__(self, scan):
        if self.schedule:
            f = self.base / max(self.speed, 0.2)
            self.pid.kp, self.pid.ki, self.pid.kd = self.k0[0] * f * f, self.k0[1] * f * f, self.k0[2] * f
        angle = super().__call__(scan)
        self.speed = self.speed_pid.update(self.front - self.front_target, DT)
        return self.speed, angle


class Const:
    """drive at a constant speed with a steering controller"""
    def __init__(self, speed, steer):
        self.speed, self.steer = speed, steer
    def __call__(self, scan):
        return self.speed, self.steer(scan)


def simulate_speed(walls, ctrl, T, x=0.0, y=0.0, heading=90.0, kw=FAST, seed=0):
    """rows (t, x, y, heading, angle, speed_cmd, wall distance, v); the controller returns (speed, angle)"""
    w = sim2d.World(walls, x=x, y=y, heading_deg=heading, seed=seed, **kw)
    w.scan()
    rows = []
    for f in range(int(round(T * 60))):
        speed, angle = ctrl(w.scan())
        w.step(DT, speed, angle)
        rows.append((w.t, w.x, w.y, math.degrees(w.psi), angle, speed, w.wall_distance(), w.v))
        if w.crashed:
            break
    return np.array(rows), w.crashed


def finish_time(o, y_finish=2450.0):
    idx = np.where(o[:, 2] > y_finish)[0]
    return o[idx[0], 0] if len(idx) else None
