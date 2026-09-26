"""Figures for 7-9 (sim2d model): the bubble around the nearest point (BUBBLE in gap_follow.py)."""
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
OUT = "../images/racecar-neo-jp/7-9"
P = C.r._orig
WA, WB = K.corner_course(), K.obstacle_course()
runs = {}
for thr in ("150.0", "100.0"):
    for bub in ("0.0", "20.0"):
        for cname, W, fy in (("A", WA, 2450), ("B", WB, 2000)):
            res = []
            for seed in range(5):
                L, out, crashed = C.drive("gap_follow.py", W, 60, subs=C.settings(THRESHOLD=thr, BUBBLE=bub), seed=seed)
                fin = np.where(L[:, 2] > fy)[0]; n = fin[0] if len(fin) else len(L)
                res.append((round(L[fin[0], 0], 1) if len(fin) else ("X" if crashed else "-"), round(C.closest_to_walls(W, L, n), 1)))
                if seed == 0: runs[(thr, bub, cname)] = (L, n, crashed)
            P(f"THRESHOLD {thr} BUBBLE {bub} course {cname}:", res, flush=True)
# a scan next to the first box (course B, THRESHOLD 100)
L, n, _ = runs[("100.0", "0.0", "B")]
k = int(np.argmin([C.closest_to_walls(WB[-20:], L[i:i + 1], 1) for i in range(n)]))
w = sim2d.World(WB, x=L[k, 1], y=L[k, 2], heading_deg=math.degrees(L[k, 3]), **wallsim.REAL); w.scan(); scan = w.scan()
angles, dists = G.front_view(scan); bub = G.add_bubble(angles, dists, 20.0)
i = int(np.argmin(dists)); P("pose", L[k, 1:3].round(), "nearest", round(float(dists[i]), 1), "at", angles[i], "blocked", round(math.degrees(math.asin(20 / dists[i])), 1))

fig = plt.figure(figsize=(11.4, 6.0), dpi=200)
ax = fig.add_axes([0.06, 0.12, 0.5, 0.74])
ax.plot(angles, dists, color="#495057", lw=1.6, label="そろえた距離")
ax.plot(angles, bub, color="#E8590C", lw=1.6, label="バブルでふさいだあと")
ax.axhline(100, color="#C92A2A", ls="--", lw=1); ax.text(-89, 106, "THRESHOLD 100 cm", fontsize=8.5, color="#C92A2A")
ax.plot(angles[i], dists[i], "o", color="#C92A2A", ms=7); ax.annotate(f"いちばん近い点（{dists[i]:.0f} cm）", xy=(angles[i], dists[i]), xytext=(angles[i] + 12, 30), fontsize=9, color="#C92A2A", arrowprops=dict(arrowstyle="->", color="#C92A2A"))
ax.set_xlim(-90, 90); ax.set_ylim(-5, 320); ax.grid(alpha=0.3)
ax.set_xlabel("角度〔度〕（左が－、右が＋）"); ax.set_ylabel("距離〔cm〕")
ax.legend(fontsize=9, loc="upper center", frameon=True, framealpha=0.95)   # upper left would hide the 300 cm part
ax.set_title("箱のすぐ横で見た正面 ±90°（半径 20 cm のバブル）", fontsize=10)
for s in ("top", "right"): ax.spines[s].set_visible(False)
a2 = fig.add_axes([0.6, 0.04, 0.38, 0.84])
C.draw_walls(a2, WB, lw=1.2)
for bubv, col, lab in (("0.0", "#868E96", "バブルなし"), ("20.0", "#E8590C", "BUBBLE 20")):
    L2, n2, crashed = runs[("100.0", bubv, "B")]
    a2.plot(L2[:n2, 1], L2[:n2, 2], color=col, lw=1.6, label=f"THRESHOLD 100、{lab}\n（壁や箱に {C.closest_to_walls(WB, L2, n2):.0f} cm まで近づいた）")
a2.set_aspect("equal"); a2.axis("off"); a2.set_ylim(-150, 2050); a2.set_xlim(-200, 1350)
a2.legend(fontsize=8, loc="lower right", frameon=True, framealpha=0.95)   # the empty lower right: no path there
a2.set_title("コース B の道すじ", fontsize=10)
fig.suptitle("いちばん近い点のまわりをふさぐ（説明用の簡単なモデル）", fontsize=11)
fig.savefig(f"{OUT}/fig1-bubble.png", facecolor="white"); plt.close(fig)
