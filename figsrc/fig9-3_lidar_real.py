"""Figure for 9-3 (sim2d model, a 720-point LIDAR turning about 10 times a second).
Left: what the LIDAR sees in a hallway with a clear glass pane (the pane is not seen).
Right: safety_stop.py driving toward the pane: it stops for a wall, not for glass (ch9/glass_run.py -> ch9/data/glass.json)."""
import json, os, sys
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
from sim_real import GlassWorld

OUT = "../images/racecar-neo-jp/9-3"
os.makedirs(OUT, exist_ok=True)
WALLS = [(-75, -100, -75, 1200), (75, -100, 75, 1200), (-75, -100, 75, -100), (-75, 1200, 75, 1200)]
PANE = [(-75, 500, 75, 500)]
data = json.load(open(os.path.join(HERE, "ch9", "data", "glass.json")))

fig = plt.figure(figsize=(9.0, 5.0), dpi=200)

# left: the scan in the glass hallway
a2 = fig.add_axes([0.08, 0.1, 0.3, 0.78])
w = GlassWorld(WALLS, PANE, x=0, y=200, heading_deg=90, seed=0)
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
a3 = fig.add_axes([0.52, 0.13, 0.44, 0.72])
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
fig.text(0.5, 0.01, "説明用の簡単なモデル（上から見た2次元の車と、720 点・1 秒に 10 回転の LIDAR）", ha="center",
         fontsize=8.5, color="#495057")
fig.savefig(os.path.join(OUT, "fig1-lidar-real.png"))
