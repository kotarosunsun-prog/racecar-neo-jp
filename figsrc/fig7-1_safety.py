"""Figures for 7-1 (sim2d model): the band in front of the car, and stopping before a wall."""
import os, sys, re, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager as fm
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch7"))
import ch7run as C
import sim2d, wallsim
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/7-1"
P = C.r._orig
HW = 20.0

# ---------- fig1: the band ----------
W = [(-200, 330, 200, 250)] + sim2d.cone_segments(12, 150, radius=6.0) + sim2d.cone_segments(-45, 110, radius=6.0)
w = sim2d.World(W, x=0, y=0, heading_deg=90, **wallsim.REAL)
w.scan(); scan = w.scan()
ang = np.radians(np.arange(720) * 0.5)
fwd, side = scan * np.cos(ang), scan * np.sin(ang)
ok = scan > 0
inside = ok & (fwd > 0) & (np.abs(side) < HW)
near = fwd[inside].min(); k = np.flatnonzero(inside)[np.argmin(fwd[inside])]
fig, ax = plt.subplots(figsize=(7.2, 6.6), dpi=200)
ax.add_patch(patches.Rectangle((-HW, 0), 2 * HW, 340, color="#FFE8CC", lw=0, zorder=0))
ax.plot([-HW, -HW], [0, 340], color="#E8590C", lw=1.2, ls="--"); ax.plot([HW, HW], [0, 340], color="#E8590C", lw=1.2, ls="--")
for x1, y1, x2, y2 in W: ax.plot([x1, x2], [y1, y2], color="#495057", lw=2)
ax.scatter(side[ok & ~inside], fwd[ok & ~inside], s=4, color="#868E96", label="LIDAR の点")
ax.scatter(side[inside], fwd[inside], s=7, color="#E8590C", label="帯の中の点")
ax.plot(side[k], fwd[k], "o", ms=11, mfc="none", mec="#C92A2A", mew=2)
ax.annotate(f"帯の中でいちばん近い点\n（前向きに {near:.0f} cm）", xy=(side[k], fwd[k]), xytext=(60, 175), fontsize=9.5, color="#C92A2A",
            arrowprops=dict(arrowstyle="->", color="#C92A2A"))
