"""Figure for 6-12: starting 150 cm from the wall (target 50 cm), the integral winds up (sim2d model, realistic LIDAR)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import wallsim
from pid_book import PID
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-12"
WALLS = [(100, -200, 100, 6000), (-100, -200, -100, 6000)]
runs = [("ためすぎを防がない（6-11 のまま）", lambda: wallsim.PIA(0.02, 0.005, 0.04), "#868E96", lambda c: c.ki * c.integral),
        ("命令がいっぱいのときは、ためない", lambda: wallsim.WallPID(PID(0.02, 0.005, 0.04)), "#1C7ED6", lambda c: c.pid.ki * c.pid.integral),
        ("＋ ずれが 20 cm より大きいときも、ためない", lambda: wallsim.WallPID(PID(0.02, 0.005, 0.04, i_zone=20)), "#E8590C", lambda c: c.pid.ki * c.pid.integral)]
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10.4, 6.4), dpi=200, sharex=True, gridspec_kw=dict(height_ratios=[1.6, 1]))
for lab, make, col, ipart in runs:
    ctrl = make()
    o, crashed = wallsim.simulate(WALLS, ctrl, 0.5, 15, x=-50, extra=lambda c, f=ipart: (f(c),))
    d = 100 - o[:, 1]
    a1.plot(o[:, 0], d, color=col, lw=2, label=lab)
    a2.plot(o[:, 0], o[:, 7], color=col, lw=2)
    print(lab, "crashed" if crashed else "", f"closest {d.min():.1f} final {d[-120:].mean():.1f} max I part {o[:, 7].max():.3f}")
a1.axhline(50, color="#2F9E44", ls="--", lw=1.2); a1.text(14.9, 51, "目標 50 cm", color="#2B8A3E", fontsize=9, ha="right", va="bottom")
a1.axhspan(0, 12, color="#FFE3E3"); a1.text(14.9, 6, "ここまで近づくと壁にぶつかる（車の中心から 12 cm）", fontsize=8.5, color="#C92A2A", ha="right", va="center")
a1.set_ylim(0, 160); a1.set_ylabel("壁までの本当の距離〔cm〕"); a1.grid(alpha=0.3)
a1.legend(fontsize=9, loc="upper right", frameon=True, framealpha=0.9)
a1.set_title("壁から 150 cm の所から走り出す（KP 0.02、KI 0.005、壁の向き 0.04、speed 0.5）", fontsize=10.5, loc="left")
a2.axhline(0, color="#868E96", lw=1)
a2.set_ylabel("I の部分"); a2.set_xlabel("時間〔秒〕"); a2.grid(alpha=0.3); a2.set_xlim(0, 15)
a2.set_title("I の部分（KI × ずれの積分）", fontsize=10.5, loc="left")
for a in (a1, a2):
    for s in ("top", "right"): a.spines[s].set_visible(False)
fig.suptitle("積分の暴走と、その防ぎ方（説明用の簡単なモデル）", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-windup.png", facecolor="white"); plt.close(fig)

# round room: the protection must not stop I from doing its job
R = 250
o, crashed = wallsim.simulate(wallsim.circle(R), wallsim.WallPID(PID(0.02, 0.005, 0.04, i_zone=20)), 0.5, 20, x=R - 50)
d = R - np.hypot(o[:, 1], o[:, 2]); print(f"round room with i_zone 20: final {d[-120:].mean():.1f}")
for z in (5, 10):
    o, crashed = wallsim.simulate(wallsim.circle(R), wallsim.WallPID(PID(0.02, 0.005, 0.04, i_zone=z)), 0.5, 20, x=R - 50)
    d = R - np.hypot(o[:, 1], o[:, 2]); print(f"round room with i_zone {z}: final {d[-120:].mean():.1f}")
# stop at the wall (friction), from 300 cm, with the PID class
import sim2d
for lab, pid in [("6-11 program", None), ("PID class", PID(0.02, 0.01, 0.0))]:
    if pid is None:
        o, crashed = wallsim.simulate_front_stop(0.02, 0.01, 300, 10, deadband=0.15)
        print(lab, "crashed" if crashed else f"final {o[-1, 1]:.1f}", f"closest {o[:, 1].min():.1f}")
        continue
    w = sim2d.World([(-200, 300, 200, 300)], x=0, y=0, heading_deg=90, speed_deadband=0.15); w.scan()
    for f in range(600):
        _, front = wallsim.rc_utils.get_lidar_closest_point(w.scan(), (350, 10))
        w.step(wallsim.DT, pid.update(front - 50, wallsim.DT), 0.0)
        if w.crashed: break
    L = np.array(w.log); print(lab, "crashed" if w.crashed else f"final {300 - L[-1, 2]:.1f}", f"closest {(300 - L[:, 2]).min():.1f}")
