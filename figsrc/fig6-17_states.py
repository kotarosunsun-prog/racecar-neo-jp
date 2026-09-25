"""Figure for 6-17: a corridor with openings (sim2d model, realistic LIDAR, speed 0.5).
Left: paths of the 6-16 program, of the state program switching at once (HOLD 1), and with HOLD 10.
Right: the state along the corridor for HOLD 10."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager as fm
import wallsim
from pid_book import PID
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-17"
W = wallsim.openings_course()
runs = [("両側の真ん中だけ（6-16）", lambda: wallsim.Center(PID(0.04, 0.005, 0.04, i_zone=20)), "#868E96"),
        ("状態を切りかえる（HOLD 1：すぐ切りかえる）", lambda: wallsim.States(PID(0.04, 0.005, 0.04, i_zone=20), hold=1), "#1C7ED6"),
        ("状態を切りかえる（HOLD 10）", lambda: wallsim.States(PID(0.04, 0.005, 0.04, i_zone=20), hold=10), "#E8590C")]
fig = plt.figure(figsize=(10.4, 8.8), dpi=200)
ax = fig.add_axes([0.07, 0.07, 0.52, 0.86]); axs = fig.add_axes([0.66, 0.07, 0.07, 0.86], sharey=ax)
for x1, y1, x2, y2 in W: ax.plot([x1, x2], [y1, y2], color="#495057", lw=2.4)
final = None
for lab, make, col in runs:
    ctrl = make()
    o, crashed = wallsim.simulate(W, ctrl, 0.5, 36, x=0, extra=(lambda c: (c.state,)) if isinstance(ctrl, wallsim.States) else None)
    ax.plot(o[:, 1], o[:, 2], color=col, lw=2, label=lab + ("（ぶつかった）" if crashed else ""))
    if crashed: ax.plot([o[-1, 1]], [o[-1, 2]], "x", color=col, ms=10, mew=3)
    if not crashed: final = o
    print(lab, "crashed" if crashed else "", f"end y {o[-1, 2]:.0f}, largest sideways move {np.abs(o[:, 1]).max():.1f} cm")
ax.text(-235, 455, "左の壁がない\n（奥の壁は 450 cm 先）", ha="center", va="center", fontsize=8.5, color="#495057")
ax.text(270, 1350, "右の壁がない", ha="center", va="center", fontsize=8.5, color="#495057")
ax.text(0, 1950, "両側の壁がない\n（広い部屋）", ha="center", va="center", fontsize=8.5, color="#495057",
        bbox=dict(fc="white", ec="none", alpha=0.8))
ax.plot([0], [0], "o", color="#212529", ms=5); ax.text(15, -60, "スタート", fontsize=9)
ax.set_aspect("equal"); ax.set_xlim(-650, 650); ax.set_ylim(-120, 2650); ax.grid(alpha=0.25)
ax.set_xlabel("横〔cm〕"); ax.set_ylabel("縦〔cm〕")
ax.legend(fontsize=8, loc="upper right", frameon=True, framealpha=0.95)
ax.set_title("入り口や広い部屋のある通路（speed 0.5、説明用の簡単なモデル）", fontsize=10.5, loc="left")
cols = {0: "#FFD8A8", 1: "#A5D8FF", 2: "#B2F2BB", 3: "#DEE2E6"}
st = final[:, 7].astype(int); y = final[:, 2]
start = 0
for i in range(1, len(st) + 1):
    if i == len(st) or st[i] != st[start]:
        axs.add_patch(patches.Rectangle((0, y[start]), 1, y[i - 1] - y[start], color=cols[st[start]], lw=0))
        mid = (y[start] + y[i - 1]) / 2
        if y[i - 1] - y[start] > 100:
            axs.text(0.5, mid, wallsim.States.NAMES[st[start]], ha="center", va="center", fontsize=8.5, rotation=90)
        start = i
axs.set_xlim(0, 1); axs.set_xticks([]); axs.tick_params(labelleft=False)
axs.set_title("状態\n（HOLD 10）", fontsize=9.5)
fig.savefig(f"{OUT}/fig1-states.png", facecolor="white"); plt.close(fig)
