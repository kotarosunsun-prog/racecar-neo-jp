"""Figure for 6-1: approaching a wall with on-off control vs proportional control (sim2d model)."""
import os, math, numpy as np, sim2d
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-1"
DT, TARGET = 1 / 60, 50.0

def front_distance(scan):
    idx = np.r_[700:720, 0:21]; s = scan[idx]; s = s[s > 0]
    return s.min() if len(s) else 1e6

def run(controller, seconds=6.0):
    w = sim2d.World([(-200, 300, 200, 300)], x=0, y=0, heading_deg=90)
    t, d = [], []
    for k in range(int(seconds / DT)):
        f = front_distance(w.scan())
        w.step(DT, controller(f), 0.0)
        t.append(w.t); d.append(300 - w.y)
    return np.array(t), np.array(d)

fig, ax = plt.subplots(figsize=(8.0, 4.4), dpi=200)
ax.axhline(TARGET, color="#212529", ls="--", lw=1.2); ax.text(5.95, TARGET + 6, "目標 50 cm", ha="right", fontsize=10)
t, d = run(lambda f: 1.0 if f > TARGET else -1.0)
ax.plot(t, d, color="#E03131", lw=2, label="オン・オフ（遠ければ全開で前、近ければ全開で後ろ）")
for kp, col in [(0.005, "#F08C00"), (0.02, "#2F9E44"), (0.1, "#1C7ED6")]:
    t, d = run(lambda f, kp=kp: max(-1.0, min(1.0, kp * (f - TARGET))))
    ax.plot(t, d, color=col, lw=2.2, label=f"比例制御 KP = {kp}")
ax.set_xlabel("時間〔秒〕"); ax.set_ylabel("壁までの距離〔cm〕"); ax.set_ylim(0, 310); ax.set_xlim(0, 6)
ax.grid(alpha=0.3); ax.legend(fontsize=9, loc="upper right", frameon=False)
ax.set_title("壁の手前 50 cm で止まる（説明用の簡単なモデル）", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-stop.png", facecolor="white"); plt.close(fig)
