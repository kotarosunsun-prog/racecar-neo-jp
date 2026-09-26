"""Figure for 7-13 (sim2d model): switching between the wall follower and the gap follower on the mixed course D."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch7"))
import ch7run as C
import courses7 as K
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/7-13"
os.makedirs(OUT, exist_ok=True)
P = C.r._orig
W = K.mixed_course()
FY = 4600
NORESET = ("        if not BLEND:\n            wall.reset()                     # 壁沿い走行を、はじめからやり直す\n", "")
BLEND = ("BLEND = False ", "BLEND = True ")
CFG = [("wall", "壁沿い走行だけ", "wall_only.py", []),
       ("gap", "Gap Follower だけ（speed 0.5）", "gap_follow.py", C.settings("final", MIN_SPEED="0.5", MAX_SPEED="0.5")),
       ("switch", "切りかえ（combo_follow.py）", "combo_follow.py", []),
       ("noreset", "切りかえ、もどるときに reset() しない", "combo_follow.py", [NORESET]),
       ("blend", "混ぜ合わせ（BLEND = True）", "combo_follow.py", [BLEND])]
runs = {}
for key, lab, prog, subs in CFG:
    res = []
    for seed in range(5):
        L, out, crashed = C.drive(prog, W, 110, subs=subs, seed=seed)
        fin = np.where(L[:, 2] > FY)[0]; n = fin[0] if len(fin) else len(L)
        res.append((round(float(L[fin[0], 0]), 1) if len(fin) else ("X" if crashed else "-"), L[n - 1, 1:3].round().tolist(),
                    sum(1 for f, t in out if t.startswith("GAP へ"))))
        runs[(key, seed)] = (L, n, crashed, out)
    P(key, res, flush=True)
L, n, crashed, out = runs[("switch", 0)]
for f, t in out[:14]:
    P(f"{f / 60:5.1f} 秒 {t}")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 8.2), dpi=240)
for ax in (a1, a2):
    C.draw_walls(ax, W, lw=1.1)
    ax.axhline(FY, color="#2F9E44", ls=":", lw=1.2); ax.text(-690, FY + 40, "ゴール", fontsize=8.5, color="#2F9E44", ha="left")
    ax.axhline(2600, color="#ADB5BD", ls="--", lw=0.8)
    ax.plot([0], [0], "o", color="#212529", ms=4)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_ylim(-150, 4750); ax.set_xlim(-700, 700)
a1.text(-690, 1300, "横に入り口の\nある通路\n（6-17）", fontsize=8.5, color="#495057")
a1.text(-690, 3600, "柱の並ぶ\n広間", fontsize=8.5, color="#495057")
for key, col in (("wall", "#1C7ED6"), ("gap", "#E8590C")):
    L2, n2, cr, _ = runs[(key, 0)]
    a1.plot(L2[:n2, 1], L2[:n2, 2], color=col, lw=1.5, label=dict((k, l) for k, l, p, s in CFG)[key] + ("（ぶつかった）" if cr else "（ゴールできなかった）"))
    if cr: a1.plot(L2[n2 - 1, 1], L2[n2 - 1, 2], "x", color=col, ms=9, mew=2.5)
a1.legend(fontsize=8.5, loc="lower center", bbox_to_anchor=(0.5, -0.06), frameon=False)
a1.set_title("どちらか1つだけで走る", fontsize=10.5)
# the switching run, coloured by mode (from the printed messages)
mode = np.zeros(n, int)
for f, t in out:
    if t.startswith("GAP へ"): mode[f:] = 1
    if t.startswith("WALL へ"): mode[f:] = 0
cols = {0: "#1C7ED6", 1: "#E8590C"}
k0 = 0
for k in range(1, n + 1):
    if k == n or mode[k] != mode[k0]:
        a2.plot(L[k0:k + 1, 1], L[k0:k + 1, 2], color=cols[mode[k0]], lw=2.0)
        k0 = k
a2.plot([], [], color=cols[0], lw=2, label="WALL（壁沿い走行）"); a2.plot([], [], color=cols[1], lw=2, label="GAP（Gap Follower）")
a2.legend(fontsize=8.5, loc="lower center", bbox_to_anchor=(0.5, -0.06), frameon=False, ncol=2)
a2.set_title(f"切りかえて走る（{L[n - 1, 0]:.1f} 秒でゴール）", fontsize=10.5)
fig.suptitle("前に物があるときだけ Gap Follower に切りかえる（説明用の簡単なモデル）", fontsize=11)
fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.07, wspace=0.05)
fig.savefig(f"{OUT}/fig1-combine.png", facecolor="white"); plt.close(fig)
