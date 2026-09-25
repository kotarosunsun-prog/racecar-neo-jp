"""Figures for 6-9 (sim2d model, realistic LIDAR, speed 0.5, starting 100 cm from the right wall).
fig1: the rate of change measured over 1 frame vs over 10 frames, and what it does to the steering.  fig2: P only vs P + D."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import wallsim
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-9"
WALLS = [(100, -200, 100, 4000), (-100, -200, -100, 4000)]

# ---------- fig1 ----------
fig, ax = plt.subplots(figsize=(10.4, 4.4), dpi=200)
ax.axhspan(-8, 0, color="#CED4DA"); ax.axhline(0, color="#495057", lw=2); ax.text(10, -4, "右の壁", va="center", fontsize=9)
ax.axhline(50, color="#2F9E44", ls="--", lw=1.2); ax.text(752, 50, "目標\n50 cm", color="#2B8A3E", fontsize=9, va="center")
runs = [("P だけ（KP 0.02）", wallsim.P(0.02), "#868E96"),
        ("P ＋ D（KP 0.02、KD 0.01）", wallsim.PD(0.02, 0.01, 10), "#1C7ED6"),
        ("P ＋ D（KP 0.02、KD 0.03）", wallsim.PD(0.02, 0.03, 10), "#E8590C")]
for lab, ctrl, col in runs:
    o, crashed = wallsim.simulate(WALLS, ctrl, 0.5, 10, x=0)
    d = 100 - o[:, 1]
    ax.plot(o[:, 2], d, color=col, lw=2, label=lab + ("（壁にぶつかった）" if crashed else ""))
    if crashed: ax.plot([o[-1, 2]], [d[-1]], "x", color=col, ms=10, mew=3)
    after = d[o[:, 2] > 100]
    print(lab, "crashed" if crashed else "", "min", round(d.min(), 1), "final", round(d[-60:].mean(), 1))
ax.plot([0], [100], "o", color="#212529", ms=6); ax.text(8, 96, "スタート（壁から 100 cm）", fontsize=9, va="top")
ax.set_xlim(0, 790); ax.set_ylim(-8, 108); ax.grid(alpha=0.3)
ax.set_xlabel("進んだ距離〔cm〕"); ax.set_ylabel("右の壁までの距離〔cm〕")
ax.legend(fontsize=9, loc="upper right", frameon=False)
ax.set_title("D を足すと、行き過ぎずに目標の線に落ち着く（speed 0.5、10 秒、説明用の簡単なモデル）", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-pd.png", facecolor="white"); plt.close(fig)

# ---------- fig2 ----------
ctrl = wallsim.PD(0.02, 0.03, 10)
o, _ = wallsim.simulate(WALLS, ctrl, 0.5, 10, x=0)
t = o[:, 0]; meas_e = o[:, 5] - 50
true_d = 100 - o[:, 1]
true_rate = np.gradient(true_d, t)
rate1 = np.r_[0, np.diff(meas_e) / wallsim.DT]
rate10 = np.array([(meas_e[i] - meas_e[max(0, i - 10)]) / (max(1, min(i, 10)) * wallsim.DT) if i > 0 else 0 for i in range(len(meas_e))])
o1, crashed1 = wallsim.simulate(WALLS, wallsim.PD(0.02, 0.03, 1), 0.5, 10, x=0)
print("1-frame D crashed:", crashed1, "at", round(o1[-1, 0], 2), "s")

fig, (a1, a2) = plt.subplots(2, 1, figsize=(10.4, 6.6), dpi=200, sharex=True)
m = t <= 3
a1.plot(t[m], rate1[m], color="#ADB5BD", lw=1.0, label="1コマで求めた速さ")
a1.plot(t[m], rate10[m], color="#E8590C", lw=2.0, label="10コマで求めた速さ（RATE_FRAMES = 10）")
a1.plot(t[m], true_rate[m], color="#212529", lw=1.2, ls="--", label="本当の速さ（モデルの答え）")
a1.set_ylim(-160, 160); a1.set_ylabel("ずれの変わる速さ〔cm/秒〕"); a1.grid(alpha=0.3)
a1.legend(fontsize=9, loc="upper right", frameon=True, framealpha=0.9)
a1.set_title("同じ測った値から求めた「ずれの変わる速さ」", fontsize=10.5, loc="left")
m1 = o1[:, 0] <= 3
a2.plot(o1[m1, 0], o1[m1, 4], color="#ADB5BD", lw=1.2, label="1コマで求めた速さを使った走り")
a2.plot(o[m, 0], o[m, 4], color="#E8590C", lw=2.0, label="10コマで求めた速さを使った走り")
if crashed1:
    a2.axvline(o1[-1, 0], color="#868E96", ls=":", lw=1.2)
    a2.text(o1[-1, 0] + 0.03, -0.8, "1コマのほうは\nここで壁にぶつかった", fontsize=9, color="#495057", va="center")
a2.set_ylim(-1.1, 1.1); a2.set_ylabel("angle"); a2.set_xlabel("時間〔秒〕"); a2.grid(alpha=0.3)
a2.legend(fontsize=9, loc="upper right", frameon=True, framealpha=0.9)
a2.set_title("ハンドルの命令（angle）", fontsize=10.5, loc="left")
a2.set_xlim(0, 3)
for a in (a1, a2):
    for s in ("top", "right"): a.spines[s].set_visible(False)
fig.suptitle("速さを1コマで求めると、ノイズと LIDAR の回転のせいでとげとげになる（説明用の簡単なモデル）", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-rate.png", facecolor="white"); plt.close(fig)
print("rate sd (t in 1..3 s): 1-frame", round(np.std((rate1 - true_rate)[(t > 1) & m]), 1), " 10-frame", round(np.std((rate10 - true_rate)[(t > 1) & m]), 1))

# ---------- the RATE_FRAMES table in the text (KD 0.03) ----------
for n in (1, 5, 10, 20):
    o, crashed = wallsim.simulate(WALLS, wallsim.PD(0.02, 0.03, n), 0.5, 10, x=0)
    d = 100 - o[:, 1]
    print(f"RATE_FRAMES {n:2d}: {'crashed at %.1f s' % o[-1, 0] if crashed else 'final %.1f cm' % d[-60:].mean()}, "
          f"steering jitter {np.std(np.diff(o[:, 4])):.3f}")
o, crashed = wallsim.simulate(WALLS, wallsim.PD(0.02, 0.03, 1), 0.5, 10, x=0, kw=wallsim.IDEAL)
print("1-frame D with an exact LIDAR:", "crashed" if crashed else "ok", f"min {(100 - o[:, 1]).min():.1f} cm")
