"""Figures for 5-11: detection output anatomy, NMS before/after, and a convolution feature map."""
import os, io, contextlib, runpy, cv2 as cv, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/5-11"
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("fig5-11_iou_nms.py")
boxes, scores, nms = g["boxes"], g["scores"], g["nms"]

def cone(img, cx, top, bottom, half):
    pts = np.array([[cx, top], [cx - half, bottom], [cx + half, bottom]])
    cv.fillPoly(img, [pts], (20, 110, 240))
    for frac in (0.45, 0.7):
        y = int(top + (bottom - top) * frac); w = int(half * frac * 0.95)
        cv.rectangle(img, (cx - w, y - 4), (cx + w, y + 4), (235, 235, 235), -1)
    cv.rectangle(img, (cx - half - 6, bottom), (cx + half + 6, bottom + 8), (20, 90, 200), -1)
img = np.zeros((480, 640, 3), np.uint8)
for r in range(480):
    gv = 200 - int(r * 0.1) if r < 250 else 150 - int((r - 250) * 0.25)
    img[r, :] = (gv, gv, gv)
cone(img, 140, 205, 312, 34); cone(img, 425, 236, 292, 18)
cv.rectangle(img, (250, 170), (300, 215), (60, 90, 150), -1)       # a brownish box in the background
rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
cv.imwrite("scene_5-11.png", img)

# ---------- fig1: anatomy ----------
fig, ax = plt.subplots(figsize=(7.6, 5.6), dpi=200)
ax.imshow(rgb); ax.set_xticks([0, 160, 320, 480, 639]); ax.set_yticks([0, 120, 240, 360, 479]); ax.tick_params(labelsize=8)
for i, col, lab in [(0, "#2F9E44", "cone 0.91"), (3, "#2F9E44", "cone 0.77")]:
    x0, y0, x1, y1 = boxes[i]
    ax.add_patch(patches.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=col, lw=2.4))
    ax.text(x0, y0 - 6, lab, color="white", fontsize=10, bbox=dict(fc=col, ec="none", pad=1.5))
x0, y0, x1, y1 = (244, 164, 306, 221)
ax.add_patch(patches.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="#868E96", lw=1.8, ls="--"))
ax.text(x0, y0 - 6, "cone 0.22", color="#495057", fontsize=9, bbox=dict(fc="white", ec="#868E96", pad=1.5))
ax.annotate("自信が低い（しきい値 0.4 より下）\n→ 捨てる", xy=(306, 190), xytext=(330, 120), fontsize=9, color="#495057",
            arrowprops=dict(arrowstyle="->", color="#868E96"))
x0, y0, x1, y1 = boxes[0]; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
ax.plot([cx], [cy], "o", color="#E8590C", ms=7)
ax.annotate(f"中心 (x, y) = ({cx:.0f}, {cy:.0f})\n幅 {x1 - x0}・高さ {y1 - y0}", xy=(cx, cy), xytext=(30, 420), fontsize=10,
            bbox=dict(boxstyle="round", fc="white", ec="#ADB5BD"), arrowprops=dict(arrowstyle="->", color="#E8590C"))
ax.annotate(f"左上 ({x0}, {y0})", xy=(x0, y0), xytext=(20, 140), fontsize=9, arrowprops=dict(arrowstyle="->", color="#495057"))
ax.annotate(f"右下 ({x1}, {y1})", xy=(x1, y1), xytext=(210, 360), fontsize=9, arrowprops=dict(arrowstyle="->", color="#495057"))
ax.set_xlabel("x（左から右、画素）"); ax.set_ylabel("y（上から下、画素）")
ax.set_title("物体検出の答え：名前・自信・枠（説明用に作った画像と値）", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-detections.png", facecolor="white"); plt.close(fig)

# ---------- fig3: NMS before / after ----------
keep = nms(boxes, scores)
fig, axs = plt.subplots(1, 2, figsize=(10, 3.9), dpi=200)
cols = ["#2F9E44", "#F08C00", "#AE3EC9", "#1C7ED6"]
for ax, idx, t in [(axs[0], range(len(boxes)), "NMS の前：同じコーンに枠が3つ"), (axs[1], keep, "NMS の後：1つのコーンに枠1つ")]:
    ax.imshow(rgb[150:360, 60:500]); ax.set_xticks([]); ax.set_yticks([]); ax.set_title(t, fontsize=11)
    for i in idx:
        x0, y0, x1, y1 = boxes[i]
        ax.add_patch(patches.Rectangle((x0 - 60, y0 - 150), x1 - x0, y1 - y0, fill=False, ec=cols[i], lw=2))
        ty = y0 - 150 - 6 if i != 2 else y1 - 150 + 16
        ax.text(x0 - 60 + (0 if i != 1 else 30), ty, f"{scores[i]:.2f}", color="white", fontsize=9, bbox=dict(fc=cols[i], ec="none", pad=1.2))
fig.tight_layout(); fig.savefig(f"{OUT}/fig3-nms.png", facecolor="white"); plt.close(fig)

# ---------- fig4: convolution feature map ----------
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY).astype(np.float32)
k = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32)     # responds to left-right brightness changes
fm_ = cv.filter2D(gray, -1, k)
fig, axs = plt.subplots(1, 3, figsize=(10.4, 3.2), dpi=200, gridspec_kw={"width_ratios": [1, 0.45, 1]})
axs[0].imshow(gray, cmap="gray"); axs[0].set_title("入力（白黒にした画像）", fontsize=10)
axs[1].imshow(k, cmap="coolwarm", vmin=-2, vmax=2)
for (r, c), v in np.ndenumerate(k): axs[1].text(c, r, f"{v:.0f}", ha="center", va="center", fontsize=12)
axs[1].set_title("3×3 のフィルタ", fontsize=10)
axs[2].imshow(np.abs(fm_), cmap="magma", vmin=0, vmax=np.abs(fm_).max() * 0.35); axs[2].set_title("出力（特徴マップ）：縦の境目が光る", fontsize=10)
for ax in axs: ax.set_xticks([]); ax.set_yticks([])
fig.tight_layout(); fig.savefig(f"{OUT}/fig4-convolution.png", facecolor="white"); plt.close(fig)
print("keep", keep)
