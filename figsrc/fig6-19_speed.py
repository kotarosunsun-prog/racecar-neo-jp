"""Figure for 6-19: speed from the front distance on the 6-18 course, with a faster car whose tyres can slide
(sim2d model: speed 1.0 = 3 m/s, sideways acceleration up to 5 m/s^2)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import font_manager as fm
import wallsim
from pid_book import PID
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-19"
W, PTS = wallsim.full_course()

best, _ = wallsim.simulate_speed(W, wallsim.SpeedBook(), 20)
best = best[best[:, 2] < 2700]
c7, crashed7 = wallsim.simulate_speed(W, wallsim.Const(0.7, wallsim.CourseBook(PID(0.04, 0.005, 0.04, i_zone=20))), 50)
c6, _ = wallsim.simulate_speed(W, wallsim.Const(0.6, wallsim.CourseBook(PID(0.04, 0.005, 0.04, i_zone=20))), 50)

fig = plt.figure(figsize=(11.0, 7.4), dpi=200)
ax = fig.add_axes([0.0, 0.05, 0.42, 0.86]); cax = fig.add_axes([0.41, 0.3, 0.013, 0.45])
ax2 = fig.add_axes([0.56, 0.12, 0.42, 0.74])
for x1, y1, x2, y2 in W: ax.plot([x1, x2], [y1, y2], color="#495057", lw=2.2)
pts = best[:, 1:3].reshape(-1, 1, 2); seg = np.concatenate([pts[:-1], pts[1:]], axis=1)
lc = LineCollection(seg, cmap="plasma", norm=plt.Normalize(0.8, 3.0), lw=3)
lc.set_array(best[:-1, 7] / 100); ax.add_collection(lc)
cb = fig.colorbar(lc, cax=cax); cb.set_label("車の速さ〔m/秒〕", fontsize=9)
c7v = c7[c7[:, 2] < 2700]
ax.plot(c7v[:, 1], c7v[:, 2], color="#868E96", lw=1.2, ls="--", label="ずっと speed 0.7\n（ぶつかった）")
ax.plot([c7[-1, 1]], [c7[-1, 2]], "x", color="#868E96", ms=10, mew=3)
ax.plot([0], [0], "o", color="#212529", ms=5); ax.text(40, 120, "スタート", fontsize=9)
ax.set_aspect("equal"); ax.set_xlim(-650, 800); ax.set_ylim(-120, 2750); ax.axis("off")
ax.legend(fontsize=8.5, loc="center left", bbox_to_anchor=(0.0, 0.33), frameon=True, framealpha=0.95)
ax.set_title("速さの PID ＋ ゲインの切りかえ（色が速さ）", fontsize=10.5)
t_best = wallsim.finish_time(best); t6 = wallsim.finish_time(c6)
m = best[:, 0] <= t_best; m6 = c6[:, 0] <= t6
ax2.plot(c6[m6, 0], c6[m6, 7] / 100, color="#868E96", lw=1.6, label=f"ずっと speed 0.6（{t6:.1f} 秒）")
ax2.plot(best[m, 0], best[m, 7] / 100, color="#E8590C", lw=1.8, label=f"速さの PID ＋ ゲインの切りかえ（{t_best:.1f} 秒）")
ax2.set_xlim(0, 20); ax2.set_ylim(0, 3.6); ax2.grid(alpha=0.3)
ax2.set_xlabel("時間〔秒〕"); ax2.set_ylabel("車の速さ〔m/秒〕")
ax2.legend(fontsize=8.5, loc="upper right", frameon=True, framealpha=0.95)
ax2.set_title("車の速さ（ゴールまで）", fontsize=10.5)
for s in ("top", "right"): ax2.spines[s].set_visible(False)
fig.suptitle("曲がり角の前で速さを落とす（速い車、説明用の簡単なモデル）", fontsize=11)
fig.savefig(f"{OUT}/fig1-speed.png", facecolor="white"); plt.close(fig)

# ---------- the table in the text ----------
for sp in (0.5, 0.6, 0.7, 1.0):
    o, crashed = wallsim.simulate_speed(W, wallsim.Const(sp, wallsim.CourseBook(PID(0.04, 0.005, 0.04, i_zone=20))), 50)
    t = wallsim.finish_time(o)
    print(f"constant speed {sp}: {'crashed at (%.0f, %.0f)' % (o[-1, 1], o[-1, 2]) if crashed else 'finish %.1f s' % t}, closest {o[:, 6].min():.1f} cm")
for lab, ctrl in [("speed PID, no gain change", wallsim.SpeedBook(schedule=False)), ("speed PID + gain change", wallsim.SpeedBook())]:
    o, crashed = wallsim.simulate_speed(W, ctrl, 30)
    o = o[o[:, 0] <= wallsim.finish_time(o)] if not crashed else o
    print(f"{lab}: {'crashed' if crashed else 'finish %.1f s' % o[-1, 0]}, closest {o[:, 6].min():.1f} cm, mean speed cmd {o[:, 5].mean():.2f}")
