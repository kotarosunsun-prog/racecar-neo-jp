"""Figure for 6-3: camera view of a marker at the junction, and top-down paths for marker IDs 0 and 1 (sim2d model).
The paths are re-computed with the same logic as ar_turn.py."""
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
OUT = "../images/racecar-neo-jp/6-3"
WALLS = [(-75, -100, -75, 450), (75, -100, 75, 450), (-600, 600, 600, 600), (75, 450, 600, 450), (-600, 450, -75, 450)]
SPEED, KP, NEAR, TURN_TIME = 0.4, 0.8, 60, 2.3

def run(mid):
    w = sim2d.World(WALLS, x=20, y=0, heading_deg=90); cam = sim2d.MarkerCamera([(0, 600, mid, 20, (205, 120, 40))])
    rng = np.random.default_rng(0); timer = 0.0; turn_at = None
    for k in range(720):
        img = cam.render(w, rng=rng); speed, angle = SPEED, 0.0
        if timer <= 0:
            ms = [m for m in rc_utils.get_ar_markers(img) if m.get_id() in (0, 1)]
            if ms:
                m = max(ms, key=lambda m: np.ptp(m.get_corners()[:, 0])); c = m.get_corners()
                angle = max(-1, min(1, KP * (c[:, 1].mean() - 320) / 320))
                if np.ptp(c[:, 0]) > NEAR:
                    timer = TURN_TIME; turn_at = (w.x, w.y); turn = 1.0 if m.get_id() == 1 else -1.0
        if timer > 0:
            angle = turn; timer -= 1 / 60
        w.step(1 / 60, speed, angle)
    L = np.array(w.log); return L[:, 1], L[:, 2], turn_at

fig = plt.figure(figsize=(10.6, 4.9), dpi=200)
ax1 = fig.add_axes([0.03, 0.12, 0.45, 0.76])
w = sim2d.World([], x=-40, y=440, heading_deg=86)
img = sim2d.MarkerCamera([(0, 600, 1, 20, (205, 120, 40))]).render(w, rng=np.random.default_rng(3))
m = rc_utils.get_ar_markers(img)[0]; c = m.get_corners()
out = img.copy(); rc_utils.draw_ar_markers(out, [m])
ax1.imshow(cv.cvtColor(out, cv.COLOR_BGR2RGB)); ax1.set_xticks([]); ax1.set_yticks([])
ax1.plot([320, 320], [0, 479], color="white", ls=":", lw=1.5)
h = int(np.ptp(c[:, 0])); col = c[:, 1].mean()
ax1.annotate("", xy=(col, 285), xytext=(320, 285), arrowprops=dict(arrowstyle="<->", color="#E8590C", lw=2))
ax1.text(330, 360, f"ずれ = ({col:.0f} − 320) ÷ 320 = {(col - 320) / 320:+.2f}\n→ マーカーのほうを向く", fontsize=9,
         bbox=dict(boxstyle="round", fc="white", ec="#ADB5BD"))
ax1.text(10, 30, f"ID {m.get_id()}・写った高さ {h} 画素", fontsize=10, bbox=dict(boxstyle="round", fc="white", ec="#ADB5BD"))
ax1.set_title("カメラで見たマーカー", fontsize=11)
ax2 = fig.add_axes([0.55, 0.1, 0.43, 0.8])
for x1, y1, x2, y2 in WALLS: ax2.plot([x1, x2], [y1, y2], color="#495057", lw=3)
ax2.add_patch(patches.Rectangle((-15, 596), 30, 8, color="#1C7ED6"))
ax2.text(0, 612, "マーカー", ha="center", fontsize=9)
for mid, col_, lab in [(1, "#2F9E44", "番号 1 → 右へ"), (0, "#AE3EC9", "番号 0 → 左へ")]:
    x, y, ta = run(mid); ax2.plot(x, y, color=col_, lw=2.2, label=lab)
    ax2.plot([ta[0]], [ta[1]], "o", color=col_, ms=6)
ax2.text(30, 380, "●：曲がり始めた場所", fontsize=9)
ax2.set_aspect("equal"); ax2.set_xlim(-420, 420); ax2.set_ylim(-60, 660); ax2.grid(alpha=0.25)
ax2.legend(fontsize=9, loc="lower right", frameon=True); ax2.set_title("T 字路での道すじ", fontsize=11)
ax2.set_xlabel("横〔cm〕"); ax2.set_ylabel("縦〔cm〕")
fig.suptitle("AR マーカーの番号で曲がる向きを決める（説明用の簡単なモデル）", fontsize=11)
fig.savefig(f"{OUT}/fig1-ar-turn.png", facecolor="white"); plt.close(fig)
