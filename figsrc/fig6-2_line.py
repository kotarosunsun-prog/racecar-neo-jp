"""Figures for 6-2: camera view with the floor crop and line centre; top-down paths for three gains (sim2d model)."""
import os, sys, math, numpy as np, cv2 as cv, sim2d
sys.path.insert(0, os.environ.get("RACECAR_LIBRARY", "../../racecar-neo-library/library"))
import racecar_utils as rc_utils
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-2"
BLUE = ((90, 50, 50), (120, 255, 255)); LINE_BGR = (205, 120, 40)
line = sim2d.curve_line()

# ---------- fig1: camera view ----------
w = sim2d.World([], x=-12, y=120, heading_deg=95)
img = sim2d.FloorCamera(first_row=75).render(w, [(line, 5.0, LINE_BGR)], rng=np.random.default_rng(1))
crop = rc_utils.crop(img, (360, 0), (480, 640))
c = rc_utils.get_largest_contour(rc_utils.find_contours(crop, BLUE[0], BLUE[1]), 30)
row, col = rc_utils.get_contour_center(c)
err = (col - 320) / 320
fig, ax = plt.subplots(figsize=(7.4, 5.6), dpi=200)
ax.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB)); ax.set_xticks([0, 160, 320, 480, 639]); ax.set_yticks([0, 120, 240, 360, 479]); ax.tick_params(labelsize=8)
ax.add_patch(patches.Rectangle((0, 360), 639, 119, fill=False, ec="#E8590C", lw=2.4, ls="--"))
ax.text(8, 352, "切りとる部分：行 360〜479（車のすぐ前の床）", color="#D9480F", fontsize=10, va="bottom",
        bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
ax.plot([col], [row + 360], "o", color="#E03131", ms=8)
ax.plot([320, 320], [360, 479], color="white", lw=1.5, ls=":")
ax.annotate("", xy=(col, 420), xytext=(320, 420), arrowprops=dict(arrowstyle="<->", color="#FFD43B", lw=2.2))
ax.text((col + 320) / 2, 445, f"ずれ = ({col} − 320) ÷ 320 = {err:+.2f}", ha="center", fontsize=10, color="#212529",
        bbox=dict(boxstyle="round", fc="white", ec="#ADB5BD"))
ax.text(col + 10, row + 350, f"線の中心の列 {col}", fontsize=9.5, color="#C92A2A", bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
ax.set_title("カメラで見た床の線（説明用の簡単なモデル）", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-camera.png", facecolor="white"); plt.close(fig)
print("center", row, col, "error", round(err, 3))

# ---------- fig2: paths ----------
def run(kp, frames=560):
    w = sim2d.World([], x=8, y=0, heading_deg=90); cam = sim2d.FloorCamera(first_row=360); rng = np.random.default_rng(0)
    angle = 0.0
    for _ in range(frames):
        im = cam.render(w, [(line, 5.0, LINE_BGR)], rng=rng)
        cr = rc_utils.crop(im, (360, 0), (480, 640))
        ct = rc_utils.get_largest_contour(rc_utils.find_contours(cr, BLUE[0], BLUE[1]), 30)
        if ct is not None:
            e = (rc_utils.get_contour_center(ct)[1] - 320) / 320
            angle = max(-1.0, min(1.0, kp * e))
        w.step(1 / 60, 0.5, angle)
        if w.x > 330: break
    L = np.array(w.log); return L[:, 1], L[:, 2]
fig, ax = plt.subplots(figsize=(7.2, 5.6), dpi=200)
p = np.array(line)
ax.plot(p[:, 0], p[:, 1], color="#339AF0", lw=7, alpha=0.35, solid_capstyle="butt", label="床の青い線")
for kp, col in [(0.3, "#F08C00"), (1.0, "#2F9E44"), (3.0, "#AE3EC9")]:
    x, y = run(kp); ax.plot(x, y, color=col, lw=2, label=f"KP = {kp}")
ax.scatter([8], [0], color="#212529", s=30, zorder=5); ax.text(14, -12, "スタート（線の 8 cm 右）", fontsize=9)
ax.set_aspect("equal"); ax.set_xlim(-60, 360); ax.set_ylim(-30, 420); ax.grid(alpha=0.3)
ax.set_xlabel("横〔cm〕"); ax.set_ylabel("縦〔cm〕"); ax.legend(fontsize=9, loc="upper left", frameon=False)
ax.set_title("線をたどった道すじ（speed 0.5、説明用の簡単なモデル）", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-paths.png", facecolor="white"); plt.close(fig)
