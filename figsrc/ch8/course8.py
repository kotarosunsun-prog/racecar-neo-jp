"""The book's own grand-prix course for chapter 8 (sim2d model, cm), and a camera that sees both the floor line and AR markers.
Sections: a line on an open floor -> a corridor with two corners -> a T junction with marker 1 (turn right)
-> a hall with boxes, closed at the top with marker 3 on the end wall (finish)."""
import math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import sim2d
sys.path.insert(0, HERE)


def box(cx, cy, w, h):
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    return [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]


def arc(pts, cx, cy, r, a0, a1, step=3):
    s = step if a1 > a0 else -step
    for a in np.arange(a0, a1 + s * 0.01, s)[1:]:
        pts.append((cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))))


def gp_line():
    """the tape line of section 1: north, a right curve, a left curve, north into the corridor"""
    pts = [(0.0, 0.0), (0.0, 200.0)]
    arc(pts, 150, 200, 150, 180, 90)          # right turn -> heading east at (150, 350)
    arc(pts, 150, 500, 150, 270, 360)         # left turn  -> heading north at (300, 500)
    pts.append((300.0, 950.0))
    return pts


# boxes in the hall (section 4)
BOXES = [(300, 2950, 40, 40), (170, 3250, 40, 40), (440, 3300, 40, 40), (300, 3600, 40, 40)]


def gp_walls():
    W = []
    # section 1: an open floor 1000 x 950 with the corridor mouth at the top
    W += [(-300, -150, 700, -150), (-300, -150, -300, 800), (700, -150, 700, 800),
          (-300, 800, 225, 800), (375, 800, 700, 800)]
    # section 2: corridor north (x 225..375), west (y 1425..1575), north (x -375..-225)
    W += [(225, 800, 225, 1425), (375, 800, 375, 1575),
          (225, 1425, -375, 1425), (375, 1575, -225, 1575),
          (-375, 1425, -375, 2175), (-225, 1575, -225, 2175)]
    # section 3: the T junction (y 2175..2325): a dead end to the west, the way on to the east, then north
    W += [(-375, 2175, -700, 2175), (-700, 2175, -700, 2325), (-700, 2325, 225, 2325),
          (-225, 2175, 375, 2175), (375, 2175, 375, 2600), (225, 2325, 225, 2600)]
    # section 4: a hall 600 wide (x 0..600, y 2600..4700) with boxes, closed at the top; marker 3 is on the end wall
    W += [(0, 2600, 225, 2600), (375, 2600, 600, 2600), (0, 2600, 0, 4700), (600, 2600, 600, 4700),
          (0, 4700, 600, 4700)]
    for b in BOXES:
        W += box(*b)
    return W


LINE_BGR = (205, 120, 40)                           # the blue line (inside the Lab E / Lab F template's BLUE range)
MARKERS = [(-300, 2325, 1, 20, (255, 255, 255)),   # at the T junction: 1 = turn right (the book's rule)
           (300, 4700, 3, 20, (255, 255, 255))]    # on the end wall: 3 = finish (the book's rule)
FINISH_Y = 4000                                     # past this line (after the boxes) the run may end once the car stands still


class GPCamera:
    """floor camera (the line) + AR markers pasted above the horizon (illustrative: no occlusion, markers face the car).
    The floor is looked up in a top-down picture of the line (1 cm per pixel), drawn once."""
    def __init__(self, line=None, markers=MARKERS, width=5):
        import cv2 as cv
        self.floor = sim2d.FloorCamera()
        self.mark = sim2d.MarkerCamera(markers)
        pts = np.asarray(gp_line() if line is None else line, float)
        self.x0, self.y0 = pts[:, 0].min() - 20, pts[:, 1].min() - 20
        w = int(pts[:, 0].max() - self.x0 + 20); h = int(pts[:, 1].max() - self.y0 + 20)
        self.tex = np.zeros((h, w), np.uint8)
        q = np.round((pts - [self.x0, self.y0]) * 4).astype(np.int32)          # 1/4 cm sub-pixel precision
        cv.polylines(self.tex, [q.reshape(-1, 1, 2)], False, 255, thickness=width, lineType=cv.LINE_8, shift=2)
        self.frame, self.img = -1, None

    def render(self, world, frame, rng=None):
        if frame == self.frame:
            return self.img
        img = np.empty((480, 640, 3), np.uint8); img[:] = 185; img[300:] = 150
        F = self.floor
        c, s_ = np.cos(world.psi), np.sin(world.psi)
        gx = world.x + F.forward * c + F.right * s_ - self.x0
        gy = world.y + F.forward * s_ - F.right * c - self.y0
        ix, iy = gx.astype(np.int32), gy.astype(np.int32)
        ok = (gx >= 0) & (gy >= 0) & (ix < self.tex.shape[1]) & (iy < self.tex.shape[0])
        on = np.zeros(gx.shape, bool)
        on[ok] = self.tex[iy[ok], ix[ok]] > 0
        img[F.first_row:][on] = LINE_BGR
        m = self.mark.render(world)                 # grey background 160 above row 300
        top = m[:300]
        keep = np.any(top != 160, axis=2)
        img[:300][keep] = top[keep]
        if rng is not None:
            img = np.clip(img + rng.standard_normal(img.shape, dtype=np.float32) * 2, 0, 255).astype(np.uint8)
        self.frame, self.img = frame, img
        return img
