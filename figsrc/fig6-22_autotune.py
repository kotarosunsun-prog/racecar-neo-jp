"""Figure for 6-22: the loss of auto_tune.py over (KP, KA) with the path of gradient descent,
and the tuned gains tried in the sim2d model (start 100 cm from the right wall, target 50 cm, speed 0.5)."""
import io, contextlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import wallsim
from pid_book import PID
with contextlib.redirect_stdout(io.StringIO()):
    import auto_tune_book as A          # the book's auto_tune.py (runs its descent once on import)
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-22"


def descend(kp, ka, steps=300):
    path = [(kp, ka)]
    for _ in range(steps):
        gk = (A.loss(kp + A.H, ka) - A.loss(kp - A.H, ka)) / (2 * A.H)
        ga = (A.loss(kp, ka + A.H) - A.loss(kp, ka - A.H)) / (2 * A.H)
        kp, ka = kp - A.LR * gk, ka - A.LR * ga
        path.append((kp, ka))
    return np.array(path)


KP = np.linspace(0.004, 0.08, 153); KA = np.linspace(0.004, 0.13, 127)
Z = np.array([[A.loss(kp, ka) for kp in KP] for ka in KA])
path = descend(0.01, 0.01)
print("end", path[-1], A.loss(*path[-1]))
for start in [(0.07, 0.01), (0.05, 0.12), (0.002, 0.002)]:
    p = descend(*start); print("start", start, "end", np.round(p[-1], 4), round(A.loss(*p[-1]), 3))

W = [(100, -200, 100, 6000), (-100, -200, -100, 6000)]
runs = [("はじめ（KP 0.01、KA 0.01）", (0.01, 0.01), "#868E96"),
        (f"勾配降下法の答え（KP {path[-1][0]:.4f}、KA {path[-1][1]:.4f}）", tuple(path[-1]), "#E8590C"),
        ("6-10 で決めた値（KP 0.02、KA 0.04）", (0.02, 0.04), "#1C7ED6")]

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.6, 5.2), dpi=200, gridspec_kw=dict(width_ratios=[1, 1.15]))
crash = Z >= 1000
Zc = np.where(crash, np.nan, Z)
cs = ax.contourf(KP, KA, np.log10(Zc), levels=np.linspace(np.log10(3.8), np.log10(60), 16), cmap="viridis_r", extend="max")
ax.contour(KP, KA, np.log10(Zc), levels=np.linspace(np.log10(3.8), np.log10(60), 16), colors="white", linewidths=0.4, alpha=0.5)
ax.contourf(KP, KA, crash.astype(float), levels=[0.5, 1.5], colors=["#FFC9C9"])
ax.text(0.068, 0.012, "ぶつかる", color="#C92A2A", fontsize=10, ha="center", va="center")
ax.plot(path[:, 0], path[:, 1], "-", color="#E8590C", lw=2)
ax.plot(path[::10, 0], path[::10, 1], "o", color="#E8590C", ms=3)
ax.plot(*path[0], "o", color="#212529", ms=7); ax.text(path[0][0] - 0.001, path[0][1] + 0.004, "はじめ", fontsize=9, ha="right")
ax.plot(*path[-1], "*", color="#E8590C", ms=15, mec="white"); ax.text(path[-1][0] + 0.003, path[-1][1] - 0.004, "300 回め", fontsize=9, color="#D9480F")
ax.plot(0.02, 0.04, "s", color="#1C7ED6", ms=7); ax.text(0.023, 0.043, "6-10 の値", fontsize=9, color="#1864AB")
ax.plot(0.04, 0.04, "D", color="#7048E8", ms=6); ax.text(0.043, 0.036, "6-14 の値（I なし）", fontsize=9, color="#5F3DC4")
ax.set_xlabel("KP（ずれ 1 cm あたり）"); ax.set_ylabel("KA（壁の向き 1° あたり）")
ax.set_title("損失の地図と、勾配降下法で進んだ道すじ", fontsize=10.5)
cb = fig.colorbar(cs, ax=ax, fraction=0.05, pad=0.02); cb.set_label("損失（黄色いほど小さい）", fontsize=9)
cb.set_ticks(np.log10([4, 5, 7, 10, 20, 40])); cb.set_ticklabels(["4", "5", "7", "10", "20", "40"])

for lab, g, col in runs:
    o, crashed = wallsim.simulate(W, wallsim.WallPID(PID(g[0], 0.0, g[1], i_zone=20)), 0.5, 12, x=0.0)
    rows = wallsim.log_rows(o); m = wallsim.metrics(rows)
    t = [r[0] for r in rows]; d = [r[1] for r in rows]
    ax2.plot(t, d, color=col, lw=1.8, label=lab)
    print(lab, {k: (round(v, 2) if v is not None else None) for k, v in m.items()})
ax2.axhspan(47.5, 52.5, color="#EBFBEE"); ax2.axhline(50, color="#2F9E44", ls="--", lw=1)
ax2.set_xlim(0, 12); ax2.set_ylim(20, 105); ax2.grid(alpha=0.3)
ax2.set_xlabel("時間〔秒〕"); ax2.set_ylabel("右の壁までの距離〔cm〕")
ax2.legend(fontsize=8.5, loc="upper right", frameon=True, framealpha=0.95)
ax2.set_title("説明用の簡単なモデル（6-13 と同じ走らせ方）で試す", fontsize=10.5)
for s in ("top", "right"): ax2.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-descent.png", facecolor="white"); plt.close(fig)
