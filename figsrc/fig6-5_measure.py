"""Figure for 6-5: when the car is tilted, the ray at 90 degrees is longer than the true distance;
the closest point in the (45, 135) window stays at the true distance (sim2d model, no noise)."""
import os, sys, math, numpy as np, sim2d
sys.path.insert(0, os.environ.get("RACECAR_LIBRARY", "../../racecar-neo-library/library"))
import racecar_utils as rc_utils
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as mtransforms
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-5"
D = 50.0


def measure(tilt):
    w = sim2d.World([(D, -500, D, 3000)], x=0, y=0, heading_deg=90 - tilt, lidar_noise=0.0, delay_frames=0)
    s = w.scan()
    return rc_utils.get_lidar_average_distance(s, 90), rc_utils.get_lidar_closest_point(s, (45, 135))


fig = plt.figure(figsize=(10.6, 4.9), dpi=200)
# ---- left: geometry at tilt 30 ----
ax = fig.add_axes([0.01, 0.05, 0.42, 0.83])
T = 30; th = math.radians(T)
ax.add_patch(patches.Rectangle((D, -60), 8, 170, fc="#CED4DA", ec="#495057", lw=1.4, hatch="///"))
hx, hy = math.sin(th), math.cos(th)          # heading (tilted right by T)
rx, ry = math.cos(th), -math.sin(th)         # the car's right
for a in np.arange(45, 136, 5):              # the window (45..135 deg from the front, clockwise)
    ar = math.radians(a); dx, dy = hx * math.cos(ar) + rx * math.sin(ar), hy * math.cos(ar) + ry * math.sin(ar)
    if dx > 1e-6:
        t = D / dx
        if t * dy > -60: ax.plot([0, D], [0, t * dy], color="#D0EBFF", lw=1.0, zorder=1)
L90 = D / math.cos(th)
ax.plot([0, rx * L90], [0, ry * L90], color="#E8590C", lw=2.4, zorder=3)
ax.text(-31, -18, f"真横（90°）の\n光線 {L90:.1f} cm", color="#D9480F", fontsize=9.5, va="top",
        bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
ax.plot([0, D], [0, 0], color="#2F9E44", lw=2.4, zorder=3)
ax.text(12, 4, f"いちばん近い点\n{D:.0f} cm（本当の距離）", color="#2B8A3E", fontsize=9, ha="left", va="bottom",
        bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
car = patches.FancyBboxPatch((-6, -12), 12, 24, boxstyle="round,pad=1.2", fc="#1C7ED6", ec="#1864AB", lw=1.3, zorder=4)
car.set_transform(mtransforms.Affine2D().rotate_deg(-T) + ax.transData); ax.add_patch(car)
ax.annotate("", xy=(hx * 40, hy * 40), xytext=(hx * 15, hy * 15), arrowprops=dict(arrowstyle="-|>", color="#1864AB", lw=2), zorder=5)
ax.plot([0, 0], [0, 44], color="#868E96", lw=1, ls=":")
ax.text(-31, 96, f"車が壁のほうへ\n{T}° 傾いている", fontsize=9.5, color="#1864AB", va="top")
ax.text(-31, -44, "うすい青の線：\n調べる窓\n（45°〜135°）", fontsize=8.5, color="#1971C2", va="top")
ax.text(D + 4, 113, "右の壁", ha="center", fontsize=10)
ax.set_xlim(-32, 68); ax.set_ylim(-62, 122); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("傾いた車から右の壁を測る（上から見た図）", fontsize=11)
# ---- right: graph ----
ax2 = fig.add_axes([0.53, 0.14, 0.44, 0.72])
tilts = np.arange(0, 61, 2)
ray = []; cl = []
for t in tilts:
    r, (a, c) = measure(t); ray.append(r); cl.append(c)
ax2.plot(tilts, ray, color="#E8590C", lw=2.2, label="真横（90°）の距離")
ax2.plot(tilts, cl, color="#2F9E44", lw=2.2, label="いちばん近い点（45°〜135°）")
ax2.axhline(D, color="#868E96", ls="--", lw=1); ax2.text(1, D - 1.5, "本当の距離 50 cm", fontsize=9, color="#495057", va="top")
ax2.axvline(45, color="#ADB5BD", lw=1, ls=":")
ax2.text(44, 88, "傾きが 45° をこえると、\nいちばん近い点が\n窓の外に出る", fontsize=8.5, color="#495057", va="top", ha="right")
ax2.set_xlim(0, 60); ax2.set_ylim(40, 105); ax2.grid(alpha=0.3)
ax2.set_xlabel("車の傾き〔度〕"); ax2.set_ylabel("測った距離〔cm〕")
ax2.legend(fontsize=9, loc="upper left", frameon=False)
ax2.set_title("傾きと、測った距離", fontsize=11)
for s_ in ("top", "right"): ax2.spines[s_].set_visible(False)
fig.suptitle("車が傾くと、真横の光線は長くなる（説明用の簡単なモデル、ノイズなし）", fontsize=11, y=0.99)
fig.savefig(f"{OUT}/fig1-tilt.png", facecolor="white"); plt.close(fig)
for t in (0, 10, 20, 30, 40, 50):
    r, (a, c) = measure(t); print(t, round(r, 1), round(c, 1), a)
