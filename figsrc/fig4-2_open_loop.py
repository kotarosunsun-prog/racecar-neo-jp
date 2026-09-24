"""Illustrative model (NOT the RACECAR simulator): the same open-loop 'square' command queue
driven 20 times with small random differences in frame timing, motor strength and steering offset."""
import math, random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"

L, MAX_STEER, VMAX, TAU = 0.30, math.radians(20), 2.0, 0.35   # wheelbase [m], steer [rad], top speed [m/s], lag [s]

def square_queue(turn_time):
    q = []
    for _ in range(4):
        q.append([1.5, 0.5, 0.0])        # straight
        q.append([turn_time, 0.5, 1.0])  # turn right
    q.append([0.8, 0.0, 0.0])            # coast to stop
    return q

def drive(queue, rng=None):
    x = y = th = v = 0.0; th = math.pi / 2          # start at origin, facing up
    gain = 1.0 if rng is None else rng.gauss(1.0, 0.05)
    bias = 0.0 if rng is None else math.radians(rng.gauss(0, 0.7))
    q = [s[:] for s in queue]; path = [(x, y)]
    while q:
        dt = 1 / 60 if rng is None else max(0.008, rng.gauss(1 / 60, 0.004))
        _, speed, angle = q[0]
        q[0][0] -= dt
        if q[0][0] <= 0: q.pop(0)
        v += (VMAX * gain * speed - v) / TAU * dt
        delta = angle * MAX_STEER + bias
        th -= v / L * math.tan(delta) * dt       # right turn = clockwise
        x += v * math.cos(th) * dt; y += v * math.sin(th) * dt
        path.append((x, y))
    return path

# choose the turn time that closes the square in the noiseless model
best = min((abs(math.hypot(*drive(square_queue(t))[-1])), t) for t in [1.0 + 0.005 * k for k in range(120)])
TURN = best[1]
nominal = drive(square_queue(TURN))
rng = random.Random(7)
runs = [drive(square_queue(TURN), rng) for _ in range(20)]
ends = [r[-1] for r in runs]
spread = max(math.hypot(e[0] - nominal[-1][0], e[1] - nominal[-1][1]) for e in ends)

fig, ax = plt.subplots(figsize=(7.2, 5.6), dpi=200)
for r in runs:
    ax.plot([p[0] for p in r], [p[1] for p in r], color="#1C7ED6", alpha=0.35, lw=1.2)
ax.plot([p[0] for p in nominal], [p[1] for p in nominal], color="#212529", lw=2.4, label="ずれのない理想の走り")
ax.scatter([e[0] for e in ends], [e[1] for e in ends], color="#E8590C", s=22, zorder=5, label="20回それぞれのゴール")
ax.scatter([0], [0], color="#2F9E44", s=70, marker="s", zorder=6, label="スタート")
ax.set_aspect("equal"); ax.grid(alpha=0.3)
ax.set_xlabel("横の位置〔m〕"); ax.set_ylabel("縦の位置〔m〕")
ax.set_title("同じ命令の列で20回走らせたときの道すじ（説明用のモデル）", fontsize=12)
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=9, frameon=False)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig("../images/racecar-neo-jp/4-2/fig1-open-loop.png", facecolor="white")
print(f"turn time={TURN:.3f}s  nominal end=({nominal[-1][0]:.3f},{nominal[-1][1]:.3f})  max end spread from nominal={spread:.2f} m")
