"""Figure for 9-5 (sim2d model + the made-up Edge TPU in ch9/mock_vision.py): detect_stop.py with and without
CONFIRM_TIME, seed 0. Reads ch9/data/stop.json written by ch9/stop_run.py."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "../images/racecar-neo-jp/9-5"
os.makedirs(OUT, exist_ok=True)
data = json.load(open(os.path.join(HERE, "ch9", "data", "stop.json")))
SIGNS_Y = [900, 1800]

fig, axes = plt.subplots(2, 1, figsize=(11.2, 6.2), dpi=200, sharex=True)
for ax, key, title in ((axes[0], "naive", "標識が 1 回見えたら止まる"),
                       (axes[1], "filtered", "0.2 秒続けて見えたら止まる（detect_stop.py）")):
    d = data[key]
    t, y = np.array(d["t"]), np.array(d["y"])
    ax.plot(t, y / 100, color="#212529", lw=1.8)
    for k, (ts, s) in enumerate(d["states"]):
        if s == "STOP へ":
            ax.axvspan(ts, ts + 3, color="#FFC9C9", zorder=0)
    for sy in SIGNS_Y:
        ax.axhline(sy / 100, color="#C92A2A", lw=0.8, ls="--")
        ax.text(60.5, sy / 100, "標識", color="#C92A2A", fontsize=8.5, va="center")
    fr = [f / 60 for f, kind, h in d["vlog"] if kind == "false"]
    ok = [f / 60 for f, kind, h in d["vlog"] if kind == "true" and h >= 60]
    ax.plot(fr, [-1.5] * len(fr), "x", color="#E8590C", ms=7, mew=2, label="まちがった答え（標識がないのに「ある」）")
    ax.plot(ok, [-2.6] * len(ok), "|", color="#1C7ED6", ms=8, mew=1.2, label="近くの本当の標識の答え（1 秒に 15 回まで）")
    ax.set_ylim(-3.3, 31); ax.set_xlim(0, 63)
    ax.set_ylabel("位置〔m〕")
    stops = data[key + "0"]["stops"]
    good = sum(1 for _, sy in stops if any(s - 200 <= sy <= s for s in SIGNS_Y))
    ax.set_title(f"{title}：止まった {len(stops)} 回（標識の前 {good} 回、それ以外 {len(stops) - good} 回）", fontsize=10)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
axes[0].legend(loc="upper left", fontsize=8.5, frameon=False)
axes[1].set_xlabel("時間〔秒〕（赤い帯：止まっている 3 秒）")
fig.text(0.5, 0.005, "説明用の簡単なモデル（標識の見え方と、まちがった答えは、この本で作ったもの）", ha="center", fontsize=8.5,
         color="#495057")
fig.tight_layout(rect=(0, 0.02, 1, 1))
fig.savefig(os.path.join(OUT, "fig1-detect-stop.png"))
