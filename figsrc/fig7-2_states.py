"""Figures for 7-2: the state diagram of patrol.py, and a 60-second run in a room (sim2d model)."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager as fm
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch7"))
import ch7run as C
from ch7run import box
import sim2d, wallsim
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/7-2"
P = C.r._orig
COL = {"FORWARD": "#1C7ED6", "BACK": "#E8590C", "TURN": "#2F9E44"}

# ---------- fig1: the state diagram ----------
fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=200)
pos = {"FORWARD": (1.5, 2.2), "BACK": (5.0, 3.3), "TURN": (5.0, 1.0)}
desc = {"FORWARD": "まっすぐ進む\nspeed 0.5", "BACK": "下がる\nspeed −0.4", "TURN": "空いているほうへ\n曲がる speed 0.4"}
for s, (x, y) in pos.items():
    ax.add_patch(patches.FancyBboxPatch((x - 0.95, y - 0.5), 1.9, 1.0, boxstyle="round,pad=0.05,rounding_size=0.25", fc="white", ec=COL[s], lw=2.2))
    ax.text(x, y + 0.2, s, ha="center", va="center", fontsize=11.5, color=COL[s], weight="bold")
    ax.text(x, y - 0.18, desc[s], ha="center", va="center", fontsize=8.5, color="#495057")
def arrow(a, b, text, rad, tx, ty):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color="#495057", lw=1.5, connectionstyle=f"arc3,rad={rad}", shrinkA=4, shrinkB=4))
    ax.text(tx, ty, text, fontsize=8.8, ha="center", va="center", bbox=dict(fc="#F8F9FA", ec="none"))
arrow((2.45, 2.55), (4.05, 3.3), "前の物が 50 cm より近い", -0.2, 2.9, 3.35)
arrow((5.0, 2.8), (5.0, 1.5), "1 秒たった\nまたは\n後ろの物が\n30 cm より近い", 0.0, 3.95, 2.15)
arrow((4.05, 1.0), (2.45, 1.85), "1.5 秒たった", -0.2, 3.0, 1.0)
arrow((5.95, 1.2), (5.95, 3.1), "前の物が\n50 cm より近い", 0.9, 7.55, 3.1)
ax.annotate("", xy=(0.55, 2.2), xytext=(-0.1, 2.2), arrowprops=dict(arrowstyle="-|>", color="#212529", lw=1.5))
ax.text(-0.1, 2.45, "start()", fontsize=9)
ax.set_xlim(-0.3, 8.3); ax.set_ylim(0.2, 4.1); ax.axis("off")
ax.set_title("patrol.py のステートマシン（状態と、切りかわる条件）", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-diagram.png", facecolor="white"); plt.close(fig)

# ---------- fig2: a run in a room ----------
W = [(-250, -150, 250, -150), (250, -150, 250, 450), (250, 450, -250, 450), (-250, 450, -250, -150)] + box(100, 250, 60, 60) + box(-120, 50, 50, 80)
states = []
w = sim2d.World(W, x=0, y=0, heading_deg=90, **wallsim.REAL)
w, out = C.run("patrol.py", w, 60)
L = np.array(w.log)
# rebuild the state of each frame from the printed changes
cur = "FORWARD"; changes = {f: t.split(" ")[0] for f, t in out if t.endswith("へ")}
for i in range(len(L)):
    if i + 1 in changes: cur = changes[i + 1]
    states.append(cur)
P("crashed:", w.crashed, "changes:", len(changes), "first:", [t for f, t in out][:7])
n = {s: sum(1 for x in changes.values() if x == s) for s in COL}
P("count into each state:", n)
closest = min(w.wall_distance() for _ in [0])
fig = plt.figure(figsize=(10.4, 5.4), dpi=200)
ax = fig.add_axes([0.03, 0.04, 0.5, 0.82]); ax2 = fig.add_axes([0.6, 0.18, 0.37, 0.6])
for x1, y1, x2, y2 in W: ax.plot([x1, x2], [y1, y2], color="#495057", lw=2)
for s, c in COL.items():
    m = np.array([st == s for st in states])
    ax.scatter(L[m, 1], L[m, 2], s=1.5, color=c, label=s)
ax.plot([0], [0], "o", color="#212529", ms=5)
ax.set_aspect("equal"); ax.set_xlim(-270, 270); ax.set_ylim(-170, 470); ax.axis("off")
ax.legend(fontsize=9, loc="upper left", markerscale=6, frameon=True, framealpha=0.95, bbox_to_anchor=(0.0, 1.0))
ax.set_title("60 秒間の道すじ（色は状態）", fontsize=10.5)
t = L[:, 0]; k = t <= 20
code = np.array([list(COL).index(s) for s in states])
for i, s in enumerate(COL):
    m = (code == i) & k
    ax2.scatter(t[m], np.full(m.sum(), 2 - i), s=6, color=COL[s], marker="s")
ax2.set_yticks([2, 1, 0]); ax2.set_yticklabels(list(COL)); ax2.set_xlim(0, 20); ax2.set_ylim(-0.6, 2.6)
ax2.set_xlabel("時間〔秒〕"); ax2.grid(axis="x", alpha=0.3); ax2.set_title("はじめの 20 秒の状態", fontsize=10.5)
for s in ("top", "right"): ax2.spines[s].set_visible(False)
fig.suptitle("部屋の中を走り回る（説明用の簡単なモデル）", fontsize=11, y=0.985)
fig.savefig(f"{OUT}/fig2-run.png", facecolor="white"); plt.close(fig)
