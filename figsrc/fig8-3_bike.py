"""Figure for 8-3: how a bicycle-type robot turns -- the turning centre, the radii of the two wheels, L and the steering angle."""
import math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Arc, FancyBboxPatch
import matplotlib.transforms as T
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/8-3"
os.makedirs(OUT, exist_ok=True)

L, dlt = 0.6, math.radians(30)
R = L / math.tan(dlt)                                   # the turning centre is at (R, 0)
fig, ax = plt.subplots(figsize=(7.2, 5.6), dpi=200)


def wheel(x, y, heading_deg, color):
    w, h = 0.05, 0.16
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.005", fc=color, ec="#212529", lw=1.2,
                         transform=T.Affine2D().rotate_deg_around(x, y, -heading_deg) + ax.transData)
    ax.add_patch(box)


ax.plot([0, 0], [0, L], color="#495057", lw=4, solid_capstyle="round", zorder=2)        # the frame
wheel(0, 0, 0, "#ADB5BD"); wheel(0, L, math.degrees(dlt), "#FFA94D")
ax.plot([0, R], [0, 0], color="#1C7ED6", lw=1.6, ls="--")                              # rear wheel -> centre
ax.plot([0, R], [L, 0], color="#E8590C", lw=1.6, ls="--")                              # front wheel -> centre
ax.plot([R], [0], "o", color="#212529", ms=6)
ax.text(R + 0.04, -0.07, "回転の中心", fontsize=10)
ax.text(R / 2, -0.09, "後輪の半径 $R = L / \\tan\\delta$", fontsize=10, color="#1864AB", ha="center")
ax.text(R / 2 + 0.1, L / 2 + 0.06, "前輪の半径 $L / \\sin\\delta$", fontsize=10, color="#D9480F", rotation=-math.degrees(math.atan2(L, R)))
ax.annotate("", xy=(-0.12, L), xytext=(-0.12, 0), arrowprops=dict(arrowstyle="<->", color="#495057"))
ax.text(-0.15, L / 2, "L", fontsize=11, ha="right", va="center")
ax.plot([0, 0], [L, L + 0.25], color="#868E96", lw=1, ls=":")
ax.plot([0, 0.25 * math.sin(dlt)], [L, L + 0.25 * math.cos(dlt)], color="#E8590C", lw=1.2)
ax.add_patch(Arc((0, L), 0.36, 0.36, theta1=90 - math.degrees(dlt), theta2=90, color="#E8590C", lw=1.2))
ax.text(0.06, L + 0.21, "δ", fontsize=11, color="#D9480F")
ax.add_patch(Arc((R, 0), 2 * R, 2 * R, theta1=100, theta2=180, color="#1C7ED6", lw=1, ls=":"))
ax.add_patch(Arc((R, 0), 2 * math.hypot(R, L), 2 * math.hypot(R, L), theta1=118, theta2=160, color="#E8590C", lw=1, ls=":"))
ax.text(0.05, -0.05, "後輪", fontsize=9, ha="left", va="top"); ax.text(-0.06, L + 0.02, "前輪", fontsize=9, ha="right")
ax.plot([0.06, R - 0.08], [0.02, 0.02], alpha=0)
ax.add_patch(Arc((R, 0), 0.3, 0.3, theta1=180 - math.degrees(math.atan2(L, R)), theta2=180, color="#495057", lw=1))
ax.text(R - 0.25, 0.06, "δ", fontsize=10, color="#495057")
ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-0.45, R + 0.45); ax.set_ylim(-0.25, L + 0.4)
ax.set_title("自転車の形のロボットの曲がり方（後輪は、回転の中心のまわりに半径 R の円をえがく）", fontsize=10.5)
fig.tight_layout()
fig.savefig(f"{OUT}/fig1-bike.png", facecolor="white"); plt.close(fig)
