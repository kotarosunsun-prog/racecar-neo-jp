"""Figure for 5-4: two ArUco (6x6) markers detected with racecar_utils, with corner order and orientation."""
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
OUT = "../images/racecar-neo-jp/5-4"; os.makedirs(OUT, exist_ok=True)

D = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_250)
def marker_img(mid, size, frame_bgr):
    m = cv.cvtColor(cv.aruco.generateImageMarker(D, mid, size), cv.COLOR_GRAY2BGR)
    q = size // 5
    m = cv.copyMakeBorder(m, q, q, q, q, cv.BORDER_CONSTANT, value=(255, 255, 255))
    f = size // 6
    return cv.copyMakeBorder(m, f, f, f, f, cv.BORDER_CONSTANT, value=frame_bgr)

def scene():
    img = np.zeros((480, 640, 3), np.uint8)
    for r in range(480):
        g = 190 - int(r * 0.1) if r < 300 else 140 - int((r - 300) * 0.3)
        img[r, :] = (g, g, g)
    a = marker_img(1, 150, (205, 120, 40))                        # ID 1, upright, blue frame, near
    img[90:90 + a.shape[0], 60:60 + a.shape[1]] = a
    b = cv.rotate(marker_img(3, 80, (40, 40, 210)), cv.ROTATE_90_CLOCKWISE)   # ID 3, turned right, red frame, far
    img[150:150 + b.shape[0], 430:430 + b.shape[1]] = b
    rng = np.random.default_rng(5)
    return np.clip(img.astype(np.int16) + rng.normal(0, 2, img.shape), 0, 255).astype(np.uint8)

if __name__ == "__main__":
    img = scene(); cv.imwrite("scene_5-4.png", img)
    COLORS = [((90, 100, 100), (120, 255, 255), "blue"), ((170, 100, 100), (10, 255, 255), "red")]
    markers = rc_utils.get_ar_markers(img, COLORS)
    out = img.copy(); rc_utils.draw_ar_markers(out, markers)
    fig, ax = plt.subplots(figsize=(7.6, 5.5), dpi=200)
    ax.imshow(cv.cvtColor(out, cv.COLOR_BGR2RGB)); ax.set_xticks([]); ax.set_yticks([])
    for m in markers:
        c = m.get_corners()
        for k, (r, col) in enumerate(c):
            ax.text(col, r, str(k), color="white", fontsize=9, ha="center", va="center",
                    bbox=dict(boxstyle="circle,pad=0.2", fc="#E8590C", ec="none"))
        cr, cc = c.mean(axis=0)
        below = c[:, 0].max() + 28
        ax.text(cc, below, f"ID {m.get_id()}・向き {m.get_orientation().name}・色 {m.get_color()}\n中心 ({cr:.0f}, {cc:.0f})",
                ha="center", va="top", fontsize=10, bbox=dict(boxstyle="round", fc="white", ec="#ADB5BD"))
        print(m.get_id(), m.get_orientation(), m.get_color(), c.tolist(), (round(cr), round(cc)))
    ax.set_title("get_ar_markers() で見つけたマーカー（数字は角の順番、説明用に作った画像）", fontsize=10.5)
    fig.tight_layout(); fig.savefig(f"{OUT}/fig1-markers.png", facecolor="white"); plt.close(fig)
