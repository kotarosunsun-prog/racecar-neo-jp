"""Figures for 7-10 (sim2d model): extending the near distance at the edges of things (HALF_WIDTH in gap_follow.py)."""
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
OUT = "../images/racecar-neo-jp/7-10"
P = C.r._orig
WA, WB = K.corner_course(), K.obstacle_course()
CFG = [("いちばん遠い点", dict(AIM='"farthest"')), ("いちばん遠い点 ＋ はしをのばす", dict(AIM='"farthest"', HALF_WIDTH="20.0")),
       ("いちばん遠い点 ＋ はしをのばす ＋ バブル", dict(AIM='"farthest"', HALF_WIDTH="20.0", BUBBLE="20.0")),
       ("真ん中", dict()), ("真ん中 ＋ はしをのばす", dict(HALF_WIDTH="20.0")), ("真ん中 ＋ はしをのばす ＋ バブル", dict(HALF_WIDTH="20.0", BUBBLE="20.0"))]
runs = {}
for lab, kw in CFG:
    for cname, W, fy in (("A", WA, 2450), ("B", WB, 2000)):
        res = []
        for seed in range(5):
            L, out, crashed = C.drive("gap_follow.py", W, 60, subs=C.settings(**kw), seed=seed)
            fin = np.where(L[:, 2] > fy)[0]; n = fin[0] if len(fin) else len(L)
            res.append((round(L[fin[0], 0], 1) if len(fin) else ("X" if crashed else "-"), round(C.closest_to_walls(W, L, n), 1)))
            if seed == 0: runs[(lab, cname)] = (L, n, crashed)
        P(f"{lab} course {cname}:", res, flush=True)
# the scan 1 s before the crash at the corner (farthest point, course A)
L, n, crashed = runs[("いちばん遠い点", "A")]; k = len(L) - 60
w = sim2d.World(WA, x=L[k, 1], y=L[k, 2], heading_deg=math.degrees(L[k, 3]), **wallsim.REAL); w.scan(); scan = w.scan()
angles, dists = G.front_view(scan); ext = G.extend_disparities(angles, dists, 20.0, 50.0)
g0 = G.widest_gap(G.find_gaps(dists, 150.0)); t0 = G.gap_farthest(g0, angles, dists)
g1 = G.widest_gap(G.find_gaps(ext, 150.0)); t1 = G.gap_farthest(g1, angles, ext)
j = int(np.argmin(np.abs(angles - t0)))
P("pose", L[k, 1:3].round(), "target without", t0, "with", t1, "near side of the jump", dists[j - 1].round(1), "far side", dists[j].round(1))

fig = plt.figure(figsize=(11.4, 6.0), dpi=200)
ax = fig.add_axes([0.06, 0.12, 0.5, 0.74])
ax.plot(angles, dists, color="#868E96", lw=1.2, label="そろえた距離")
ax.plot(angles, ext, color="#E8590C", lw=1.6, label="はしで、近い距離をのばしたあと")
ax.axvline(t0, color="#868E96", ls="--", lw=1.2); ax.text(t0 - 1, 170, f"のばす前の目標\n{t0:+.1f}°", fontsize=8.5, color="#495057", ha="right")
ax.axvline(t1, color="#E8590C", ls="--", lw=1.2); ax.text(t1 + 1, 12, f"のばしたあとの目標\n{t1:+.1f}°", fontsize=8.5, color="#D9480F", ha="left")
ax.set_xlim(-90, 90); ax.set_ylim(0, 320); ax.grid(alpha=0.3)
ax.set_xlabel("角度〔度〕（左が－、右が＋）"); ax.set_ylabel("距離〔cm〕")
ax.legend(fontsize=9, loc="upper left", frameon=True, framealpha=0.95)
ax.set_title("コース A のななめの通路の出口の手前で見た正面 ±90°（ぶつかる 1 秒前）", fontsize=10)
for s in ("top", "right"): ax.spines[s].set_visible(False)
a2 = fig.add_axes([0.6, 0.1, 0.38, 0.78])
C.draw_walls(a2, WA, lw=1.4)
for lab, col in (("いちばん遠い点", "#868E96"), ("いちばん遠い点 ＋ はしをのばす", "#E8590C")):
    L2, n2, cr = runs[(lab, "A")]
    top = np.where(L2[:n2, 2] > 1300)[0]; m2 = top[0] if len(top) else n2   # up to where it leaves the drawing
    a2.plot(L2[:m2, 1], L2[:m2, 2], color=col, lw=1.8, label=lab + ("（ぶつかった）" if cr else ""))
    if cr: a2.plot(L2[-1, 1], L2[-1, 2], "x", color=col, ms=10, mew=3)
a2.add_patch(plt.Circle((L[k, 1], L[k, 2]), 18, fill=False, ec="#C92A2A", lw=1.5))
a2.set_aspect("equal"); a2.set_xlim(-330, 450); a2.set_ylim(-120, 1300); a2.axis("off")
a2.legend(fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, 0.0), frameon=False, ncol=1)
a2.set_title("コース A の前半の道すじ（赤い丸が左の図の場所）", fontsize=10)
fig.suptitle("距離が急に変わる所で、近い距離を車の幅の分だけのばす（説明用の簡単なモデル）", fontsize=11)
fig.savefig(f"{OUT}/fig1-disparity.png", facecolor="white"); plt.close(fig)
