"""Figure 2 for 6-8: why P alone keeps swinging (sim2d model).
Left: the path of the P run, with the car's direction drawn where the error is 0.
Right: the error over time with no lag at all, with steering lag only, and with the realistic LIDAR as well."""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import wallsim
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-8"
WALLS = [(100, -200, 100, 4000), (-100, -200, -100, 4000)]

fig = plt.figure(figsize=(10.8, 4.8), dpi=200)
# ---- left: path with the car direction at the zero crossings ----
ax = fig.add_axes([0.06, 0.13, 0.42, 0.72])
o, _ = wallsim.simulate(WALLS, wallsim.P(0.02), 0.3, 15, x=30)
y, dist, head = o[:, 2], 100 - o[:, 1], o[:, 3]
ax.axhspan(-6, 0, color="#CED4DA"); ax.axhline(0, color="#495057", lw=2); ax.text(8, -3, "右の壁", va="center", fontsize=9)
ax.axhline(50, color="#2F9E44", ls="--", lw=1.2)
ax.plot(y, dist, color="#E8590C", lw=2)
e = dist - 50
idx = np.where(np.diff(np.sign(e)) != 0)[0]
for i in idx:
    tilt = head[i] - 90                   # > 0 : pointing left (away from the right wall)
    L = 45
    dx, dy = L * math.cos(math.radians(tilt)), L * math.sin(math.radians(tilt))
    ax.annotate("", xy=(y[i] + dx, dist[i] + dy), xytext=(y[i], dist[i]),
                arrowprops=dict(arrowstyle="-|>", color="#1864AB", lw=2))
    ax.plot([y[i]], [dist[i]], "o", color="#1864AB", ms=5)
    ax.text(y[i] + 6, dist[i] + (10 if tilt > 0 else -13), f"{abs(tilt):.0f}°", fontsize=9, color="#1864AB",
            va="center", bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.5))
    print("zero crossing at", round(o[i, 0], 2), "s, tilt", round(tilt, 1))
ax.text(12, 92, "青い矢印：ずれが 0 になった瞬間の、車の向き", fontsize=9, color="#1864AB")
ax.set_xlim(0, 700); ax.set_ylim(-6, 100); ax.grid(alpha=0.3)
ax.set_xlabel("進んだ距離〔cm〕"); ax.set_ylabel("右の壁までの距離〔cm〕")
ax.set_title("ずれが 0 でも、車はななめを向いている", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
# ---- right: lag makes it grow ----
ax2 = fig.add_axes([0.57, 0.13, 0.41, 0.72])
cases = [("遅れなし（LIDAR もハンドルもすぐ反応）", wallsim.NO_LAG, "#2F9E44"),
         ("ハンドルの遅れだけ", wallsim.IDEAL, "#1C7ED6"),
         ("ハンドルの遅れ ＋ LIDAR の遅れとノイズ", wallsim.REAL, "#E8590C")]
for lab, kw, col in cases:
    oo, crashed = wallsim.simulate(WALLS, wallsim.P(0.02), 0.3, 20, x=30, kw=kw)
    ee = (100 - oo[:, 1]) - 50
    ax2.plot(oo[:, 0], ee, color=col, lw=1.8, label=lab)
    peaks = [np.abs(ee[(oo[:, 0] >= a) & (oo[:, 0] < a + 5)]).max() for a in (0, 5, 10, 15)]
    print(lab, "crashed" if crashed else "", [round(p, 1) for p in peaks])
ax2.axhline(0, color="#868E96", lw=1, ls="--")
ax2.set_xlim(0, 20); ax2.set_ylim(-45, 45); ax2.grid(alpha=0.3)
ax2.set_xlabel("時間〔秒〕"); ax2.set_ylabel("ずれ（距離 − 50）〔cm〕")
ax2.legend(fontsize=8.5, loc="lower left", frameon=True, framealpha=0.9)
ax2.set_title("遅れがあると、揺れはだんだん大きくなる", fontsize=11)
for s in ("top", "right"): ax2.spines[s].set_visible(False)
fig.suptitle("P 制御だけでは揺れが止まらない理由（KP 0.02、speed 0.3、説明用の簡単なモデル）", fontsize=11, y=0.985)
fig.savefig(f"{OUT}/fig2-why.png", facecolor="white"); plt.close(fig)
