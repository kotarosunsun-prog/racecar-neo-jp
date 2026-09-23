import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import numpy as np
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=200)
V = np.linspace(0, 6, 50)
cols = {1: "#1C7ED6", 2: "#0CA678", 3: "#D9480F"}
for R, c in cols.items():
    ax.plot(V, V / R, color=c, lw=2.4)
    ax.text(6.08, 6 / R, f"R = {R} Ω", color=c, va="center", fontsize=11, fontweight="bold")
ax.plot([3], [1], "o", color="#D9480F", ms=8, zorder=5)
ax.annotate("懐中電灯に 3 V\n→ 1 A 流れる", (3, 1), xytext=(3.6, 0.35), fontsize=10.5,
            arrowprops=dict(arrowstyle="->", color="#495057"))
ax.plot([1.5], [0.5], "o", mfc="white", mec="#D9480F", mew=2, ms=8, zorder=5)
ax.annotate("単三電池1本（1.5 V）だと\n0.5 A しか流れない", (1.5, 0.5), xytext=(0.15, 2.1), fontsize=10.5,
            arrowprops=dict(arrowstyle="->", color="#495057"))
ax.set_xlim(0, 6); ax.set_ylim(0, 6.3)
ax.set_xlabel("電圧 V〔V〕", fontsize=12); ax.set_ylabel("電流 I〔A〕", fontsize=12)
ax.set_title("抵抗が同じなら、電流は電圧に比例する", fontsize=13)
ax.grid(alpha=0.3)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(rect=(0, 0, 0.93, 1))
fig.savefig("images/racecar-neo-jp/9-2/fig3-vi-graph.png", facecolor="white")
