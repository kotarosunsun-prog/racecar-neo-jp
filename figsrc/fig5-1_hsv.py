"""Figures for 5-1: (1) OpenCV hue scale with S/V square, (2) BGR vs HSV masks on a synthetic scene."""
import cv2 as cv, numpy as np, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f or "NotoSansCJK-Bold" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/5-1"; os.makedirs(OUT, exist_ok=True)

# ---------- fig2: hue bar (OpenCV H 0..179) and S-V square for H=110 ----------
H = np.tile(np.arange(180, dtype=np.uint8), (24, 1))
bar = cv.cvtColor(np.dstack([H, np.full_like(H, 255), np.full_like(H, 255)]), cv.COLOR_HSV2RGB)
s = np.linspace(0, 255, 160).astype(np.uint8); v = np.linspace(255, 0, 160).astype(np.uint8)
S, V = np.meshgrid(s, v)
sq = cv.cvtColor(np.dstack([np.full_like(S, 110), S, V]), cv.COLOR_HSV2RGB)
fig = plt.figure(figsize=(8.4, 5.0), dpi=200)
ax1 = fig.add_axes([0.06, 0.60, 0.9, 0.18])
ax1.imshow(bar, aspect="auto", extent=[0, 180, 0, 1]); ax1.set_yticks([])
ax1.set_xticks([0, 15, 30, 60, 90, 120, 150, 179])
fig.text(0.06, 0.93, "H（色合い）：OpenCV では 0〜179。角度 0〜360° を半分にした値", fontsize=11)
for x, name in [(0, "赤"), (16, "だいだい"), (30, "黄"), (60, "緑"), (90, "水色"), (120, "青"), (150, "紫"), (176, "赤")]:
    ax1.text(x + (3 if x == 0 else (-3 if x == 176 else 0)), 1.12, name, ha="center", va="bottom", fontsize=9, transform=ax1.transData)
ax1.set_xlim(0, 180)
ax2 = fig.add_axes([0.08, 0.10, 0.28, 0.36])
ax2.imshow(sq, extent=[0, 255, 0, 255]); ax2.set_xlabel("S（あざやかさ）", fontsize=9); ax2.set_ylabel("V（明るさ）", fontsize=9)
ax2.set_xticks([0, 255]); ax2.set_yticks([0, 255]); ax2.tick_params(labelsize=8)
ax2.set_title("H = 110 のときの S と V", fontsize=10, loc="left")
fig.text(0.42, 0.40, "・S が小さいほど、白や灰色に近づく", fontsize=10)
fig.text(0.42, 0.31, "・V が小さいほど、黒に近づく（暗い・影）", fontsize=10)
fig.text(0.42, 0.22, "・影になっても H はほとんど変わらない", fontsize=10)
fig.text(0.42, 0.13, "・赤は 0 の近くと 179 の近くの両方にある", fontsize=10)
fig.savefig(f"{OUT}/fig2-hsv.png", facecolor="white"); plt.close(fig)

# ---------- synthetic scene ----------
def scene():
    img = np.zeros((480, 640, 3), np.uint8)
    for r in range(480):   # wall / floor gradient
        g = 200 - int(r * 0.12) if r < 230 else 150 - int((r - 230) * 0.25)
        img[r, :] = (g, g, g)
    # blue cube: front face lit, side face in shadow (same hue, lower value)
    cv.fillPoly(img, [np.array([[180, 170], [300, 170], [300, 300], [180, 300]])], (205, 120, 40))
    cv.fillPoly(img, [np.array([[300, 170], [345, 150], [345, 275], [300, 300]])], (100, 58, 19))
    cv.fillPoly(img, [np.array([[180, 170], [225, 150], [345, 150], [300, 170]])], (235, 160, 80))
    # orange cube
    cv.fillPoly(img, [np.array([[430, 210], [510, 210], [510, 295], [430, 295]])], (30, 120, 240))
    cv.fillPoly(img, [np.array([[510, 210], [540, 196], [540, 280], [510, 295]])], (15, 60, 125))
    rng = np.random.default_rng(1)
    return np.clip(img.astype(np.int16) + rng.normal(0, 3, img.shape), 0, 255).astype(np.uint8)
img = scene(); cv.imwrite("scene_5-1.png", img)
bgr_mask = ((img[:, :, 0] > 150) & (img[:, :, 1] < 150) & (img[:, :, 2] < 100)).astype(np.uint8) * 255
hsv_mask = cv.inRange(cv.cvtColor(img, cv.COLOR_BGR2HSV), (90, 50, 50), (120, 255, 255))
fig, axs = plt.subplots(1, 3, figsize=(10, 3.3), dpi=200)
for ax, im, t in [(axs[0], cv.cvtColor(img, cv.COLOR_BGR2RGB), "元の画像（青と だいだいの箱）"),
                  (axs[1], bgr_mask, "BGR で「青っぽい」を選ぶ\nB>150, G<150, R<100"),
                  (axs[2], hsv_mask, "HSV で青を選ぶ\n(90, 50, 50)〜(120, 255, 255)")]:
    ax.imshow(im, cmap="gray", vmin=0, vmax=255); ax.set_title(t, fontsize=10); ax.set_xticks([]); ax.set_yticks([])
fig.tight_layout(); fig.savefig(f"{OUT}/fig3-mask.png", facecolor="white"); plt.close(fig)
print("blue lit", cv.cvtColor(np.uint8([[[205, 120, 40]]]), cv.COLOR_BGR2HSV)[0, 0],
      "blue shade", cv.cvtColor(np.uint8([[[100, 58, 19]]]), cv.COLOR_BGR2HSV)[0, 0],
      "orange", cv.cvtColor(np.uint8([[[30, 120, 240]]]), cv.COLOR_BGR2HSV)[0, 0])
print("bgr mask px", int(bgr_mask.sum() / 255), "hsv mask px", int(hsv_mask.sum() / 255))
