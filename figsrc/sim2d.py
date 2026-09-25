"""
sim2d.py -- a tiny 2-D world for checking the book's examples (illustrative model, NOT the RACECAR simulator).
Units: cm, seconds, radians. World axes: x to the right, y forward (up on the page).
Car heading psi is measured counterclockwise from +x. angle > 0 turns right (like RACECAR).
LIDAR: 720 samples, index 0 = straight ahead, clockwise, cm, 0.0 = no return.
"""
import math
import numpy as np

class World:
    def __init__(self, segments, x=0.0, y=0.0, heading_deg=90.0, *,
                 vmax=150.0, tau_v=0.25, max_steer_deg=20.0, tau_steer=0.08, wheelbase=30.0,
                 lidar_noise=0.5, dropout=0.0, max_range=1000.0, delay_frames=2, radius=12.0, seed=0,
                 lidar_rel_noise=0.0, spin_hz=None, min_range=12.0, speed_deadband=0.0, steer_bias=0.0, grip=None):
        self.seg = np.array(segments, dtype=float).reshape(-1, 4)   # (N, 4): x1, y1, x2, y2
        self.x, self.y, self.psi = x, y, math.radians(heading_deg)
        self.v, self.delta = 0.0, 0.0
        self.vmax, self.tau_v, self.max_steer = vmax, tau_v, math.radians(max_steer_deg)
        self.tau_steer, self.L = tau_steer, wheelbase
        self.noise, self.dropout, self.max_range = lidar_noise, dropout, max_range
        self.rel_noise, self.spin_hz, self.min_range = lidar_rel_noise, spin_hz, min_range
        self._spin_scan, self._spin_cur = None, 0
        self.deadband, self.steer_bias = speed_deadband, steer_bias   # |speed| below the deadband does not move the car
        self.grip = grip       # largest sideways acceleration the tyres can give (cm/s^2); None = no limit
        self.delay, self.radius = delay_frames, radius
        self.rng = np.random.default_rng(seed)
        self.n = 720
        self.phi = np.arange(self.n) * 2 * math.pi / self.n   # clockwise from the front
        self.buffer = []
        self.t = 0.0
        self.log = []                                         # (t, x, y, psi, v, speed_cmd, angle_cmd)
        self.crashed = False

    def _raw_scan(self):
        if len(self.seg) == 0:
            return np.zeros(self.n, np.float32)
        ang = self.psi - self.phi                             # world direction of each ray
        dx, dy = np.cos(ang)[:, None], np.sin(ang)[:, None]
        x1, y1, x2, y2 = [self.seg[:, i][None, :] for i in range(4)]
        ex, ey = x2 - x1, y2 - y1
        den = dx * (-ey) - dy * (-ex)
        with np.errstate(divide="ignore", invalid="ignore"):
            t = ((x1 - self.x) * (-ey) - (y1 - self.y) * (-ex)) / den
            u = (dx * (y1 - self.y) - dy * (x1 - self.x)) / den
        ok = (np.abs(den) > 1e-12) & (t > 0) & (u >= 0) & (u <= 1)
        t = np.where(ok, t, np.inf).min(axis=1)
        t = t + self.rng.normal(0, self.noise, self.n)
        if self.rel_noise > 0:
            t = t * self.rng.normal(1, self.rel_noise, self.n)
        t[(t > self.max_range) | (t < self.min_range) | ~np.isfinite(t)] = 0.0
        if self.dropout > 0:
            t[self.rng.random(self.n) < self.dropout] = 0.0
        return t.astype(np.float32)

    def scan(self, dt=1/60):
        """the scan the program sees now (delayed by a few frames).
        With spin_hz set, the scan is refreshed a slice at a time, like a spinning LIDAR
        (the simulator's LIDAR spins 6 times a second: 720 * 6 samples per second)."""
        if self.spin_hz:
            raw = self._raw_scan()
            if self._spin_scan is None:
                self._spin_scan = raw.copy()
            k = int(round(self.n * self.spin_hz * dt))
            idx = (self._spin_cur + np.arange(k)) % self.n
            self._spin_scan[idx] = raw[idx]
            self._spin_cur = (self._spin_cur + k) % self.n
            self.buffer.append(self._spin_scan.copy())
        else:
            self.buffer.append(self._raw_scan())
        if len(self.buffer) > self.delay + 1:
            self.buffer.pop(0)
        return self.buffer[0].copy()

    def wall_distance(self):
        """shortest distance from the car centre to any wall"""
        if len(self.seg) == 0:
            return float("inf")
        p = np.array([self.x, self.y]); a = self.seg[:, :2]; b = self.seg[:, 2:]
        ab = b - a; tt = np.clip(((p - a) * ab).sum(1) / (ab * ab).sum(1), 0, 1)
        return float(np.min(np.linalg.norm(a + ab * tt[:, None] - p, axis=1)))

    def step(self, dt, speed_cmd, angle_cmd):
        drive = speed_cmd if abs(speed_cmd) >= self.deadband else 0.0          # friction: too small a command does nothing
        self.v += (drive * self.vmax - self.v) / self.tau_v * dt
        target = max(-self.max_steer, min(self.max_steer, (angle_cmd + self.steer_bias) * self.max_steer))
        self.delta += (target - self.delta) / self.tau_steer * dt
        if self.grip is None:
            self.psi -= self.v / self.L * math.tan(self.delta) * dt
        else:                                                    # turning harder than the tyres allow: the car slides wide
            curv = math.tan(self.delta) / self.L
            if abs(self.v) > 1e-6:
                kmax = self.grip / (self.v * self.v)
                curv = max(-kmax, min(kmax, curv))
            self.psi -= self.v * curv * dt
        self.x += self.v * math.cos(self.psi) * dt
        self.y += self.v * math.sin(self.psi) * dt
        self.t += dt
        self.log.append((self.t, self.x, self.y, self.psi, self.v, speed_cmd, angle_cmd))
        if self.wall_distance() < self.radius:
            self.crashed = True

