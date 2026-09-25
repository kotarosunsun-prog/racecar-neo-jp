"""Figure for 6-16: the middle of the corridor vs the right wall (sim2d model, realistic LIDAR, speed 0.5)."""
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
OUT = "../images/racecar-neo-jp/6-16"
PTS = [(0, -100), (0, 400), (0, 800), (-300, 1100), (-300, 1500), (-300, 1800), (0, 2100), (0, 2300), (0, 2700)]
WD = [150, 100, 100, 100, 250, 250, 250, 150]
W = wallsim.corridor(PTS, WD)
runs = [("右の壁から 50 cm（6-12 の方法、KP 0.04）", lambda: wallsim.WallPID(PID(0.04, 0.005, 0.04, i_zone=20)), "#868E96"),
        ("左右の真ん中（この回）", lambda: wallsim.Center(PID(0.04, 0.005, 0.04, i_zone=20)), "#E8590C")]
fig, ax = plt.subplots(figsize=(9.2, 8.6), dpi=200)
for x1, y1, x2, y2 in W: ax.plot([x1, x2], [y1, y2], color="#495057", lw=2.6)
P = np.array(PTS); ax.plot(P[:, 0], P[:, 1], color="#2F9E44", lw=1, ls="--", label="通路の真ん中")
for lab, make, col in runs:
    o, crashed = wallsim.simulate(W, make(), 0.5, 36, x=30)
    ax.plot(o[:, 1], o[:, 2], color=col, lw=2, label=lab + ("（ぶつかった）" if crashed else ""))
    if crashed: ax.plot([o[-1, 1]], [o[-1, 2]], "x", color=col, ms=10, mew=3)
    print(lab, "crashed" if crashed else "", f"closest to a wall {o[:, 6].min():.1f} cm, end y {o[-1, 2]:.0f}")
ax.text(60, 560, "幅 100 cm", fontsize=9); ax.text(-150, 1600, "幅 250 cm", fontsize=9); ax.text(90, 150, "幅 150 cm", fontsize=9)
ax.plot([30], [0], "o", color="#212529", ms=5); ax.text(40, -60, "スタート", fontsize=9)
ax.set_aspect("equal"); ax.set_xlim(-520, 320); ax.set_ylim(-120, 2450); ax.grid(alpha=0.25)
ax.set_xlabel("横〔cm〕"); ax.set_ylabel("縦〔cm〕")
ax.legend(fontsize=9, loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False)
ax.set_title("幅や向きが変わる通路を走る（speed 0.5、説明用の簡単なモデル）", fontsize=11, loc="left")
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-center.png", facecolor="white"); plt.close(fig)
