"""Figure for 7-5: farthest_point.py on the 6-18 course crashes into the corner of the 45-degree bend (sim2d model)."""
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch7"))
import ch7run as C
import courses7 as K
import sim2d, wallsim
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/7-5"
P = C.r._orig
W = K.corner_course()
L, out, crashed = C.drive("farthest_point.py", W, 40)
P("crashed", crashed, "at", L[-1, 1:3].round(), "t", round(L[-1, 0], 2), [t for f, t in out][:8])
for seed in range(1, 5):
    L2, o2, c2 = C.drive("farthest_point.py", W, 40, seed=seed); P("seed", seed, "crashed", c2, L2[-1, 1:3].round())
# a snapshot 1 s before the crash: the scan and the farthest point
k = len(L) - 60
w = sim2d.World(W, x=L[k, 1], y=L[k, 2], heading_deg=math.degrees(L[k, 3]), **wallsim.REAL)
w.scan(); scan = w.scan()
i = int(np.argmax(scan)); a = i * 0.5; d = scan[i]
psi = L[k, 3]; wa = psi - math.radians(a)
fx, fy = L[k, 1] + d * math.cos(wa), L[k, 2] + d * math.sin(wa)
P("snapshot at t", round(L[k, 0], 2), "farthest", round(a if a <= 180 else a - 360, 1), "deg", round(d, 1), "cm")
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(10.4, 6.4), dpi=200, gridspec_kw=dict(width_ratios=[1, 1.25]))
C.draw_walls(ax, W)
ax.plot(L[:, 1], L[:, 2], color="#E8590C", lw=2); ax.plot(L[-1, 1], L[-1, 2], "x", color="#C92A2A", ms=11, mew=3)
ax.plot([0], [0], "o", color="#212529", ms=5); ax.text(20, -60, "スタート", fontsize=9)
ax.set_aspect("equal"); ax.set_xlim(-250, 500); ax.set_ylim(-150, 1300); ax.axis("off")
ax.set_title("farthest_point.py の道すじ", fontsize=10.5)
C.draw_walls(ax2, W)
ang = np.radians(np.arange(720) * 0.5); ok = scan > 0
px = L[k, 1] + scan * np.cos(psi - ang); py = L[k, 2] + scan * np.sin(psi - ang)
ax2.scatter(px[ok], py[ok], s=2, color="#868E96")
ax2.plot([L[k, 1], fx], [L[k, 2], fy], color="#C92A2A", lw=1.6)
ax2.plot(fx, fy, "o", color="#C92A2A", ms=7)
ax2.text(fx + 25, fy + 10, f"いちばん遠い点\n（{d:.0f} cm、{a - 360:+.0f}° の向き）", fontsize=9, color="#C92A2A", va="center")
ax2.add_patch(plt.Circle((L[k, 1], L[k, 2]), 12, color="#1C7ED6"))
ax2.plot(L[k:, 1], L[k:, 2], color="#E8590C", lw=2); ax2.plot(L[-1, 1], L[-1, 2], "x", color="#C92A2A", ms=11, mew=3)
ax2.annotate("ここでぶつかる", xy=(L[-1, 1], L[-1, 2]), xytext=(L[-1, 1] + 60, L[-1, 2] + 260), fontsize=9.5, color="#C92A2A",
             arrowprops=dict(arrowstyle="->", color="#C92A2A"))
ax2.set_aspect("equal"); ax2.set_xlim(-200, 560); ax2.set_ylim(-150, 1300); ax2.grid(alpha=0.25)
ax2.set_title("ぶつかる 1 秒前：LIDAR の点と、いちばん遠い点", fontsize=10.5)
fig.suptitle("いちばん遠い点へ向かうと、曲がり角の角にぶつかる（speed 0.5、説明用の簡単なモデル）", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-corner.png", facecolor="white"); plt.close(fig)
