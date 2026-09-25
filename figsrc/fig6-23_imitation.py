"""Figure and numbers for 6-23 (imitation learning, sim2d model).
The book's record_drive.py / train_drive.py / drive_net.py (copies in il6-23/) are run in the stand-in."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "il6-23"))
import il_helpers as H
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-23"
out = H.r._orig


def tests(n=3):
    res, paths = [], []
    for s in range(1, n + 1):
        w, t = H.drive(s); L = np.array(w.log); paths.append(L)
        res.append(f"goal {t:.1f} s" if t else f"crash at ({L[-1,1]:.0f}, {L[-1,2]:.0f})")
    return res, paths


# 1) one lap of good driving
H.fresh()
wA = H.record(0.0, 0); out(H.train())
resA, pathsA = tests(); out("one good lap:", H.rows(), resA)
# 2) + one teaching run (the network drives, the human shows the angle)
wB = H.teach(1)
teach_rows = H.rows(); out(H.train())
resB, pathsB = tests(); out("+ teaching run (crashed=%s):" % wB.crashed, teach_rows, resB)
# 3) wobbly laps
for n in (3, 5):
    H.fresh()
    for s in range(n): H.record(0.3, s)
    H.train(); res, _ = tests(); out(f"{n} wobbly laps:", H.rows(), res)
H.fresh()

offA, offB = H.offset(np.array(wA.log)), H.offset(np.array(wB.log))
out(f"offset of the good lap: std {offA.std():.1f} cm, max {np.abs(offA).max():.1f}; teaching run: std {offB.std():.1f}, max {np.abs(offB).max():.1f}")

fig = plt.figure(figsize=(11.2, 7.4), dpi=200)
ax = fig.add_axes([0.02, 0.06, 0.44, 0.86]); ax2 = fig.add_axes([0.56, 0.3, 0.41, 0.5])
for x1, y1, x2, y2 in H.W: ax.plot([x1, x2], [y1, y2], color="#495057", lw=2)
LA, LB = pathsA[0], pathsB[0]
def upto_goal(L):
    idx = np.where(L[:, 2] > 2450)[0]
    return L[: idx[0] + 1] if len(idx) else L
LA, LB = upto_goal(LA), upto_goal(LB)
ax.plot(LA[:, 1], LA[:, 2], color="#868E96", lw=1.8, label="上手な運転1周だけで学習")
ax.plot(LA[-1, 1], LA[-1, 2], "x", color="#868E96", ms=11, mew=3)
ax.plot(LB[:, 1], LB[:, 2], color="#E8590C", lw=1.8, label="＋ 教える運転1回で学習し直し")
ax.plot([225, 375], [2450, 2450], color="#2F9E44", lw=2.5); ax.text(390, 2450, "ゴール", va="center", fontsize=9, color="#2B8A3E")
ax.plot([0], [0], "o", color="#212529", ms=5); ax.text(40, 60, "スタート", fontsize=9)
ax.set_aspect("equal"); ax.set_xlim(-650, 800); ax.set_ylim(-120, 2750); ax.axis("off")
ax.legend(fontsize=8.5, loc="center left", bbox_to_anchor=(0.0, 0.33), frameon=True, framealpha=0.95)
ax.set_title("ネットワークだけで走らせた道すじ", fontsize=10.5)
yA, yB = np.array(wA.log)[:, 0], np.array(wB.log)[:, 0]
nA = len(upto_goal(np.array(wA.log))); yA, offA = yA[:nA], offA[:nA]
ax2.plot(yA, offA, color="#868E96", lw=1.6, label="上手な運転1周の記録")
ax2.plot(yB, offB, color="#E8590C", lw=1.6, label="教える運転の記録\n（ネットワークが運転し、人が角度を示す）")
ax2.plot(yB[-1], offB[-1], "x", color="#E8590C", ms=10, mew=2.5)
ax2.axhline(0, color="#495057", lw=0.8)
ax2.set_xlim(0, 48); ax2.set_ylim(-150, 60); ax2.grid(alpha=0.3)
ax2.set_xlabel("時間〔秒〕"); ax2.set_ylabel("通路の真ん中からのずれ〔cm〕\n（＋：進む向きの右）")
ax2.annotate("広い所で、左へずれていく場面\n（上手な運転の記録にはない）", xy=(yB[-1] - 1.0, offB[-60]), xytext=(9, -120), fontsize=9, color="#D9480F", arrowprops=dict(arrowstyle="->", color="#D9480F"))
ax2.legend(fontsize=8.5, loc="upper left", frameon=True, framealpha=0.95)
ax2.set_title("記録した場面の、真ん中からのずれ", fontsize=10.5)
for s_ in ("top", "right"): ax2.spines[s_].set_visible(False)
fig.suptitle("人の運転をまねるネットワーク（6-18 のコース、speed 0.5、説明用の簡単なモデル）", fontsize=11)
fig.savefig(f"{OUT}/fig1-imitation.png", facecolor="white"); plt.close(fig)
