"""Figure for 6-7: P-only wall following with three gains (sim2d model, realistic LIDAR).
The car starts 70 cm from the right wall (target 50 cm), speed 0.3, for 15 seconds."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import wallsim
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-7"
WALLS = [(100, -200, 100, 4000), (-100, -200, -100, 4000)]

fig, ax = plt.subplots(figsize=(10.4, 4.4), dpi=200)
ax.axhspan(-8, 0, color="#CED4DA"); ax.axhline(0, color="#495057", lw=2)
ax.text(10, -4, "右の壁", va="center", fontsize=9)
ax.axhline(50, color="#2F9E44", ls="--", lw=1.2); ax.text(690, 50, "目標\n50 cm", color="#2B8A3E", fontsize=9, va="center")
for kp, col in [(0.01, "#1C7ED6"), (0.02, "#E8590C"), (0.04, "#AE3EC9")]:
    o, crashed = wallsim.simulate(WALLS, wallsim.P(kp), 0.3, 15, x=30)
    dist = 100 - o[:, 1]
    lab = f"KP = {kp}" + ("（壁にぶつかった）" if crashed else "")
    ax.plot(o[:, 2], dist, color=col, lw=2, label=lab)
    if crashed:
        ax.plot([o[-1, 2]], [dist[-1]], "x", color=col, ms=10, mew=3)
    print(kp, crashed, round(o[-1, 0], 1), round(dist.min(), 1), round(dist.max(), 1))
ax.plot([0], [70], "o", color="#212529", ms=6); ax.text(8, 74, "スタート（壁から 70 cm）", fontsize=9)
ax.set_xlim(0, 720); ax.set_ylim(-8, 100); ax.grid(alpha=0.3)
ax.set_xlabel("進んだ距離〔cm〕"); ax.set_ylabel("右の壁までの距離〔cm〕")
ax.legend(fontsize=9, loc="upper right", ncol=3, frameon=False)
ax.set_title("P 制御だけで壁沿いに走った道すじ（speed 0.3、15 秒、説明用の簡単なモデル）", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-paths.png", facecolor="white"); plt.close(fig)
o, crashed = wallsim.simulate(WALLS, wallsim.P(0.02), 0.5, 15, x=30)
print("KP 0.02, speed 0.5:", f"crashed at {o[-1, 0]:.1f} s" if crashed else "no crash")
