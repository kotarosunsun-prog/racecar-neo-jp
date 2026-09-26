"""8-3: the worked answers of the book's own exercise (a bicycle-type robot), computed here so the page's numbers are checked."""
import math
import sys
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import gaps as G

p = print
# the robot's specification (the book's own numbers)
L, D, VMAX, DMAX = 0.6, 0.16, 3.0, 30.0        # wheelbase (m), wheel diameter (m), top speed (m/s), largest steering angle (deg)
LIDAR_STEP, LIDAR_HZ, IMU_HZ, CAM_FPS, LOOP_HZ = 0.5, 8, 50, 30, 60
r = D / 2
d = math.radians(DMAX)

p("Q1 turning")
R = L / math.tan(d); Rf = L / math.sin(d)
w = VMAX / R
p(f"  R (rear) = {R:.3f} m   R (front) = {Rf:.3f} m")
p(f"  yaw rate = {w:.3f} rad/s = {math.degrees(w):.1f} deg/s")
p(f"  rear wheel = {VMAX / r:.1f} rad/s   front wheel speed = {VMAX / math.cos(d):.3f} m/s = {VMAX / math.cos(d) / r:.1f} rad/s")
p(f"  U-turn: width 2R = {2 * R:.2f} m, time = {math.pi / w:.2f} s")

p("Q2 sensor timing")
pts = int(360 / LIDAR_STEP)
p(f"  points per scan = {pts}, per second = {pts * LIDAR_HZ}")
p(f"  new scan every {1 / LIDAR_HZ:.3f} s = {LOOP_HZ / LIDAR_HZ:.1f} frames; distance per scan at top speed = {VMAX / LIDAR_HZ:.3f} m")
p(f"  frames per camera image = {LOOP_HZ / CAM_FPS:.1f}, per IMU sample = {LOOP_HZ / IMU_HZ:.1f}")

p("Q3 stopping")
A = 3.0                                        # braking deceleration (m/s^2)
delay = 1 / LIDAR_HZ + 1 / LOOP_HZ
for v in (1.5, 3.0):
    p(f"  v={v}: reaction {v * delay:.3f} m + braking {v * v / (2 * A):.3f} m = {v * delay + v * v / (2 * A):.3f} m")

p("Q4 PID step")
kp, ki, kd = 1.2, 0.3, 0.15
e0, e1, dt, I0 = 0.20, 0.17, 1 / LIDAR_HZ, 0.40
I1 = I0 + e1 * dt
P_, I_, D_ = kp * e1, ki * I1, kd * (e1 - e0) / dt
p(f"  P={P_:.4f} integral={I1:.5f} I={I_:.6f} rate={(e1 - e0) / dt:.3f} D={D_:.4f} total={P_ + I_ + D_:.4f}")

p("Q5 complementary filter")
alpha, dti = 0.98, 1 / IMU_HZ
p(f"  tau = {alpha * dti / (1 - alpha):.3f} s")
th = alpha * (10.0 + 5.0 * dti) + (1 - alpha) * 12.0
p(f"  one step: {th:.4f} deg")
p(f"  gyro only, bias 0.2 deg/s for 5 min: {0.2 * 300:.0f} deg")

p("Q6 gaps")
ang = np.arange(-60, 61, 15).astype(float)
dist = np.array([120, 140, 260, 300, 300, 90, 80, 220, 250], float)   # cm
thr = 150.0
gs = G.find_gaps(dist, thr)
p(f"  gaps {[(ang[a], ang[b]) for a, b in gs]}  widest centre {G.gap_center(G.widest_gap(gs), ang)}")
bub = G.add_bubble(ang, dist, 35.0)
i = int(np.argmin(dist))
p(f"  bubble around {ang[i]} ({dist[i]} cm): half angle {math.degrees(math.asin(35 / dist[i])):.1f} -> {bub}")
gs2 = G.find_gaps(bub, thr)
p(f"  gaps {[(ang[a], ang[b]) for a, b in gs2]}  centre {G.gap_center(G.widest_gap(gs2), ang)}")
ext = G.extend_disparities(ang, dist, 35.0, 50.0)
p(f"  disparity: {ext}")
for a, b in ((1, 2), (4, 5), (6, 7)):
    near = min(dist[a], dist[b]); p(f"    jump {ang[a]}..{ang[b]}: near {near}, spread {math.degrees(math.atan2(35, near)):.1f}")
both = G.add_bubble(ang, ext, 35.0)
gs3 = G.find_gaps(both, thr)
p(f"  disparity + bubble: {both}  gaps {[(ang[a], ang[b]) for a, b in gs3]}  centre {G.gap_center(G.widest_gap(gs3), ang)}")

p("Q8 where the time goes")
sections = {"線": 18.0, "通路": 26.0, "交差点": 9.0, "広間": 31.0}
total = sum(sections.values())
p(f"  total {total}")
for k, v in sections.items():
    p(f"  {k}: {v} s ({v / total * 100:.0f} %) ; 20 % faster saves {v * (1 - 1 / 1.2):.1f} s")
