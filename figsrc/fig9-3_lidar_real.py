"""Figure for 9-3 (sim2d model).
Left: the same index scan[180] points to 90 deg with 720 points but to 60 deg with 1080 points.
Middle: what a 1080-point LIDAR sees in a hallway with a clear glass pane (the pane is not seen).
Right: safety_stop.py driving toward the pane: it stops for a wall, not for glass (ch9/glass_run.py -> ch9/data/glass.json)."""
import json, math, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wallsim
from sim_real import GlassWorld, real_like

OUT = "../images/racecar-neo-jp/9-3"
os.makedirs(OUT, exist_ok=True)
WALLS = [(-75, -100, -75, 1200), (75, -100, 75, 1200), (-75, -100, 75, -100), (-75, 1200, 75, 1200)]
PANE = [(-75, 500, 75, 500)]
data = json.load(open(os.path.join(HERE, "ch9", "data", "glass.json")))

fig = plt.figure(figsize=(11.2, 5.0), dpi=200)

# left: the index pitfall
a1 = fig.add_axes([0.03, 0.1, 0.3, 0.78])
a1.plot([50, 50], [-60, 110], color="#495057", lw=3)
a1.text(53, -55, "右の壁", fontsize=9, color="#495057")
a1.add_patch(plt.Rectangle((-10, -15), 20, 30, color="#212529"))
a1.annotate("", xy=(0, 40), xytext=(0, 16), arrowprops=dict(arrowstyle="->", lw=1.5))
a1.text(3, 36, "前", fontsize=9)
for deg, c, lab in ((90, "#1C7ED6", "シミュレータ（720 点）\nscan[180] は 90°：50 cm"),
                    (60, "#C92A2A", "実機（1080 点）\nscan[180] は 60°：57.7 cm")):
    r = 50 / math.sin(math.radians(deg))
    x, y = r * math.sin(math.radians(deg)), r * math.cos(math.radians(deg))
    a1.plot([0, x], [0, y], color=c, lw=2)
    a1.plot([x], [y], "o", color=c, ms=6)
    a1.text(-58, 88 if deg == 60 else -40, lab, color=c, fontsize=9, va="center")
a1.set_xlim(-60, 80); a1.set_ylim(-65, 110); a1.set_aspect("equal"); a1.axis("off")
a1.set_title("同じ番号でも、向きがちがう", fontsize=10)

# middle: the scan in the glass hallway
a2 = fig.add_axes([0.37, 0.1, 0.22, 0.78])
w = real_like(GlassWorld(WALLS, PANE, x=0, y=200, heading_deg=90, seed=0))
scan = w._raw_scan()
ok = scan > 0
ang = w.psi - w.phi
a2.plot(w.x + scan[ok] * np.cos(ang[ok]), w.y + scan[ok] * np.sin(ang[ok]), ".", color="#1C7ED6", ms=1.5,
        label="LIDAR の点")
for x1, y1, x2, y2 in WALLS:
    a2.plot([x1, x2], [y1, y2], color="#ADB5BD", lw=1)
a2.plot([-75, 75], [500, 500], color="#74C0FC", lw=4, alpha=0.6)
a2.text(0, 560, "ガラス\n（点がない）", ha="center", fontsize=8.5, color="#1971C2")
a2.add_patch(plt.Rectangle((-10, 185), 20, 30, color="#212529"))
a2.set_xlim(-160, 160); a2.set_ylim(-110, 1220); a2.set_aspect("equal")
a2.set_xticks([]); a2.set_yticks([0, 500, 1000]); a2.set_ylabel("前向きの位置〔cm〕")
a2.set_title("ガラスの向こうの壁が見える", fontsize=10)
for s in ("top", "right"): a2.spines[s].set_visible(False)

# right: position against time
a3 = fig.add_axes([0.68, 0.13, 0.3, 0.72])
for key, c, lab in (("wall", "#2F9E44", "見える板（壁）"), ("glass", "#C92A2A", "ガラスの板")):
    d = data[key]
    a3.plot(d["t"], d["y"], color=c, lw=2, label=lab)
    if d["crashed"]:
        a3.text(d["t"][-1] - 0.1, d["y"][-1] + 18, "ぶつかった", color=c, fontsize=8.5, ha="right")
    else:
        a3.text(8.4, d["y"][-1] - 90, f"止まった\n（板の {500 - d['y'][-1]:.0f} cm 手前）", color=c, fontsize=8.5, ha="right")
a3.axhline(500, color="#74C0FC", lw=3, alpha=0.6)
a3.text(0.1, 508, "板の位置", fontsize=8.5, color="#1971C2")
a3.set_xlim(0, 8.5); a3.set_ylim(0, 560)
a3.set_xlabel("時間〔秒〕"); a3.set_ylabel("車の中心の位置〔cm〕")
a3.legend(loc="lower right", fontsize=8.5, frameon=False)
a3.set_title("safety_stop.py（7-1）で板に向かって走る", fontsize=10)
for s in ("top", "right"): a3.spines[s].set_visible(False)
fig.text(0.5, 0.01, "説明用の簡単なモデル（上から見た2次元の車と、1080 点・1 秒に 10 回転の LIDAR）", ha="center",
         fontsize=8.5, color="#495057")
fig.savefig(os.path.join(OUT, "fig1-lidar-real.png"))
