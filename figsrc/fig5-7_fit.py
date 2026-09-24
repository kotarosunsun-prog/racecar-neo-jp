"""Figure for 5-7: data, three candidate lines with their losses, and residuals for one line."""
import os, io, contextlib, runpy, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/5-7"; os.makedirs(OUT, exist_ok=True)
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("fig5-7_regression_loss.py")
x, y, loss = g["x"], g["y"], g["loss"]
fig, axs = plt.subplots(1, 2, figsize=(10, 4.2), dpi=200)
xx = np.linspace(0.05, 0.65, 50)
cols = {"A": "#F08C00", "B": "#AE3EC9", "C": "#2F9E44"}
for (name, w, b) in [("A", 2.0, 0.0), ("B", 3.0, -0.3), ("C", 2.4, -0.1)]:
    axs[0].plot(xx, w * xx + b, color=cols[name], lw=2, label=f"{name}：w={w}, b={b}（損失 {loss(w, b):.4f}）")
axs[0].scatter(x, y, color="#212529", zorder=5, s=24, label="測ったデータ")
axs[0].set_xlabel("アクセルの値 x"); axs[0].set_ylabel("速さ y〔m/s〕"); axs[0].legend(fontsize=8.5, loc="upper left", frameon=False)
axs[0].set_title("3本の直線の候補", fontsize=11); axs[0].grid(alpha=0.3)
w, b = 2.0, 0.0
axs[1].plot(xx, w * xx + b, color=cols["A"], lw=2, label="A：y = 2.0 x")
for xi, yi in zip(x, y):
    axs[1].plot([xi, xi], [w * xi + b, yi], color="#E03131", lw=1.6)
axs[1].scatter(x, y, color="#212529", zorder=5, s=24)
axs[1].plot([], [], color="#E03131", lw=1.6, label="誤差（実際 − 予想）")
axs[1].set_xlabel("アクセルの値 x"); axs[1].legend(fontsize=9, loc="upper left", frameon=False)
axs[1].set_title("直線 A の誤差：これを2乗して平均したものが損失", fontsize=11); axs[1].grid(alpha=0.3)
for ax in axs:
    for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-fit.png", facecolor="white"); plt.close(fig)
