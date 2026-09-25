"""Figures for 6-11 (sim2d model, realistic LIDAR).
fig1: following the wall of a round room (radius 250 cm) with and without I.
fig2: 6-1's stop-at-wall task with friction: P vs P + I."""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import wallsim
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-11"
R = 250
WALLS = wallsim.circle(R)

# ---------- fig1 ----------
runs = [("I なし（KI = 0）", 0.0, "#868E96"), ("KI = 0.005", 0.005, "#E8590C"), ("KI = 0.02", 0.02, "#AE3EC9")]
res = {}
for lab, ki, col in runs:
    o, crashed = wallsim.simulate(WALLS, wallsim.PIA(0.02, ki, 0.04), 0.5, 20, x=R - 50,
                                  extra=lambda c: (c.ki * c.integral,))
    res[ki] = o
    d = R - np.hypot(o[:, 1], o[:, 2])
    print(lab, "crashed" if crashed else "", f"final {d[-120:].mean():.2f} min {d.min():.1f} max {d.max():.1f}")
fig = plt.figure(figsize=(11.0, 4.9), dpi=200)
axA = fig.add_axes([0.02, 0.1, 0.30, 0.78]); axB = fig.add_axes([0.40, 0.14, 0.58, 0.72])
th = np.linspace(0, 2 * np.pi, 361)
axA.plot(R * np.cos(th), R * np.sin(th), color="#495057", lw=3)
axA.plot((R - 50) * np.cos(th), (R - 50) * np.sin(th), color="#2F9E44", lw=1, ls="--")
for lab, ki, col in runs[:2]:
    o = res[ki]; m = o[:, 0] >= 8
    axA.plot(o[m, 1], o[m, 2], color=col, lw=2, label=lab)
axA.text(0, 0, "丸い部屋\n（半径 250 cm）", ha="center", va="center", fontsize=9, color="#495057")
axA.text(0, -55, "緑の点線：壁から 50 cm", ha="center", fontsize=8.5, color="#2B8A3E")
axA.set_aspect("equal"); axA.set_xlim(-R - 15, R + 15); axA.set_ylim(-R - 15, R + 15); axA.axis("off")
axA.legend(fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False)
axA.set_title("上から見た道すじ（8 秒から後）", fontsize=11)
for lab, ki, col in runs:
    o = res[ki]; axB.plot(o[:, 0], R - np.hypot(o[:, 1], o[:, 2]), color=col, lw=2, label=lab)
axB.axhline(50, color="#2F9E44", ls="--", lw=1.2); axB.text(19.8, 50.5, "目標 50 cm", color="#2B8A3E", fontsize=9, ha="right", va="bottom")
axB.set_xlim(0, 20); axB.set_ylim(30, 60); axB.grid(alpha=0.3)
axB.set_xlabel("時間〔秒〕"); axB.set_ylabel("壁までの本当の距離〔cm〕")
axB.legend(fontsize=9, loc="lower right", frameon=True, framealpha=0.9)
axB.set_title("壁までの距離（KP 0.02、KA 0.04、speed 0.5）", fontsize=11)
for s in ("top", "right"): axB.spines[s].set_visible(False)
fig.suptitle("丸い部屋の壁にそって走る（説明用の簡単なモデル）", fontsize=11, y=0.985)
fig.savefig(f"{OUT}/fig1-round-room.png", facecolor="white"); plt.close(fig)

# ---------- fig2: I part ----------
o = res[0.005]
fig, ax = plt.subplots(figsize=(10.4, 3.9), dpi=200)
ax.plot(o[:, 0], o[:, 4], color="#ADB5BD", lw=0.9, label="angle（ハンドルの命令）")
ax.plot(o[:, 0], o[:, 7], color="#E8590C", lw=2.2, label="I の部分（KI × ずれの積分）")
ax.axhline(0, color="#868E96", lw=1)
ax.set_xlim(0, 20); ax.set_ylim(-0.7, 0.1); ax.grid(alpha=0.3)
ax.set_xlabel("時間〔秒〕"); ax.set_ylabel("angle への足し分")
ax.legend(fontsize=9, loc="upper right", frameon=True, framealpha=0.9)
ax.set_title("I の部分が、曲がり続けるのに必要なハンドルを受け持つようになる（KI 0.005、説明用の簡単なモデル）", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-i-part.png", facecolor="white"); plt.close(fig)
print("I part at the end:", round(o[-60:, 7].mean(), 3), " angle mean at the end:", round(o[-60:, 4].mean(), 3))

# ---------- numbers quoted in the text ----------
STRAIGHT = [(100, -200, 100, 6000), (-100, -200, -100, 6000)]
for ki in (0.0, 0.002, 0.005, 0.01, 0.02):
    o, crashed = wallsim.simulate(WALLS, wallsim.PIA(0.02, ki, 0.04), 0.5, 20, x=R - 50)
    d = R - np.hypot(o[:, 1], o[:, 2])
    print(f"round room KI {ki}: final {d[-120:].mean():.1f} min {d.min():.1f} max {d.max():.1f}")
for ki in (0.0, 0.005):
    o, crashed = wallsim.simulate(STRAIGHT, wallsim.PIA(0.02, ki, 0.04), 0.5, 20, x=50, kw=dict(wallsim.REAL, steer_bias=0.1))
    d = 100 - o[:, 1]
    print(f"straight wall, steering bias 0.1, KI {ki}: final {d[-120:].mean():.1f}")
for ki, start, T in ((0.0, 100, 8), (0.01, 100, 8), (0.01, 300, 10)):
    o, crashed = wallsim.simulate_front_stop(0.02, ki, start, T, deadband=0.15)
    print(f"stop at wall with friction, KI {ki}, start {start} cm: {'crashed' if crashed else 'final %.1f' % o[-1, 1]}, closest {o[:, 1].min():.1f}")