def hallway(length=2000, width=150):
    """straight hallway: left wall at x = -width/2, right wall at x = +width/2"""
    h = width / 2
    return [(-h, -200, -h, length), (h, -200, h, length)]


class FloorCamera:
    """A forward camera looking down at a flat floor with coloured tape lines (illustrative model).
    Only the floor is drawn; everything above the horizon is a plain grey wall."""
    def __init__(self, height=20.0, pitch_deg=20.0, f=466.0, first_row=300):
        self.first_row = first_row
        v, u = np.mgrid[first_row:480, 0:640].astype(float)
        xc, yc = (u - 320) / f, (v - 240) / f
        th = math.radians(pitch_deg)
        down = math.sin(th) + yc * math.cos(th)
        fwd = math.cos(th) - yc * math.sin(th)
        s = height / down
        self.forward, self.right = s * fwd, s * xc          # ground offsets (cm) of each pixel from the camera

    def render(self, world, lines, floor=(150, 150, 150), wall=(185, 185, 185), rng=None, seg_range=None):
        img = np.empty((480, 640, 3), np.uint8); img[:] = wall
        c, s_ = math.cos(world.psi), math.sin(world.psi)
        gx = world.x + self.forward * c + self.right * s_      # right of heading = (sin, -cos)
        gy = world.y + self.forward * s_ - self.right * c
        part = np.empty(gx.shape + (3,), np.uint8); part[:] = floor
        for poly, width, bgr in lines:
            p = np.asarray(poly, float)
            near = np.min(np.hypot(p[:, 0] - world.x, p[:, 1] - world.y)) < 400
            if not near: continue
            dmin = np.full(gx.shape, np.inf)
            for (x1, y1), (x2, y2) in zip(p[:-1], p[1:]):
                ex, ey = x2 - x1, y2 - y1; L2 = ex * ex + ey * ey
                if seg_range is None:        # (the figures of 6-2 use this rule)
                    if min(math.hypot(x1 - world.x, y1 - world.y), math.hypot(x2 - world.x, y2 - world.y)) > 250: continue
                else:                        # faster: skip segments farther than seg_range from the car
                    tc = min(1.0, max(0.0, ((world.x - x1) * ex + (world.y - y1) * ey) / L2))
                    if math.hypot(world.x - (x1 + tc * ex), world.y - (y1 + tc * ey)) > seg_range: continue
                t = np.clip(((gx - x1) * ex + (gy - y1) * ey) / L2, 0, 1)
                dmin = np.minimum(dmin, np.hypot(gx - (x1 + t * ex), gy - (y1 + t * ey)))
            part[dmin < width / 2] = bgr
        img[self.first_row:] = part
        if rng is not None:
            img = np.clip(img.astype(np.int16) + rng.normal(0, 3, img.shape), 0, 255).astype(np.uint8)
        return img


def curve_line(straight=150, radius=150, turn_deg=90, after=200, step_deg=3):
    """a tape line: straight ahead (+y), then an arc turning right, then straight again"""
    pts = [(0.0, 0.0), (0.0, float(straight))]
    cx, cy = radius, straight                       # centre of the right-hand arc
    for a in np.arange(step_deg, turn_deg + 0.1, step_deg):
        th = math.radians(180 - a)
        pts.append((cx + radius * math.cos(th), cy + radius * math.sin(th)))
    th = math.radians(180 - turn_deg); hx, hy = math.sin(math.radians(turn_deg)), math.cos(math.radians(turn_deg))
    x_end, y_end = pts[-1]
    pts.append((x_end + after * hx, y_end + after * hy))
    return pts


