"""Figure for 8-1 (sim2d model): the book's grand-prix course, the path of grand_prix.py coloured by state, and two camera views."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch8"))
import ch8run as C
import course8 as K
import sim2d, wallsim
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch7"))
from ch7run import draw_walls
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/8-1"
os.makedirs(OUT, exist_ok=True)
P = C.r._orig

L, out, crashed, fin = C.gp(T=180, seed=0)
P("crashed", crashed, "end", L[-1, :3].round(1))
for f, t in out:
    if not t.startswith("  "):
        P(f"{f / 60:5.1f} 秒 {t}")
NAMES = ["LINE", "WALL", "GAP", "MARKER", "TURN", "FINISH"]
state = np.zeros(len(L), int)
for f, t in out:
    for k, nm in enumerate(NAMES):
        if t.startswith(nm + " へ"):
            state[f:] = k
COL = {0: "#1C7ED6", 1: "#495057", 2: "#E8590C", 3: "#2F9E44", 4: "#AE3EC9", 5: "#C92A2A"}
LAB = {0: "LINE（線をたどる）", 1: "WALL（壁沿い）", 2: "GAP（空きへ）", 3: "MARKER（マーカーへ）", 4: "TURN（曲がる）"}

fig = plt.figure(figsize=(11.0, 7.4), dpi=200)
ax = fig.add_axes([0.0, 0.03, 0.46, 0.9])
draw_walls(ax, K.gp_walls(), lw=1.2)
ln = np.array(K.gp_line()); ax.plot(ln[:, 0], ln[:, 1], color="#74C0FC", lw=3, alpha=0.6, zorder=1)
k0 = 0
for k in range(1, len(L) + 1):
    if k == len(L) or state[k] != state[k0]:
        ax.plot(L[k0:k + 1, 1], L[k0:k + 1, 2], color=COL[state[k0]], lw=2.2, zorder=3)
        k0 = k
for (x, y, mid, s, c) in K.MARKERS:
    ax.plot([x - 25, x + 25], [y, y], color="#212529", lw=5, solid_capstyle="butt", zorder=4)
    ax.text(x + 40, y + 45, f"マーカー {mid}", fontsize=8.5, ha="left")
ax.plot(L[-1, 1], L[-1, 2], "s", color=COL[5], ms=6, zorder=5); ax.text(L[-1, 1] + 40, L[-1, 2] - 60, "止まった", fontsize=8.5, color=COL[5])
ax.plot([0], [0], "o", color="#212529", ms=5, zorder=5); ax.text(40, -110, "スタート", fontsize=8.5)
for txt, (x, y) in (("① 線", (-280, 600)), ("② 通路", (420, 1150)), ("③ 分かれ道", (-760, 2560)), ("④ 箱のある広間", (630, 3650))):
    ax.text(x, y, txt, fontsize=9.5, color="#343A40")
ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-760, 1000); ax.set_ylim(-200, 4800)
ax.legend([Line2D([], [], color=COL[k], lw=2.2) for k in LAB] + [Line2D([], [], color="#74C0FC", lw=3, alpha=0.6)],
          list(LAB.values()) + ["床の線"], fontsize=8, loc="upper left", bbox_to_anchor=(0.62, 0.46), frameon=False)
ax.set_title(f"この本のコースを grand_prix.py で走る（{[f / 60 for f, t in out if t.startswith('FINISH')][0]:.1f} 秒で止まった）", fontsize=10)

# two camera views: on the line, and at the T junction
views = [("線の区間で見た画像（下の四角が、線を探す所）", (0, 180, 90)), ("分かれ道の手前で見た画像（マーカー 1）", (-300, 2120, 90))]
cam = K.GPCamera()
for k, (title, (x, y, h)) in enumerate(views):
    a = fig.add_axes([0.5, 0.52 - k * 0.46, 0.47, 0.4])
    w = sim2d.World([], x=x, y=y, heading_deg=h)
    img = cam.render(w, frame=-10 - k, rng=np.random.default_rng(k))
    a.imshow(img[:, :, ::-1]); a.set_xticks([0, 320, 639]); a.set_yticks([0, 240, 479]); a.tick_params(labelsize=7)
    if k == 0:
        a.add_patch(plt.Rectangle((0, 360), 639, 119, fill=False, ec="#FAB005", lw=1.5))
    a.set_title(title, fontsize=9.5)
fig.suptitle("線・壁・障害物・AR マーカーの区間を、状態を切りかえて走る（説明用の簡単なモデル）", fontsize=11)
fig.savefig(f"{OUT}/fig1-course.png", facecolor="white"); plt.close(fig)
