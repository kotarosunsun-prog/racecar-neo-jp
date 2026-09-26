# Stand-in for the simulator or the real car (chapter 9): the program drives a car in sim2d.World (illustrative model).
# JOY_FN: (frame) -> (x, y) for the left joystick; TRIG_FN: (frame, trigger) -> value; OUT collects the prints.
import struct, enum, builtins
import numpy as np
FPS = 60
DT = struct.unpack("f", struct.pack("f", 1/FPS))[0]
WORLD = None         # sim2d.World
SCRIPT = []          # (name, first_frame, last_frame)
TOTAL = 600
QUIET = False        # suppress the program's prints
STOP_ON_CRASH = True
IMAGE_FN = None
JOY_FN = None
TRIG_FN = None
OUT = []             # (frame, text) of every print
ON_FRAME = None      # called after each frame with the frame number
STOP_FN = None       # () -> True to end the run early (e.g. the car has stopped for good)
class Button(enum.IntEnum):
    A=0; B=1; X=2; Y=3; LB=4; RB=5; LJOY=6; RJOY=7
class Trigger(enum.IntEnum):
    LEFT=0; RIGHT=1
class Joystick(enum.IntEnum):
    LEFT=0; RIGHT=1
def _held(name, f): return any(n == name and s <= f <= e for n, s, e in SCRIPT)
class _Controller:
    Button, Trigger, Joystick = Button, Trigger, Joystick
    frame = 0
    def is_down(self, b): return _held(b.name, self.frame)
    def was_pressed(self, b): return _held(b.name, self.frame) and not _held(b.name, self.frame - 1)
    def was_released(self, b): return (not _held(b.name, self.frame)) and _held(b.name, self.frame - 1)
    def get_trigger(self, t):
        if TRIG_FN is not None: return float(TRIG_FN(self.frame, t))
        return 1.0 if _held("RT" if t == Trigger.RIGHT else "LT", self.frame) else 0.0
    def get_joystick(self, j):
        if JOY_FN is not None and j == Joystick.LEFT:
            return tuple(JOY_FN(self.frame))
        x = (1.0 if _held("RIGHT", self.frame) else 0.0) - (1.0 if _held("LEFT", self.frame) else 0.0)
        return (x, 0.0)
class _Drive:
    speed = angle = 0.0
    def set_speed_angle(self, speed, angle):
        assert -1.0 <= speed <= 1.0, f"speed [{speed}] must be between -1.0 and 1.0 inclusive."
        assert -1.0 <= angle <= 1.0, f"angle [{angle}] must be between -1.0 and 1.0 inclusive."
        self.speed, self.angle = speed, angle
    def stop(self): self.set_speed_angle(0, 0)
    def set_max_speed(self, m=0.25): pass
class _Lidar:
    cache = None
    def get_samples(self): return _Lidar.cache.copy()
    def get_num_samples(self): return len(_Lidar.cache) if _Lidar.cache is not None else 720
PHYS_FN = None       # (frame) -> dict(voltage=, current=, encoder=) ; None = the simulator (all 0.0)
VISION_FN = None     # (frame) -> list of Detection ; None = no detections
HAS_VISION = True    # False = the simulator (the simulator's racecar has no rc.vision)
class _Physics:
    def _get(self, k):
        return 0.0 if PHYS_FN is None else float(PHYS_FN(_frame[0]).get(k, 0.0))
    def get_battery_voltage(self): return self._get("voltage")
    def get_battery_current(self): return self._get("current")
    def get_encoder_speed(self): return self._get("encoder")
    def get_linear_acceleration(self): return np.array([0.0, 0.0, 9.8])
    def get_angular_velocity(self): return np.zeros(3)
class Detection:
    def __init__(self, class_id, score, bbox): self.class_id, self.score, self.bbox = class_id, score, bbox
    def __repr__(self):
        return (f"Detection(class_id={self.class_id!r}, score={self.score:.2f}, "
                f"bbox=({self.bbox[0]:.0f}, {self.bbox[1]:.0f}, {self.bbox[2]:.0f}, {self.bbox[3]:.0f}))")
class _Vision:
    def get_detections(self): return [] if VISION_FN is None else list(VISION_FN(_frame[0]))
TELEMETRY_ROWS = []  # rows recorded through rc.telemetry
class _Telemetry:
    names = None
    def declare_variables(self, *names):
        if _Telemetry.names is None: _Telemetry.names = names
    def record(self, *values):
        assert _Telemetry.names is not None and len(values) == len(_Telemetry.names)
        TELEMETRY_ROWS.append((_frame[0] * DT, *values))
    def visualize(self): pass
class _Camera:
    def get_color_image(self): return None if IMAGE_FN is None else IMAGE_FN(_frame[0]).copy()
    def get_depth_image(self): return None
    def get_width(self): return 640
    def get_height(self): return 480
class _Display:
    def show_color_image(self, image): pass
    def show_lidar(self, *a, **k): pass
class _Racecar:
    def __init__(self):
        self.controller = _Controller(); self.drive = _Drive(); self.lidar = _Lidar()
        self.camera = _Camera(); self.display = _Display()
        self.physics = _Physics(); self.telemetry = _Telemetry()
        if HAS_VISION: self.vision = _Vision()
        self._slow_time = 1.0; self._slow_counter = 0.0; self._us = None
    def get_delta_time(self): return DT
    def set_update_slow_time(self, t=1.0): self._slow_time = t
    def set_start_update(self, start, update, update_slow=None): self._s, self._u, self._us = start, update, update_slow
    def go(self):
        self.set_update_slow_time(); _frame[0] = 0
        if WORLD is not None: _Lidar.cache = WORLD.scan()
        self._s()
        for f in range(1, TOTAL + 1):
            self.controller.frame = f; _frame[0] = f
            if WORLD is not None: _Lidar.cache = WORLD.scan()
            self._u()
            if self._us is not None:
                self._slow_counter -= DT
                if self._slow_counter < 0: self._us(); self._slow_counter = self._slow_time
            if WORLD is not None:
                WORLD.step(DT, self.drive.speed, self.drive.angle)
                if ON_FRAME is not None: ON_FRAME(f)
                if WORLD.crashed and STOP_ON_CRASH:
                    _orig(f"[frame {f:4d}] ** crashed into a wall **"); break
                if STOP_FN is not None and STOP_FN(): break
_frame = [0]
_orig = builtins.print
def _print(*a, **k):
    text = " ".join(str(x) for x in a)
    OUT.append((_frame[0], text))
    if not QUIET: _orig(f"[frame {_frame[0]:4d}]", text)
builtins.print = _print
def create_racecar(): return _Racecar()