class MarkerCamera:
    """Pastes ArUco (6x6) markers into a plain camera image according to where they are
    relative to the car (illustrative: markers always face the car, no perspective)."""
    def __init__(self, markers, f=466.0, fov_deg=69.0):
        import cv2 as cv
        self.cv = cv
        self.f, self.half_fov = f, math.radians(fov_deg / 2)
        D = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_250)
        self.markers = []
        for (x, y, mid, size_cm, frame_bgr) in markers:
            m = cv.cvtColor(cv.aruco.generateImageMarker(D, mid, 120), cv.COLOR_GRAY2BGR)
            q = 24; m = cv.copyMakeBorder(m, q, q, q, q, cv.BORDER_CONSTANT, value=(255, 255, 255))
            fr = 20; m = cv.copyMakeBorder(m, fr, fr, fr, fr, cv.BORDER_CONSTANT, value=frame_bgr)
            self.markers.append((x, y, size_cm * m.shape[0] / 120, m))    # size_cm = size of the black square

    def render(self, world, rng=None):
        cv = self.cv
        img = np.full((480, 640, 3), 160, np.uint8); img[300:] = 135
        for (x, y, total_cm, tex) in self.markers:
            dx, dy = x - world.x, y - world.y
            dist = math.hypot(dx, dy)
            bearing = world.psi - math.atan2(dy, dx)          # > 0 : marker is to the right
            bearing = (bearing + math.pi) % (2 * math.pi) - math.pi
            if abs(bearing) > self.half_fov or dist < 15: continue
            px = int(self.f * total_cm / dist)
            if px < 12 or px > 900: continue
            m = cv.resize(tex, (px, px), interpolation=cv.INTER_AREA)
            cx = int(320 + self.f * math.tan(bearing)); cy = 200
            x0, y0 = cx - px // 2, cy - px // 2
            xs, ys = max(0, x0), max(0, y0); xe, ye = min(640, x0 + px), min(480, y0 + px)
            if xs >= xe or ys >= ye: continue
            img[ys:ye, xs:xe] = m[ys - y0:ye - y0, xs - x0:xe - x0]
        if rng is not None:
            img = np.clip(img.astype(np.int16) + rng.normal(0, 2, img.shape), 0, 255).astype(np.uint8)
        return img


def s_line(R=150.0, step=3):
    """6-21: a tape line with curves both ways -- straight, right 90, left 180, straight, right 180, straight"""
    def arc(pts, cx, cy, a0, a1):
        s = step if a1 > a0 else -step
        for a in np.arange(a0, a1 + s * 0.01, s)[1:]:
            pts.append((cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))))
    pts = [(0.0, 0.0), (0.0, 150.0)]
    arc(pts, R, 150, 180, 90)
    x, y = pts[-1]; arc(pts, x, y + R, -90, 90)
    x, y = pts[-1]; pts.append((x - 150, y))
    x, y = pts[-1]; arc(pts, x, y + R, 270, 90)
    x, y = pts[-1]; pts.append((x + 300, y))
    return pts


def cone_segments(x, y, radius=10.0, n=16):
    """a cone seen by the LIDAR: a small circle of wall segments"""
    pts = [(x + radius * math.cos(2 * math.pi * k / n), y + radius * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]
    return [(x1, y1, x2, y2) for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:])]


class ConeCamera:
    """Draws cones (a trapezoid of one colour) into a plain camera image (illustrative model).
    The camera looks straight ahead from cam_height cm above the floor; the horizon is row 240."""
    def __init__(self, cones, f=466.0, fov_deg=69.0, cam_height=15.0):
        import cv2 as cv
        self.cv = cv
        self.cones = cones                 # (x, y, base radius cm, height cm, bgr)
        self.f, self.half_fov, self.h = f, math.radians(fov_deg / 2), cam_height

    def render(self, world, rng=None):
        cv = self.cv
        img = np.full((480, 640, 3), 170, np.uint8); img[240:] = 140
        for (x, y, r, height, bgr) in self.cones:
            dx, dy = x - world.x, y - world.y
            dist = math.hypot(dx, dy)
            bearing = world.psi - math.atan2(dy, dx)          # > 0 : the cone is to the right
            bearing = (bearing + math.pi) % (2 * math.pi) - math.pi
            if abs(bearing) > self.half_fov + math.atan2(r, max(dist, 1.0)) or dist < r + 1: continue
            z = dist * math.cos(bearing)                       # depth in front of the camera
            if z < 5: continue
            cx = 320 + self.f * math.tan(bearing)
            base = 240 + self.f * self.h / z
            top = 240 + self.f * (self.h - height) / z
            wb, wt = self.f * r / z, self.f * r * 0.25 / z
            poly = np.array([[cx - wb, base], [cx + wb, base], [cx + wt, top], [cx - wt, top]])
            cv.fillPoly(img, [np.round(poly).astype(np.int32)], bgr)
        if rng is not None:
            img = np.clip(img.astype(np.int16) + rng.normal(0, 2, img.shape), 0, 255).astype(np.uint8)
        return img
