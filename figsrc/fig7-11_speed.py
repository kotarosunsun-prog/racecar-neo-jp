"""Figure for 7-11 (sim2d model): speed from how far the chosen direction is open (gap_follow.py, final settings)."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.collections import LineCollection
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch7"))
import ch7run as C
import courses7 as K
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/7-11"
os.makedirs(OUT, exist_ok=True)
P = C.r._orig
WA, WB = K.corner_course(), K.obstacle_course()
CFG = [("一定 0.5", dict(MIN_SPEED="0.5", MAX_SPEED="0.5")), ("一定 0.75", dict(MIN_SPEED="0.75", MAX_SPEED="0.75")),
       ("一定 1.0", dict(MIN_SPEED="1.0", MAX_SPEED="1.0")), ("0.4〜1.0（空き具合で決める）", dict())]
runs = {}
for lab, kw in CFG:
    for cname, W, fy in (("A", WA, 2450), ("B", WB, 2000)):
        res = []
        for seed in range(5):
            L, out, crashed = C.drive("gap_follow.py", W, 60, subs=C.settings("final", **kw), seed=seed)
            fin = np.where(L[:, 2] > fy)[0]; n = fin[0] if len(fin) else len(L)
            res.append((round(float(L[fin[0], 0]), 1) if len(fin) else ("X" if crashed else "-"), round(C.closest_to_walls(W, L, n), 1)))
            if seed == 0: runs[(lab, cname)] = (L, n, crashed, out)
        P(f"{lab} course {cname}:", res, flush=True)
L, n, crashed, out = runs[("0.4〜1.0（空き具合で決める）", "A")]
for f, t in out[:12]:
    P(f"{f / 60:5.1f} 秒 {t}")
P("max speed_cmd", L[:n, 5].max(), "min", L[:n, 5].min(), "max v cm/s", L[:n, 4].max().round(1))

fig = plt.figure(figsize=(11.0, 6.0), dpi=200)
ax = fig.add_axes([0.02, 0.06, 0.36, 0.84])
C.draw_walls(ax, WA, lw=1.4)
pts = L[:n, 1:3]; seg = np.stack([pts[:-1], pts[1:]], axis=1)
lc = LineCollection(seg, cmap="plasma", norm=plt.Normalize(0.4, 1.0), lw=2.6); lc.set_array(L[:n - 1, 5]); ax.add_collection(lc)
cb = fig.colorbar(lc, ax=ax, fraction=0.05, pad=0.02); cb.set_label("speed", fontsize=9)
ax.plot([0], [0], "o", color="#212529", ms=5); ax.text(30, -60, "スタート", fontsize=9)
ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-420, 480); ax.set_ylim(-150, 2550)
ax.set_title("コース A の道すじ（色が speed）", fontsize=10.5)
a2 = fig.add_axes([0.5, 0.14, 0.47, 0.72])
for lab, col, ls in (("一定 0.5", "#868E96", "--"), ("0.4〜1.0（空き具合で決める）", "#E8590C", "-")):
    L2, n2, cr, _ = runs[(lab, "A")]
    a2.plot(L2[:n2, 0], L2[:n2, 5], color=col, lw=1.8, ls=ls, label=f"{lab}：{L2[n2 - 1, 0]:.1f} 秒でゴール")
a2.set_xlabel("時間〔秒〕"); a2.set_ylabel("speed"); a2.set_ylim(0, 1.1); a2.set_xlim(0, 50); a2.grid(alpha=0.3)
a2.legend(fontsize=9, loc="lower right", frameon=True, framealpha=0.95)
a2.set_title("コース A での speed の変化", fontsize=10.5)
for s in ("top", "right"): a2.spines[s].set_visible(False)
fig.suptitle("前が空いているほど速く走る（説明用の簡単なモデル）", fontsize=11)
fig.savefig(f"{OUT}/fig1-speed.png", facecolor="white"); plt.close(fig)
