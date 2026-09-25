"""Figures for 6-20: tuning for a time attack on the 6-18 course with the fast car of 6-19 (sim2d model).
Each setting is run 20 times with different LIDAR noise (seed 0..19).
fig1: mean time to the goal vs. the closest distance to a wall; fig2: section times (like the checkpoints of race mode)."""
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
OUT = "../images/racecar-neo-jp/6-20"
W, _ = wallsim.full_course()
GOAL = 2450
SPLITS = (800, 1300, 2100, GOAL)     # after the 45 degree bend / after the two 90 degree corners / after the narrow and wide parts / goal


def run(ctrl, seed=0, T=40):
    """one run; returns (goal time or None, closest distance to a wall, split times)"""
    w = wallsim.sim2d.World(W, x=0, y=0, heading_deg=90, seed=seed, **wallsim.FAST)
    w.scan()
    closest, splits = 1e9, []
    for _ in range(int(T * 60)):
        speed, angle = ctrl(w.scan())
        w.step(wallsim.DT, speed, angle)
        closest = min(closest, w.wall_distance())
        while len(splits) < len(SPLITS) and w.y > SPLITS[len(splits)]:
            splits.append(w.t)
        if w.crashed:
            return None, closest, splits
        if w.y > GOAL:
            return w.t, closest, splits
    return None, closest, splits


def trials(kw, n=20):
    times, closest, fails = [], [], 0
    for s in range(n):
        t, c, _ = run(wallsim.SpeedBook(**kw), s)
        closest.append(c)
        if t is None: fails += 1
        else: times.append(t)
    return times, min(closest), fails


SETTINGS = [
    ("もと（6-19）", {}),
    ("FRONT_LIMIT 150", dict(front_limit=150)),
    ("FRONT_LIMIT 250", dict(front_limit=250)),
    ("FRONT_LIMIT 300", dict(front_limit=300)),
    ("FRONT_TARGET 30", dict(front_target=30)),
    ("FRONT_TARGET 100", dict(front_target=100)),
    ("速さの KP 0.007", dict(kpv=0.007)),
    ("MAX_SPEED 0.9", dict(max_speed=0.9)),
    ("FRONT_LIMIT 300 ＋ FRONT_TARGET 40", dict(front_limit=300, front_target=40)),
    ("FRONT_LIMIT 300 ＋ FRONT_TARGET 50", dict(front_limit=300, front_target=50)),
    ("FRONT_LIMIT 300 ＋ 速さの KP 0.006", dict(front_limit=300, kpv=0.006)),
]
res = []
for lab, kw in SETTINGS:
    times, c, fails = trials(kw)
    res.append((lab, kw, times, c, fails))
    print(f"{lab:34} ok {20 - fails:2}/20  mean {np.mean(times):5.1f}  slowest {max(times):5.1f}  fastest {min(times):5.1f}  closest {c:5.1f}")

# ---------- fig1: time vs. margin ----------
fig, ax = plt.subplots(figsize=(9.6, 6.2), dpi=200)
ax.axhspan(0, 12, color="#FFE3E3"); ax.text(20.9, 6, "ぶつかる（車の半径 12 cm）", ha="right", va="center", fontsize=9, color="#C92A2A")
ax.axhline(20, color="#868E96", ls="--", lw=1); ax.text(20.9, 20.6, "余裕の目安（20 cm）", ha="right", va="bottom", fontsize=9, color="#495057")
off = {"もと（6-19）": (0, 14), "FRONT_LIMIT 150": (-10, -14), "FRONT_LIMIT 250": (8, -4), "FRONT_LIMIT 300": (-10, 0),
       "FRONT_TARGET 30": (-10, 4), "FRONT_TARGET 100": (0, 22), "速さの KP 0.007": (0, -24), "MAX_SPEED 0.9": (8, 4),
       "FRONT_LIMIT 300 ＋ FRONT_TARGET 40": (8, -14), "FRONT_LIMIT 300 ＋ FRONT_TARGET 50": (8, -4),
       "FRONT_LIMIT 300 ＋ 速さの KP 0.006": (10, 4)}
for lab, kw, times, c, fails in res:
    mean = np.mean(times)
    if fails:
        ax.plot(mean, c, "x", color="#C92A2A", ms=10, mew=2.5)
        txt = f"{lab}\n（{fails}回ぶつかった）"; col = "#C92A2A"
    else:
        ax.plot(mean, c, "o", color="#1C7ED6" if lab != "FRONT_LIMIT 300 ＋ FRONT_TARGET 50" else "#E8590C", ms=8)
        txt = lab; col = "#212529"
    dx, dy = off[lab]
    ax.annotate(txt, (mean, c), xytext=(dx, dy), textcoords="offset points", fontsize=8.2, color=col,
                ha="left" if dx > 0 else ("right" if dx < 0 else "center"), va="center")
ax.set_xlim(14.5, 21.0); ax.set_ylim(0, 36); ax.grid(alpha=0.3)
ax.set_xlabel("ゴールまでの時間の平均〔秒〕（ぶつからなかった回だけ）"); ax.set_ylabel("20回の中で、壁にいちばん近づいた距離〔cm〕")
ax.set_title("速さと余裕（どの設定も20回ずつ、速い車、説明用の簡単なモデル）", fontsize=10.5)
ax.annotate("", xy=(14.8, 34), xytext=(16.2, 34), arrowprops=dict(arrowstyle="->", color="#495057"))
ax.text(16.3, 34, "速い", va="center", fontsize=9, color="#495057")
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-tradeoff.png", facecolor="white"); plt.close(fig)

# ---------- fig2: section times ----------
rows = [("ずっと speed 0.6", wallsim.Const(0.6, wallsim.CourseBook(PID(0.04, 0.005, 0.04, i_zone=20)))),
        ("もと（6-19）", wallsim.SpeedBook()),
        ("FRONT_LIMIT 300 ＋ FRONT_TARGET 50", wallsim.SpeedBook(front_limit=300, front_target=50))]
names = ["① 45° の角", "② 90° の角2つ", "③ せまい所・広い所", "④ 90° の角2つ・ゴール"]
cols = ["#A5D8FF", "#FFD8A8", "#B2F2BB", "#D0BFFF"]
fig, ax = plt.subplots(figsize=(9.6, 3.6), dpi=200)
for i, (lab, ctrl) in enumerate(rows):
    t, c, sp = run(ctrl, 0)
    d = np.diff([0.0] + sp)
    print(lab, f"goal {t:.2f}", " ".join(f"{v:.2f}" for v in d))
    left = 0.0
    for j, v in enumerate(d):
        ax.barh(i, v, left=left, color=cols[j], edgecolor="white", label=names[j] if i == 0 else None)
        ax.text(left + v / 2, i, f"{v:.1f}", ha="center", va="center", fontsize=8.5)
        left += v
    ax.text(left + 0.2, i, f"{t:.1f} 秒", va="center", fontsize=9)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=9); ax.invert_yaxis()
ax.set_xlim(0, 22); ax.set_xlabel("時間〔秒〕")
ax.legend(ncol=4, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.28), frameon=False)
ax.set_title("区間ごとの時間（1回目の走り、説明用の簡単なモデル）", fontsize=10.5)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-splits.png", facecolor="white"); plt.close(fig)
