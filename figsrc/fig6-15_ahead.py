"""Figure for 6-15: following the right wall into bends where the wall comes round in front of the car
(sim2d model, realistic LIDAR, speed 0.5, PID 0.04 / 0.005 / wall direction 0.04)."""
import math
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
OUT = "../images/racecar-neo-jp/6-15"
s2 = math.sqrt(0.5)
LEFT45 = [(100, -200, 100, 600), (100, 600, 100 - 900 * s2, 600 + 900 * s2), (-100, -200, -100, 500), (-100, 500, -100 - 800 * s2, 500 + 800 * s2)]
LEFT90 = [(100, -200, 100, 700), (100, 700, -900, 700), (-100, -200, -100, 500), (-100, 500, -900, 500)]
cases = [("左へ 45° 曲がる通路", LEFT45, [("正面を見ない", 0, "#868E96"), ("正面を見る（200 cm から）", 200, "#E8590C")], (-500, 200, -60, 1000)),
         ("左へ 90° 曲がる通路", LEFT90, [("正面を見ない", 0, "#868E96"), ("正面を見る（150 cm から）", 150, "#1C7ED6"), ("正面を見る（200 cm から）", 200, "#E8590C")], (-600, 200, -60, 800))]
fig, axes = plt.subplots(1, 2, figsize=(11.0, 6.0), dpi=200)
for ax, (title, W, runs, lim) in zip(axes, cases):
    for x1, y1, x2, y2 in W: ax.plot([x1, x2], [y1, y2], color="#495057", lw=3)
    for lab, flim, col in runs:
        o, crashed = wallsim.simulate(W, wallsim.Ahead(PID(0.04, 0.005, 0.04, i_zone=20), front_limit=flim), 0.5, 16, x=50)
        ax.plot(o[:, 1], o[:, 2], color=col, lw=2.2, label=lab + ("（ぶつかった）" if crashed else ""))
        if crashed: ax.plot([o[-1, 1]], [o[-1, 2]], "x", color=col, ms=11, mew=3)
        print(title, lab, "crashed" if crashed else "", f"closest to a wall {o[:, 6].min():.1f} cm")
    ax.plot([50], [0], "o", color="#212529", ms=5); ax.text(60, 10, "スタート", fontsize=9)
    ax.set_aspect("equal"); ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.grid(alpha=0.25)
    ax.set_xlabel("横〔cm〕"); ax.set_ylabel("縦〔cm〕")
    ax.legend(fontsize=8.5, loc="lower left", frameon=True, framealpha=0.95)
    ax.set_title(title, fontsize=11)
fig.suptitle("右の壁にそって走り、壁が前に回りこんでくる所を曲がる（speed 0.5、説明用の簡単なモデル）", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-bends.png", facecolor="white"); plt.close(fig)
for kf in (0.01,):
    o, crashed = wallsim.simulate(LEFT90, wallsim.Ahead(PID(0.04, 0.005, 0.04, i_zone=20), front_limit=200, kf=kf), 0.5, 16, x=50)
    print("left 90, front 200, KF", kf, "crashed" if crashed else "ok")
