"""Figure for 7-12 (sim2d model): the wall follower of 6-18 and the gap follower on four kinds of course (speed 0.5)."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch7"))
import ch7run as C
import courses7 as K
import wallsim
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/7-12"
os.makedirs(OUT, exist_ok=True)
P = C.r._orig
COURSES = [("A", "A：曲がり角", K.corner_course(), 2450), ("B", "B：箱のある通路", K.obstacle_course(), 2000),
           ("O", "O：横に入り口のある通路", wallsim.openings_course(), 2400), ("C", "C：柱の並ぶ広間", K.posts_hall(3), 2100)]
PROGS = [("wall", "壁沿い走行（6-18）", "wall_only.py", [], "#1C7ED6"),
         ("gap", "Gap Follower（7-10 の設定、speed 0.5）", "gap_follow.py", C.settings("final", MIN_SPEED="0.5", MAX_SPEED="0.5"), "#E8590C")]
runs = {}
for key, lab, prog, subs, col in PROGS:
    for cname, title, W, fy in COURSES:
        res = []
        for seed in range(5):
            L, out, crashed = C.drive(prog, W, 70, subs=subs, seed=seed)
            fin = np.where(L[:, 2] > fy)[0]; n = fin[0] if len(fin) else len(L)
            res.append((round(float(L[fin[0], 0]), 1) if len(fin) else ("X" if crashed else "-"), round(C.closest_to_walls(W, L, n), 1),
                        L[n - 1, 1:3].round().tolist()))
            if seed == 0: runs[(key, cname)] = (L, n, crashed)
        P(key, cname, res, flush=True)

fig, axes = plt.subplots(1, 4, figsize=(12.0, 7.0), dpi=200)
for ax, (cname, title, W, fy) in zip(axes, COURSES):
    C.draw_walls(ax, W, lw=1.2)
    for key, lab, prog, subs, col in PROGS:
        L, n, crashed = runs[(key, cname)]
        ax.plot(L[:n, 1], L[:n, 2], color=col, lw=1.6, label=lab)
        if crashed: ax.plot(L[n - 1, 1], L[n - 1, 2], "x", color=col, ms=9, mew=2.5)
    ax.axhline(fy, color="#2F9E44", ls=":", lw=1.2)
    ax.plot([0], [0], "o", color="#212529", ms=4)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_ylim(-150, 2650)
    ax.set_title(title, fontsize=10)
axes[0].text(-40, 2480, "ゴール", fontsize=8.5, color="#2F9E44", ha="right")
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=2, fontsize=9.5, frameon=False)
fig.suptitle("壁沿い走行と Gap Follower を、4つのコースでくらべる（ばつはぶつかった所、説明用の簡単なモデル）", fontsize=11)
fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.07, wspace=0.05)
fig.savefig(f"{OUT}/fig1-compare.png", facecolor="white"); plt.close(fig)
