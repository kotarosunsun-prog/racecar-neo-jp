"""Figure for 6-18: a course with a 45 degree bend, 90 degree corners, a narrow part and a wide part
(sim2d model, realistic LIDAR, speed 0.5)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import wallsim
from pid_book import PID
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-18"
W, PTS = wallsim.full_course()
fig, ax = plt.subplots(figsize=(9.6, 8.8), dpi=200)
for x1, y1, x2, y2 in W: ax.plot([x1, x2], [y1, y2], color="#495057", lw=2.4)
runs = [("状態で切りかえるだけ（6-17）", lambda: wallsim.States(PID(0.04, 0.005, 0.04, i_zone=20)), "#868E96"),
        ("正面を見て、開いている側へ曲がる（この回）", lambda: wallsim.CourseBook(PID(0.04, 0.005, 0.04, i_zone=20)), "#E8590C")]
for lab, make, col in runs:
    ctrl = make()
    o, crashed = wallsim.simulate(W, ctrl, 0.5, 50, x=0, extra=lambda c: (float(getattr(c, "turning", False)),))
    o = o[o[:, 2] < 2700]
    ax.plot(o[:, 1], o[:, 2], color=col, lw=2, label=lab + ("（ぶつかった）" if crashed else ""))
    if crashed: ax.plot([o[-1, 1]], [o[-1, 2]], "x", color=col, ms=10, mew=3)
    if isinstance(ctrl, wallsim.CourseBook):
        m = o[:, 7] > 0
        ax.scatter(o[m, 1], o[m, 2], s=4, color="#C92A2A", zorder=4, label="正面の壁を見て曲げている所")
    fin = np.where(o[:, 2] > 2450)[0]
    print(lab, "crashed" if crashed else "", f"finish {o[fin[0], 0]:.1f} s" if len(fin) else "", f"closest {o[:, 6].min():.1f} cm")
ax.text(40, 150, "スタート", fontsize=9); ax.plot([0], [0], "o", color="#212529", ms=5)
ax.text(400, 2600, "ゴール\n（縦 2450 cm）", fontsize=9)
notes = [(420, 650, "右へ 45°"), (420, 1150, "左へ 90°"), (-340, 1050, "右へ 90°"), (-120, 1650, "幅 90 cm"), (-480, 2000, "幅 300 cm"), (-360, 2300, "右へ 90°"), (400, 2230, "左へ 90°")]
for x, y, t in notes: ax.text(x, y, t, fontsize=9, color="#1864AB")
ax.set_aspect("equal"); ax.set_xlim(-650, 1250); ax.set_ylim(-120, 2750); ax.grid(alpha=0.25)
ax.set_xlabel("横〔cm〕"); ax.set_ylabel("縦〔cm〕")
ax.legend(fontsize=8.5, loc="lower right", bbox_to_anchor=(1.0, 0.0), frameon=True, framealpha=0.95)
ax.set_title("曲がり角・せまい所・広い所のあるコース（speed 0.5、説明用の簡単なモデル）", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-course.png", facecolor="white"); plt.close(fig)
