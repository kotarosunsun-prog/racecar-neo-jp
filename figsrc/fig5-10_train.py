"""Figure for 5-10: loss during training, and the trained network's output over H."""
import os, io, contextlib, runpy, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/5-10"
# re-run the same training while recording the loss
src = open("fig5-10_backprop_red.py").read()
src = src.replace("for step in range(20001):", "LOSSES = []\nfor step in range(20001):").replace(
    "    loss = np.mean((a2 - y) ** 2)      # 損失（平均二乗誤差）", "    loss = np.mean((a2 - y) ** 2)      # 損失（平均二乗誤差）\n    LOSSES.append(loss)")
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, "bp", "exec"), g)
L = np.array(g["LOSSES"]); ht, at = g["h_test"], g["a_test"]
fig, axs = plt.subplots(1, 2, figsize=(10.2, 3.9), dpi=200)
axs[0].plot(np.arange(len(L)), L, color="#1C7ED6", lw=2)
axs[0].set_yscale("log"); axs[0].set_xlabel("くり返した回数"); axs[0].set_ylabel("損失（目もりは10倍ごと）")
axs[0].set_title("学習が進むと、損失が下がる", fontsize=11); axs[0].grid(alpha=0.3)
truth = ((ht < 10) | (ht > 170)).astype(float)
axs[1].fill_between(ht, 0, truth, step="mid", color="#E03131", alpha=0.18, label="正解（赤 = 1）")
axs[1].plot(ht, at, color="#E03131", lw=2.4, label="学習したネットワークの出力")
axs[1].axhline(0.5, color="#868E96", ls="--", lw=1); axs[1].text(90, 0.53, "0.5 より大きければ「赤」", ha="center", fontsize=9, color="#495057")
axs[1].set_xlabel("色合い H"); axs[1].set_ylabel("赤である確からしさ"); axs[1].set_ylim(-0.05, 1.12)
axs[1].set_xticks([0, 10, 30, 60, 90, 120, 150, 170])
axs[1].legend(fontsize=9, loc="upper center", frameon=False, ncol=2, bbox_to_anchor=(0.5, 1.02))
axs[1].set_title("学習したあとの出力", fontsize=11, pad=18)
for ax in axs:
    for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-training.png", facecolor="white"); plt.close(fig)
print(L[0], L[1000], L[5000], L[-1])
