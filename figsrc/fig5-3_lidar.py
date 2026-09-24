"""Figure for 5-3: top-down view of a synthetic LIDAR scan with direction labels and the closest point."""
import sys, os, numpy as np
# racecar_utils.py (racecar-neo-library/library) must be importable; set RACECAR_LIBRARY to its folder
sys.path.insert(0, os.environ.get("RACECAR_LIBRARY", "../../racecar-neo-library/library"))
import racecar_utils as rc_utils
import lidar_scene as L
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/5-3"; os.makedirs(OUT, exist_ok=True)

scan = L.make_scan()
ang = np.arange(len(scan)) * 360 / len(scan)
ok = scan > 0
x = scan[ok] * np.sin(np.radians(ang[ok])); y = scan[ok] * np.cos(np.radians(ang[ok]))
ca, cd = rc_utils.get_lidar_closest_point(scan)
fig, ax = plt.subplots(figsize=(6.6, 7.4), dpi=200)
ax.scatter(x, y, s=4, color="#1C7ED6", label="測った点（0.0 の点は描いていない）")
ax.add_patch(plt.Rectangle((-10, -16), 20, 32, color="#2F9E44", zorder=5))
ax.annotate("", xy=(0, 38), xytext=(0, 12), arrowprops=dict(arrowstyle="-|>", color="#2F9E44", lw=2), zorder=6)
for a, idx, name, (tx, ty) in [(0, 0, "前 0°", (0, 385)), (90, 180, "右 90°", (150, 0)), (180, 360, "後ろ 180°", (0, -200)), (270, 540, "左 270°", (-150, 0))]:
    ax.plot([0, 1000 * np.sin(np.radians(a))], [0, 1000 * np.cos(np.radians(a))], color="#ADB5BD", lw=0.8, ls="--", zorder=1)
    ax.text(tx, ty, f"{name}\nscan[{idx}]", ha="center", va="center", fontsize=10,
            bbox=dict(boxstyle="round", fc="white", ec="#CED4DA"), zorder=7)
px, py = cd * np.sin(np.radians(ca)), cd * np.cos(np.radians(ca))
ax.plot([0, px], [0, py], color="#E8590C", lw=2, zorder=6)
ax.scatter([px], [py], s=60, color="#E8590C", zorder=7, label=f"いちばん近い点（{ca:.1f}°、{cd:.0f} cm）")
ax.annotate("時計回り", xy=(62, 62), xytext=(88, 25), fontsize=9, color="#495057",
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.4", color="#495057"))
ax.set_xlim(-230, 280); ax.set_ylim(-230, 420); ax.set_aspect("equal"); ax.grid(alpha=0.25)
ax.set_xlabel("右〔cm〕"); ax.set_ylabel("前〔cm〕")
ax.set_title("LIDAR の測定点を上から見た図（説明用に作ったデータ）", fontsize=11)
ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-scan.png", facecolor="white"); plt.close(fig)
print("closest", ca, cd)