ax.text(-45, 128, "帯の外の柱\n（止まらない）", ha="center", fontsize=9, color="#495057")
ax.add_patch(patches.Circle((0, 0), 12, color="#1C7ED6")); ax.annotate("", xy=(0, 40), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="#1C7ED6", lw=2))
ax.text(0, -30, "車", ha="center", fontsize=10, color="#1864AB")
ax.annotate("", xy=(-HW, 20), xytext=(HW, 20), arrowprops=dict(arrowstyle="<->", color="#E8590C"))
ax.text(HW + 6, 22, f"帯の幅 {2 * HW:.0f} cm", fontsize=9, color="#D9480F", va="center")
ax.set_aspect("equal"); ax.set_xlim(-200, 200); ax.set_ylim(-50, 350); ax.grid(alpha=0.25)
ax.set_xlabel("横〔cm〕（右が＋）"); ax.set_ylabel("前〔cm〕")
ax.legend(fontsize=9, loc="upper left", frameon=True, framealpha=0.95)
ax.set_title("車の前の帯の中だけを見る（説明用の簡単なモデル）", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-band.png", facecolor="white"); plt.close(fig)
P("band: nearest ahead", round(near, 1))

# ---------- brake test (5 runs each) ----------
table = []
for sp in (0.25, 0.5, 0.75, 1.0):
    seen, true = [], []
    for seed in range(5):
        w = sim2d.World([(-300, 400, 300, 400)], x=0, y=0, heading_deg=90, seed=seed, **wallsim.REAL)
        w, out = C.run("brake_test.py", w, 12, subs=[("SPEED = 0.5 ", f"SPEED = {sp} ")])
        m = [re.search(r"ブレーキから ([\d.]+)", t) for f, t in out]; m = [x for x in m if x]
        L = np.array(w.log); seen.append(float(m[0].group(1)))
        i = np.argmax(400 - L[:, 2] < 150); true.append((400 - L[i, 2]) - (400 - L[-1, 2]))
    table.append((sp, min(seen), max(seen), min(true), max(true)))
    P(f"brake speed {sp}: program says {min(seen):.1f}-{max(seen):.1f} cm, true {min(true):.1f}-{max(true):.1f} cm")
w = sim2d.World([(-300, 400, 300, 400)], x=0, y=0, heading_deg=90, **wallsim.REAL)
w, out = C.run("brake_test.py", w, 12)
P("brake_test output:", [t for f, t in out])

# ---------- fig2: safety stop at speed 1.0 ----------
fig, (axl, axr) = plt.subplots(1, 2, figsize=(11.0, 4.4), dpi=200, gridspec_kw=dict(width_ratios=[1, 1.35]))
sps = [r[0] for r in table]
axl.bar(np.arange(4) - 0.18, [r[2] for r in table], 0.36, color="#A5D8FF", label="プログラムの表示（5回の最大）")
axl.bar(np.arange(4) + 0.18, [r[4] for r in table], 0.36, color="#1C7ED6", label="本当に進んだ距離（5回の最大）")
for i, r in enumerate(table):
    axl.text(i - 0.18, r[2] + 1, f"{r[2]:.0f}", ha="center", fontsize=8.5); axl.text(i + 0.18, r[4] + 1, f"{r[4]:.0f}", ha="center", fontsize=8.5)
axl.set_xticks(range(4)); axl.set_xticklabels([f"speed {s}" for s in sps], fontsize=9)
axl.set_ylabel("ブレーキから止まるまで〔cm〕"); axl.set_ylim(0, 65); axl.grid(axis="y", alpha=0.3)
axl.legend(fontsize=8.5, loc="upper left", frameon=False); axl.set_title("ブレーキテスト", fontsize=10.5)
runs = [("止まる距離をいつも 30 cm", [("STOP_BASE = 15.0 ", "STOP_BASE = 30.0 "), ("STOP_PER_SPEED = 60.0 ", "STOP_PER_SPEED = 0.0 ")], "#868E96"),
        ("止まる距離を速さに合わせる（15 ＋ 60 × speed）", [], "#E8590C")]
for lab, subs, col in runs:
    w = sim2d.World([(-300, 400, 300, 400)], x=0, y=0, heading_deg=90, **wallsim.REAL)
    w, out = C.run("safety_stop.py", w, 5, subs=subs, trig=lambda f, t: 1.0 if t == 1 else 0.0, joy=lambda f: (0.0, 0.0))
    L = np.array(w.log); gap = 400 - L[:, 2] - 12
    axr.plot(L[:, 0], gap, color=col, lw=2, label=lab + ("（ぶつかった）" if w.crashed else f"（{gap[-1]:.0f} cm で止まった）"))
    if w.crashed: axr.plot(L[-1, 0], gap[-1], "x", color=col, ms=10, mew=3)
    P(lab, "crashed" if w.crashed else f"stopped, bumper gap {gap[-1]:.1f}", [t for f, t in out if "安全停止！" in t])
axr.axhspan(-5, 0, color="#FFE3E3"); axr.set_ylim(-5, 120); axr.set_xlim(1.5, 4.5); axr.grid(alpha=0.3)
axr.set_xlabel("時間〔秒〕"); axr.set_ylabel("車の前のはしから壁まで〔cm〕")
axr.legend(fontsize=8.5, loc="upper right", frameon=True, framealpha=0.95)
axr.set_title("speed 1.0 で壁に向かって走る（右トリガーをいっぱい）", fontsize=10.5)
for a in (axl, axr):
    for s in ("top", "right"): a.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-stop.png", facecolor="white"); plt.close(fig)

# ---------- posts inside / outside the band ----------
for off in (15, 30):
    w = sim2d.World(sim2d.cone_segments(off, 300, radius=5.0), x=0, y=0, heading_deg=90, **wallsim.REAL)
    w, out = C.run("safety_stop.py", w, 8, subs=[("MAX_SPEED = 1.0 ", "MAX_SPEED = 0.5 ")], trig=lambda f, t: 1.0 if t == 1 else 0.0, joy=lambda f: (0.0, 0.0))
    L = np.array(w.log); P(f"post {off} cm to the right:", "crashed" if w.crashed else "", "stopped" if L[-1, 2] < 300 else "passed", [t for f, t in out if "安全停止！" in t])
