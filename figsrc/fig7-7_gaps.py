"""Figures for 7-7 (sim2d model): the gaps in one scan, and gap_follow.py (7-7 version) on courses A and B."""
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
OUT = "../images/racecar-neo-jp/7-7"
P = C.r._orig
WA, WB = K.corner_course(), K.obstacle_course()
runs = {}
for cname, W, fy in (("A", WA, 2450), ("B", WB, 2000)):
    L, out, crashed = C.drive("gap_follow_v1.py", W, 60); fin = np.where(L[:, 2] > fy)[0]; n = fin[0] if len(fin) else len(L)
    runs[cname] = (L, n)
    P(cname, "crashed" if crashed else "", "finish", round(L[fin[0], 0], 2) if len(fin) else None, "closest", round(C.closest_to_walls(W, L, n), 1))
    if cname == "B": P("printed:", [t for f, t in out][:4])
# a scan in course B, 1.2 m before the second box
LB, nB = runs["B"]
for k in range(int(np.argmax(LB[:, 2] > 250)), nB, 10):   # from y = 250 cm: the first moment with two wide gaps (both over 20 degrees)
    w = sim2d.World(WB, x=LB[k, 1], y=LB[k, 2], heading_deg=math.degrees(LB[k, 3]), **wallsim.REAL); w.scan(); scan = w.scan()
    angles, dists = G.front_view(scan); gaps = G.find_gaps(dists, 150.0)
    if sum(1 for a, b in gaps if b - a >= 40) >= 2:
        break
best = G.widest_gap(gaps); target = G.gap_center(best, angles)
P("pose", LB[k, 1:3].round(), "gaps", [(angles[a], angles[b]) for a, b in gaps], "target", target)

fig = plt.figure(figsize=(11.4, 6.2), dpi=200)
ax = fig.add_axes([0.06, 0.12, 0.5, 0.76])
ax.plot(angles, dists, color="#495057", lw=1.2)
ax.axhline(150, color="#C92A2A", ls="--", lw=1); ax.text(-89, 156, "THRESHOLD 150 cm", fontsize=8.5, color="#C92A2A")
for a, b in gaps:
    ax.axvspan(angles[a] - 0.25, angles[b] + 0.25, color="#FFD8A8" if (a, b) != best else "#FFA94D", alpha=0.6, lw=0)
ax.axvline(target, color="#E8590C", lw=2); ax.text(target + 1.5, 20, f"目標の向き {target:+.1f}°\n（いちばん広い空きの真ん中）", fontsize=9, color="#D9480F")
ax.set_xlim(-90, 90); ax.set_ylim(0, 320); ax.grid(alpha=0.3)
ax.set_xlabel("角度〔度〕（左が－、右が＋）"); ax.set_ylabel("距離〔cm〕（front_view() でそろえたもの）")
ax.set_title("コース B の途中で見た正面 ±90°（オレンジが空き、濃いのがいちばん広い空き）", fontsize=10)
for s in ("top", "right"): ax.spines[s].set_visible(False)
for j, (cname, W) in enumerate((("A", WA), ("B", WB))):
    a2 = fig.add_axes([0.6 + j * 0.2, 0.03, 0.19, 0.84])
    L, n = runs[cname]; C.draw_walls(a2, W, lw=1.2)
    a2.plot(L[:n, 1], L[:n, 2], color="#E8590C", lw=1.6)
    if cname == "B": a2.add_patch(plt.Circle((LB[k, 1], LB[k, 2]), 25, fill=False, ec="#C92A2A", lw=1.5))
    a2.set_aspect("equal"); a2.axis("off"); a2.set_ylim(-150, 2500 if cname == "A" else 2050)
    a2.set_title(f"コース {cname}", fontsize=10)
fig.suptitle("しきい値より遠くまで見える向きのまとまり（空き）を探し、いちばん広い空きの真ん中へ（説明用の簡単なモデル）", fontsize=10.5)
fig.savefig(f"{OUT}/fig1-gaps.png", facecolor="white"); plt.close(fig)
