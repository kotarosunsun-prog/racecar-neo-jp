"""Figures for 7-6 (sim2d model): looking behind, and what front_view() does to the scan."""
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch7"))
import ch7run as C
import courses7 as K
import gaps as G
import sim2d, wallsim
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/7-6"
P = C.r._orig
WB = [(-75, -900, -75, 500), (75, -900, 75, 500)]        # a corridor open at both ends: 900 cm behind, 500 cm ahead
res = {}
for prog in ("farthest_point.py", "farthest_front.py"):
    L, out, crashed = C.drive(prog, WB, 8)
    res[prog] = (L, crashed); P(prog, "crashed" if crashed else "", L[-1, 1:3].round(), [t for f, t in out][1:4])
for prog in ("farthest_front.py",):
    for cname, W, fy in (("A", K.corner_course(), 2450), ("B", K.obstacle_course(), 2000)):
        for seed in range(3):
            L, out, crashed = C.drive(prog, W, 60, seed=seed); fin = np.where(L[:, 2] > fy)[0]
            P(prog, cname, seed, "crashed" if crashed else "", L[-1, 1:3].round(), "finish", L[fin[0], 0] if len(fin) else None)
# the scan at the start of course B
w = sim2d.World(K.obstacle_course(), x=0, y=0, heading_deg=90, **wallsim.REAL); w.scan(); scan = w.scan()
angles, dists = G.front_view(scan)
k = int(G.HALF_VIEW / 0.5); raw = scan[np.arange(-k, k + 1) % 720]
P("raw zeros in the front view:", int((raw == 0).sum()), "raw max", raw.max().round(1), "angles with 0:", angles[raw == 0].min(), angles[raw == 0].max())

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.0, 5.2), dpi=200, gridspec_kw=dict(width_ratios=[0.9, 1.4]))
C.draw_walls(ax, WB)
for prog, col, lab in (("farthest_point.py", "#868E96", "720 点すべてを見る（7-5）"), ("farthest_front.py", "#E8590C", "正面 ±90° だけを見る")):
    L, crashed = res[prog]
    ax.plot(L[:, 1], L[:, 2], color=col, lw=2, label=lab + ("（ぶつかった）" if crashed else ""))
    if crashed: ax.plot(L[-1, 1], L[-1, 2], "x", color=col, ms=10, mew=3)
ax.plot([0], [0], "o", color="#212529", ms=5); ax.annotate("スタート（上向き）", xy=(0, 0), xytext=(95, -60), fontsize=9, arrowprops=dict(arrowstyle="-", color="#868E96"))
ax.text(95, -820, "後ろは 900 cm 先まで\n何もない", ha="left", fontsize=9, color="#495057")
ax.set_aspect("equal"); ax.set_xlim(-110, 480); ax.set_ylim(-900, 520); ax.axis("off")
ax.legend(fontsize=8.5, loc="upper left", bbox_to_anchor=(0.2, 0.52), frameon=True, framealpha=0.95)
ax.set_title("後ろのほうが遠い通路", fontsize=10.5)
ax2.scatter(angles[raw > 0], raw[raw > 0], s=5, color="#868E96", label="LIDAR の値そのまま")
ax2.scatter(angles[raw == 0], raw[raw == 0], s=8, color="#C92A2A", marker="x", label="0.0（遠すぎて測れなかった）")
ax2.plot(angles, dists, color="#E8590C", lw=2, label="front_view() でそろえた値")
ax2.axhline(G.MAX_RANGE, color="#E8590C", ls=":", lw=1)
ax2.text(92, G.MAX_RANGE + 15, "MAX_RANGE\n300 cm", fontsize=8.5, color="#D9480F", va="bottom", ha="right")
ax2.set_xlim(-92, 92); ax2.set_ylim(-30, 1050); ax2.grid(alpha=0.3)
ax2.set_xlabel("角度〔度〕（左が－、右が＋）"); ax2.set_ylabel("距離〔cm〕")
ax2.legend(fontsize=8.5, loc="upper left", frameon=True, framealpha=0.95)
ax2.set_title("障害物のある通路（7-7 のコース B）のスタートで見た、正面 ±90°", fontsize=10.5)
for s in ("top", "right"): ax2.spines[s].set_visible(False)
fig.suptitle("見る範囲を決め、遠すぎる値をそろえる（説明用の簡単なモデル）", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-view.png", facecolor="white"); plt.close(fig)
