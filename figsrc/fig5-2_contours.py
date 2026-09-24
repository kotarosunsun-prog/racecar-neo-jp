"""Figures for 5-2: (1) contours found by racecar_utils on a synthetic scene, (2) apparent area vs distance."""
import sys, os, cv2 as cv, numpy as np
# racecar_utils.py (racecar-neo-library/library) must be importable; set RACECAR_LIBRARY to its folder
sys.path.insert(0, os.environ.get("RACECAR_LIBRARY", "../../racecar-neo-library/library"))
import racecar_utils as rc_utils
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/5-2"; os.makedirs(OUT, exist_ok=True)

def cube(img, x, y, s, lit, shade, top):
    d = int(s * 0.35)
    cv.fillPoly(img, [np.array([[x, y], [x + s, y], [x + s, y + s], [x, y + s]])], lit)
    cv.fillPoly(img, [np.array([[x + s, y], [x + s + d, y - d // 2], [x + s + d, y + s - d // 2], [x + s, y + s]])], shade)
    cv.fillPoly(img, [np.array([[x, y], [x + d, y - d // 2], [x + s + d, y - d // 2], [x + s, y]])], top)

img = np.zeros((480, 640, 3), np.uint8)
for r in range(480):
    g = 200 - int(r * 0.12) if r < 220 else 150 - int((r - 220) * 0.25)
    img[r, :] = (g, g, g)
cube(img, 90, 170, 150, (205, 120, 40), (100, 58, 19), (235, 160, 80))     # near blue light
cube(img, 470, 190, 42, (200, 118, 42), (98, 57, 20), (230, 158, 82))      # far blue light
cv.circle(img, (360, 150), 3, (190, 110, 45), -1)                           # tiny blue speck (noise)
rng = np.random.default_rng(3)
img = np.clip(img.astype(np.int16) + rng.normal(0, 3, img.shape), 0, 255).astype(np.uint8)
cv.imwrite("scene_5-2.png", img)

BLUE = ((90, 50, 50), (120, 255, 255))
contours = rc_utils.find_contours(img, BLUE[0], BLUE[1])
largest = rc_utils.get_largest_contour(contours, 30)
out = img.copy()
info = []
for c in contours:
    a = rc_utils.get_contour_area(c)
    if a < 30: continue
    ctr = rc_utils.get_contour_center(c)
    rc_utils.draw_contour(out, c, rc_utils.ColorBGR.green.value if c is largest else rc_utils.ColorBGR.yellow.value)
    rc_utils.draw_circle(out, ctr, rc_utils.ColorBGR.red.value)
    info.append((ctr, a, c is largest))
print("contours:", len(contours), [(i[0], round(i[1]), i[2]) for i in info])

fig, ax = plt.subplots(figsize=(7.4, 5.0), dpi=200)
ax.imshow(cv.cvtColor(out, cv.COLOR_BGR2RGB)); ax.set_xticks([]); ax.set_yticks([])
for (r, c), a, big in info:
    label = f"中心 ({r}, {c})\n面積 {a:.0f}" + ("\n← いちばん大きい" if big else "")
    ax.annotate(label, xy=(c, r), xytext=(c + (-40 if big else -150), r + (150 if big else 110)), fontsize=10,
                color="#212529", bbox=dict(boxstyle="round", fc="white", ec="#ADB5BD"),
                arrowprops=dict(arrowstyle="->", color="#495057"))
ax.text(360, 128, "小さな点（面積が小さいので\n無視される）", fontsize=9, ha="center", va="bottom",
        bbox=dict(boxstyle="round", fc="white", ec="#ADB5BD", alpha=0.9))
ax.set_title("青の範囲で見つけた輪郭（緑：いちばん大きい、黄：ほかの輪郭）", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-contours.png", facecolor="white"); plt.close(fig)

# ---------- fig2: apparent area vs distance (pinhole model, illustrative) ----------
f_px = 320 / np.tan(np.radians(69 / 2))      # about 466 px for a 69 deg horizontal field of view
W = 0.2                                        # 20 cm cube
d = np.linspace(0.4, 4, 300)
area = (f_px * W / d) ** 2
fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=200)
ax.plot(d, area, color="#1C7ED6", lw=2.4)
for dd in (1, 2):
    a = (f_px * W / dd) ** 2
    ax.plot([dd], [a], "o", color="#E8590C"); ax.annotate(f"{dd} m：約 {a:,.0f}", (dd, a), xytext=((1.3, 27000) if dd == 1 else (2.3, 8000)), fontsize=10,
                                                        arrowprops=dict(arrowstyle="->", color="#495057"))
ax.axhline(15000, color="#2F9E44", ls="--", lw=1.6)
ax.text(3.95, 16500, "たとえば「面積がこれをこえたら、交差点に着いた」", ha="right", fontsize=10, color="#2B8A3E")
ax.set_xlabel("箱までの距離〔m〕"); ax.set_ylabel("画像の中の面積〔画素の数〕")
ax.set_ylim(0, 60000); ax.grid(alpha=0.3)
ax.set_title("距離が2倍になると、面積は4分の1になる（20 cm の箱、説明用の計算）", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-area-distance.png", facecolor="white"); plt.close(fig)
print("f_px", round(f_px), "area 1m", round((f_px*W/1)**2), "2m", round((f_px*W/2)**2))
