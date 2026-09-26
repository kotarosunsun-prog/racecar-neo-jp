"""Figure for 9-2: a made-up 2S LiPo (ch9/battery_model.py) run until BatteryGuard (ch9/battery_guard.py) says STOP.
Left: the whole run; right: a 14-second close-up where each 20 A burst pulls the voltage down by I x R."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "ch9"))
import battery_model as B
import battery_guard as G

OUT = "../images/racecar-neo-jp/9-2"
os.makedirs(OUT, exist_ok=True)
dt = 1 / 60
t, i, v, ocv = B.simulate(T=560, dt=dt)   # same run as the battery_monitor.py output on the page
guard = G.BatteryGuard()
t_warn = t_stop = None
for k in range(len(t)):
    s = guard.update(v[k], dt)
    if s == G.WARN and t_warn is None: t_warn = t[k]
    if s == G.STOP and t_stop is None: t_stop = t[k]; break
warn_v, stop_v = G.WARN_PER_CELL * G.CELLS, G.STOP_PER_CELL * G.CELLS
naive = t[np.argmax(v < warn_v)]
print("warn", t_warn, "stop", t_stop, "naive", naive)
end = int(t_stop / dt) + 60 * 8

fig = plt.figure(figsize=(11.2, 4.8), dpi=200)
ax = fig.add_axes([0.07, 0.13, 0.56, 0.74])
ax.plot(t[:end], v[:end], color="#1C7ED6", lw=0.5, label="電圧（電流が流れているとき）")
ax.plot(t[:end], ocv[:end], "--", color="#212529", lw=1.2, label="電流が流れていないときの電圧（目安）")
ax.axhline(warn_v, color="#F08C00", lw=1); ax.axhline(stop_v, color="#C92A2A", lw=1)
ax.text(5, warn_v + 0.03, f"注意 {warn_v:.1f} V（1 セル {G.WARN_PER_CELL} V）", color="#F08C00", fontsize=8.5)
ax.text(5, stop_v + 0.03, f"止まる {stop_v:.1f} V（1 セル {G.STOP_PER_CELL} V）", color="#C92A2A", fontsize=8.5)
for x, c, lab, y in ((naive, "#868E96", f"一瞬でも下回ったら\n注意にすると {naive:.0f} 秒", 8.33),
                     (t_warn, "#F08C00", f"注意 {t_warn:.0f} 秒", 8.33),
                     (t_stop, "#C92A2A", f"止まる {t_stop:.0f} 秒", 8.15)):
    ax.axvline(x, color=c, lw=1, ls=":")
    ax.text(x - 4, y, lab, color=c, fontsize=8, ha="right", va="top")
ax.set_xlim(0, t[end - 1]); ax.set_ylim(6.0, 8.45)
ax.set_xlabel("時間〔秒〕"); ax.set_ylabel("バッテリーの電圧〔V〕（2 セル）")
ax.legend(loc="lower left", fontsize=8.5, frameon=False)
ax.set_title("説明用の簡単なモデル：走りながら電圧が下がっていく", fontsize=10)
for s in ("top", "right"): ax.spines[s].set_visible(False)

a2 = fig.add_axes([0.72, 0.13, 0.26, 0.74])
t0 = 300.0
m = (t >= t0) & (t < t0 + 14)
a2.plot(t[m], v[m], color="#1C7ED6", lw=0.8)
a2.plot(t[m], ocv[m], "--", color="#212529", lw=1.2)
tb = t0 + 6.5   # inside a burst (bursts start every 6 s)
k = int(tb / dt)
a2.annotate("", xy=(tb, v[k]), xytext=(tb, ocv[k]), arrowprops=dict(arrowstyle="<->", color="#C92A2A"))
a2.text(tb + 0.3, (v[k] + ocv[k]) / 2, f"20 A × {B.R_PACK} Ω\n= {20 * B.R_PACK:.1f} V 下がる", color="#C92A2A",
        fontsize=8.5, va="center")
a2.set_xlabel("時間〔秒〕"); a2.set_title(f"{t0:.0f}〜{t0 + 14:.0f} 秒を拡大\n（6 秒ごとに 1 秒、加速で 20 A）", fontsize=9)
for s in ("top", "right"): a2.spines[s].set_visible(False)
fig.savefig(os.path.join(OUT, "fig1-battery.png"))
