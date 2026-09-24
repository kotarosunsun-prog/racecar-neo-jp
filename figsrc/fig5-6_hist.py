"""Figure for 5-6: hue histograms of the two classes and the threshold learned from the training data."""
import os, io, contextlib, runpy, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/5-6"; os.makedirs(OUT, exist_ok=True)
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("fig5-6_learn_threshold.py")
h, label, train, best = g["h"], g["label"], g["train"], g["best"]
fig, ax = plt.subplots(figsize=(7.6, 3.8), dpi=200)
bins = np.arange(40, 131, 3)
ax.hist(h[train][label[train] == 0], bins=bins, color="#40C057", alpha=0.75, label="緑の箱（正解 0）")
ax.hist(h[train][label[train] == 1], bins=bins, color="#339AF0", alpha=0.75, label="青の箱（正解 1）")
ax.axvline(best + 0.5, color="#E8590C", lw=2.4)
ax.text(best + 1.5, ax.get_ylim()[1] * 0.92, f"学習で選んだしきい値\nH > {best} なら青", color="#D9480F", fontsize=10, va="top")
ax.set_xlabel("色合い H（OpenCV の値）"); ax.set_ylabel("データの数")
ax.set_title("学習用データの H の分布と、データから選んだしきい値（作ったデータ）", fontsize=11)
ax.legend(loc="upper left", fontsize=9, frameon=False)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-threshold.png", facecolor="white"); plt.close(fig)
