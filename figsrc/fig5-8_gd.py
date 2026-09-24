"""Figures for 5-8: (1) loss vs w with slope and step, (2) contour paths and learning-rate comparison."""
import os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/5-8"; os.makedirs(OUT, exist_ok=True)
x = np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60])
y = np.array([0.12, 0.29, 0.41, 0.46, 0.59, 0.70, 0.86, 0.96, 1.11, 1.13, 1.38])
def loss(w, b): return np.mean((y - (w * x + b)) ** 2)
def grads(w, b):
    e = y - (w * x + b); return -2 * np.mean(x * e), -2 * np.mean(e)
B = -0.101
# ---------- fig1: 1-D slice ----------
ws = np.linspace(1.6, 3.15, 200); Ls = [loss(w, B) for w in ws]
fig, ax = plt.subplots(figsize=(7.4, 4.2), dpi=200)
ax.plot(ws, Ls, color="#1C7ED6", lw=2.4, label="損失（b = −0.101 のまま、w だけ変えたとき）")
for w0, col, txt, tpos in [(1.9, "#E8590C", "傾きがマイナス\n→ w を増やす", (1.98, 0.058)),
                           (2.85, "#AE3EC9", "傾きがプラス\n→ w を減らす", (2.36, 0.058))]:
    L0 = loss(w0, B); g = grads(w0, B)[0]
    tx = np.linspace(w0 - 0.18, w0 + 0.18, 2)
    ax.plot(tx, L0 + g * (tx - w0), color=col, lw=2)
    ax.scatter([w0], [L0], color=col, zorder=5, s=40)
    step = 0.22 if g < 0 else -0.22
    ax.annotate("", xy=(w0 + step, L0 - 0.012), xytext=(w0, L0 - 0.012), arrowprops=dict(arrowstyle="-|>", color=col, lw=2))
    ax.text(*tpos, txt, color=col, fontsize=10)
wbest = ws[np.argmin(Ls)]
ax.scatter([wbest], [min(Ls)], color="#2F9E44", zorder=5, s=50)
ax.text(wbest, min(Ls) + 0.006, "いちばん低い点（傾き 0）", ha="center", va="bottom", fontsize=10, color="#2B8A3E")
ax.set_xlabel("w"); ax.set_ylabel("損失 L"); ax.set_ylim(-0.005, 0.105); ax.set_xlim(1.55, 3.2); ax.grid(alpha=0.3)
ax.legend(loc="upper center", fontsize=9, frameon=False)
ax.set_title("損失の「坂」を、傾きと反対の向きに下る", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-slope.png", facecolor="white"); plt.close(fig)

# ---------- fig2: contour paths + learning rates ----------
def run(lr, steps):
    w = b = 0.0; path = [(w, b)]; hist = []
    for _ in range(steps):
        hist.append(loss(w, b)); gw, gb = grads(w, b); w -= lr * gw; b -= lr * gb; path.append((w, b))
        if not np.isfinite(w) or abs(w) > 1e6: break
    return np.array(path), np.array(hist)
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.4), dpi=200)
W, Bg = np.meshgrid(np.linspace(-0.2, 3.2, 200), np.linspace(-0.5, 0.9, 200))
Z = np.vectorize(loss)(W, Bg)
cs = axs[0].contour(W, Bg, Z, levels=[0.002, 0.01, 0.03, 0.07, 0.15, 0.3, 0.6], colors="#ADB5BD", linewidths=1)
axs[0].clabel(cs, fontsize=7, fmt="%.3g")
for lr, col, lab in [(0.05, "#F08C00", "学習率 0.05"), (0.5, "#2F9E44", "学習率 0.5")]:
    p, _ = run(lr, 300)
    axs[0].plot(p[:, 0], p[:, 1], ".-", color=col, ms=3, lw=1.2, label=f"{lab}（300回）")
axs[0].scatter([2.369], [-0.101], marker="*", s=160, color="#E03131", zorder=6, label="いちばん低い点")
axs[0].scatter([0], [0], s=40, color="#212529", zorder=6); axs[0].text(0.05, 0.03, "スタート", fontsize=9)
axs[0].set_xlabel("w"); axs[0].set_ylabel("b"); axs[0].legend(fontsize=8.5, loc="upper right", framealpha=0.95)
axs[0].set_title("損失の等高線と、進んだ道すじ", fontsize=11)
for lr, col, lab in [(0.05, "#F08C00", "0.05（ゆっくり）"), (0.5, "#2F9E44", "0.5（ちょうどよい）"), (0.95, "#E03131", "0.95（大きすぎて発散）")]:
    _, h = run(lr, 300)
    axs[1].plot(np.arange(len(h)), h, color=col, lw=2, label=f"学習率 {lab}")
axs[1].set_yscale("log"); axs[1].set_ylim(1e-3, 1e3); axs[1].set_xlim(0, 300)
axs[1].set_xlabel("くり返した回数"); axs[1].set_ylabel("損失（目もりは10倍ごと）")
axs[1].legend(fontsize=9, frameon=False); axs[1].set_title("学習率による違い", fontsize=11); axs[1].grid(alpha=0.3)
for ax in axs:
    for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-paths.png", facecolor="white"); plt.close(fig)
print("lr0.05 after 300:", run(0.05, 300)[1][-1], " lr0.95 after 50:", run(0.95, 50)[1][-1])
