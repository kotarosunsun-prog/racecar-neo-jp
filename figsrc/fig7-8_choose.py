"""Figures for 7-8 (sim2d model): which gap and where in it -- gap_follow.py with PICK / AIM on course B."""
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
OUT = "../images/racecar-neo-jp/7-8"
P = C.r._orig
WA, WB = K.corner_course(), K.obstacle_course()
CFG = [("widest", "center", "いちばん広い空き・真ん中", "#E8590C"), ("widest", "farthest", "いちばん広い空き・いちばん遠い点", "#1C7ED6"),
       ("deepest", "center", "いちばん遠くまで見える空き・真ん中", "#2F9E44"), ("deepest", "farthest", "いちばん遠くまで見える空き・いちばん遠い点", "#AE3EC9")]
runs = {}
for pick, aim, lab, col in CFG:
    for cname, W, fy in (("A", WA, 2450), ("B", WB, 2000)):
        res = []
        for seed in range(5):
            L, out, crashed = C.drive("gap_follow.py", W, 60, subs=C.settings(PICK=f'"{pick}"', AIM=f'"{aim}"'), seed=seed)
            fin = np.where(L[:, 2] > fy)[0]; n = fin[0] if len(fin) else len(L)
            res.append((round(L[fin[0], 0], 1) if len(fin) else ("X" if crashed else "-"), round(C.closest_to_walls(W, L, n), 1), L[-1, 1:3].round().tolist()))
            if seed == 0: runs[(pick, aim, cname)] = (L, n, crashed)
        P(pick, aim, cname, res)
# the same scan as 7-7
LB = runs[("widest", "center", "B")][0]; nB = runs[("widest", "center", "B")][1]
for k in range(int(np.argmax(LB[:, 2] > 250)), nB, 10):
    w = sim2d.World(WB, x=LB[k, 1], y=LB[k, 2], heading_deg=math.degrees(LB[k, 3]), **wallsim.REAL); w.scan(); scan = w.scan()
    angles, dists = G.front_view(scan); gaps = G.find_gaps(dists, 150.0)
    if sum(1 for a, b in gaps if b - a >= 40) >= 2:
        break
best = G.widest_gap(gaps); tc = G.gap_center(best, angles); tf = G.gap_farthest(best, angles, dists)
P("center", tc, "farthest", tf)

fig = plt.figure(figsize=(11.4, 6.0), dpi=200)
ax = fig.add_axes([0.06, 0.12, 0.5, 0.74])
ax.plot(angles, dists, color="#495057", lw=1.2); ax.axhline(150, color="#C92A2A", ls="--", lw=1)
ax.axvspan(angles[best[0]] - 0.25, angles[best[1]] + 0.25, color="#FFA94D", alpha=0.45, lw=0)
ax.axvline(tc, color="#E8590C", lw=2); ax.text(tc + 1.5, 60, f"真ん中\n{tc:+.1f}°", fontsize=9, color="#D9480F")
ax.axvline(tf, color="#1C7ED6", lw=2); ax.text(tf - 1.5, 60, f"いちばん遠い点\n{tf:+.1f}°", fontsize=9, color="#1864AB", ha="right")
ax.annotate("遠い点は、手前の物の\nはしのすぐ横にある", xy=(tf, 300), xytext=(-85, 270), fontsize=9, color="#1864AB", arrowprops=dict(arrowstyle="->", color="#1864AB"))
ax.set_xlim(-90, 90); ax.set_ylim(0, 320); ax.grid(alpha=0.3)
ax.set_xlabel("角度〔度〕（左が－、右が＋）"); ax.set_ylabel("距離〔cm〕")
ax.set_title("7-7 と同じ場所で見た正面 ±90°（オレンジがいちばん広い空き）", fontsize=10)
for s in ("top", "right"): ax.spines[s].set_visible(False)
a2 = fig.add_axes([0.6, 0.04, 0.38, 0.84])
C.draw_walls(a2, WB, lw=1.2)
for pick, aim, lab, col in CFG[:3]:
    L, n, crashed = runs[(pick, aim, "B")]
    a2.plot(L[:n, 1], L[:n, 2], color=col, lw=1.6, label=lab + ("\n（ぶつかった）" if crashed else ""))
    if crashed: a2.plot(L[-1, 1], L[-1, 2], "x", color=col, ms=9, mew=2.5)
a2.set_aspect("equal"); a2.axis("off"); a2.set_ylim(-150, 2050); a2.set_xlim(-200, 1350)
a2.legend(fontsize=8, loc="lower right", frameon=True, framealpha=0.95)   # the empty lower right: no path there
a2.set_title("コース B の道すじ", fontsize=10)
fig.suptitle("どの空きの、どこを狙うか（説明用の簡単なモデル）", fontsize=11)
fig.savefig(f"{OUT}/fig1-choose.png", facecolor="white"); plt.close(fig)
