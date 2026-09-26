"""Figure for 8-2 (sim2d model): the stop time of grand_prix.py for each setting (5 runs each), and where the time goes.
Reads ch8/tune8/NAME.json, written by ch8/tune8.py (run that first for every NAME below)."""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "../images/racecar-neo-jp/8-2"
os.makedirs(OUT, exist_ok=True)
ROWS = json.loads(sys.argv[1])            # [[NAME, label], ...] from top to bottom
BASE, FINAL = sys.argv[2], sys.argv[3]
data = {n: json.load(open(os.path.join(HERE, "ch8", "tune8", n + ".json"))) for n, _ in ROWS}

fig = plt.figure(figsize=(11.2, 5.4), dpi=200)
ax = fig.add_axes([0.25, 0.13, 0.36, 0.75])
for k, (n, lab) in enumerate(ROWS):
    y = len(ROWS) - 1 - k
    ok = [r["stop"] for r in data[n] if r["stop"] is not None and not r["crashed"]]
    bad = [r for r in data[n] if r["stop"] is None or r["crashed"]]
    if ok:
        ax.plot([min(ok), max(ok)], [y, y], color="#ADB5BD", lw=6, solid_capstyle="round", zorder=1)
        ax.plot(ok, [y] * len(ok), "o", color="#1C7ED6", ms=5, zorder=2)
    for j, r in enumerate(bad):
        ax.plot(88 + j * 1.5, y, "x", color="#C92A2A", ms=8, mew=2.5)
    note = f"{len(ok)}/5 回" + (f"　{min(ok):.1f}〜{max(ok):.1f} 秒" if ok else "")
    ax.text(91 + 1.5 * len(bad), y, note, va="center", fontsize=8.5, color="#495057")
ax.set_yticks(range(len(ROWS))); ax.set_yticklabels([lab for _, lab in ROWS][::-1], fontsize=8.5)
ax.set_xlim(45, 90); ax.set_xlabel("止まるまでの時間〔秒〕（青い点が1回ずつ。灰色の帯は、いちばん速い回から遅い回まで）")
ax.grid(axis="x", alpha=0.3)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.set_title("設定ごとの、止まるまでの時間（5 回ずつ）", fontsize=10)

a2 = fig.add_axes([0.8, 0.13, 0.17, 0.75])
parts = [("線", "line_end", "#74C0FC"), ("通路", "turn", "#868E96"), ("分かれ道〜ゴール", "stop", "#FFA94D")]
for x, n in enumerate((BASE, FINAL)):
    rows = [r for r in data[n] if r["stop"] is not None]
    prev = np.zeros(len(rows)); bottom = 0.0
    for lab, key, col in parts:
        t = np.array([r[key] for r in rows]); seg = float(np.mean(t - prev)); prev = t
        a2.bar(x, seg, bottom=bottom, color=col, width=0.6, label=lab if x == 0 else None)
        a2.text(x, bottom + seg / 2, f"{seg:.1f}", ha="center", va="center", fontsize=8.5)
        bottom += seg
a2.set_xticks([0, 1]); a2.set_xticklabels(["はじめ", "調整後"], fontsize=9)
a2.set_ylabel("平均の時間〔秒〕"); a2.set_ylim(0, 100); a2.legend(fontsize=8, loc="upper right", frameon=False, ncol=1)
for s in ("top", "right"): a2.spines[s].set_visible(False)
a2.set_title("区間ごとの時間", fontsize=10)
fig.suptitle("1つずつ変えて、5 回ずつ走らせる（説明用の簡単なモデル）", fontsize=11)
fig.savefig(f"{OUT}/fig1-tuning.png", facecolor="white"); plt.close(fig)
