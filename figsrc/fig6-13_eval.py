"""Figures for 6-13: reading a step response (sim2d model, realistic LIDAR).
Start 100 cm from the right wall, target 50 cm, speed 0.5, PID class with the wall direction as D."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import wallsim
from pid_book import PID
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-13"
W = [(100, -200, 100, 6000), (-100, -200, -100, 6000)]


def run(kp, kd, ki, walls=W, x=0.0, T=12):
    o, crashed = wallsim.simulate(walls, wallsim.WallPID(PID(kp, ki, kd, i_zone=20)), 0.5, T, x=x)
    return o, crashed


# ---------- fig1: the base response with the numbers drawn on it ----------
o, _ = run(0.02, 0.04, 0.005)
rows = wallsim.log_rows(o); m = wallsim.metrics(rows)
t = np.array([r[0] for r in rows]); d = np.array([r[1] for r in rows])
step = m["step"]; ratio = (d - 50) / step
t90 = t[np.argmax(ratio <= 0.9)]; t10 = t[np.argmax(ratio <= 0.1)]
imin = np.argmin(d)
fig, ax = plt.subplots(figsize=(10.4, 5.0), dpi=200)
ax.axhspan(50 - 2.5, 50 + 2.5, color="#EBFBEE")
ax.axhline(50, color="#2F9E44", ls="--", lw=1.2)
ax.plot(t, d, color="#E8590C", lw=2)
ax.text(11.9, 53.2, "目標 50 cm と、± 2.5 cm の幅（緑）", color="#2B8A3E", fontsize=9, ha="right", va="bottom")
for tt, lab in [(t90, "90%"), (t10, "10%")]:
    ax.axvline(tt, color="#1C7ED6", ls=":", lw=1.2)
ax.annotate("", xy=(t10, 88), xytext=(t90, 88), arrowprops=dict(arrowstyle="<->", color="#1C7ED6", lw=1.8))
ax.text((t90 + t10) / 2, 90, f"立ち上がり時間 {m['rise']:.2f} 秒\n（ずれが 90% → 10%）", ha="center", va="bottom", fontsize=9, color="#1864AB")
ax.annotate(f"行き過ぎ量 {m['overshoot']:.1f} cm", xy=(t[imin], d[imin]), xytext=(t[imin] + 0.6, 34),
            fontsize=9, color="#9C36B5", arrowprops=dict(arrowstyle="->", color="#9C36B5"))
ax.axvline(m["settle"], color="#495057", ls="--", lw=1.2)
ax.text(m["settle"] + 0.1, 70, f"整定時間 {m['settle']:.2f} 秒\n（このあとは、ずっと緑の幅の中）", fontsize=9, color="#343A40", va="center")
ax.text(11.9, 40, f"残ったずれ {m['steady']:+.2f} cm\n（最後の 2 秒の平均）", fontsize=9, ha="right", color="#343A40")
ax.set_xlim(0, 12); ax.set_ylim(30, 105); ax.grid(alpha=0.3)
ax.set_xlabel("時間〔秒〕"); ax.set_ylabel("測った距離〔cm〕")
ax.set_title("反応を数で表す（KP 0.02、KI 0.005、壁の向き 0.04、説明用の簡単なモデル）", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-step.png", facecolor="white"); plt.close(fig)
print("base:", {k: round(v, 2) for k, v in m.items()})

# ---------- fig2: several gains ----------
sets = [("ア：KP 0.02、壁の向き 0.04、KI 0.005（もと）", (0.02, 0.04, 0.005), "#E8590C"),
        ("イ：壁の向きのゲインを小さく（0.02）", (0.02, 0.02, 0.005), "#1C7ED6"),
        ("エ：KP を大きく（0.04）", (0.04, 0.04, 0.005), "#AE3EC9"),
        ("オ：I なし（KI 0）", (0.02, 0.04, 0.0), "#868E96")]
fig, ax = plt.subplots(figsize=(10.4, 4.6), dpi=200)
ax.axhspan(47.5, 52.5, color="#EBFBEE"); ax.axhline(50, color="#2F9E44", ls="--", lw=1.2)
for lab, (kp, kd, ki), col in sets:
    o, _ = run(kp, kd, ki); rows = wallsim.log_rows(o)
    ax.plot([r[0] for r in rows], [r[1] for r in rows], color=col, lw=1.8, label=lab)
ax.set_xlim(0, 12); ax.set_ylim(30, 105); ax.grid(alpha=0.3)
ax.set_xlabel("時間〔秒〕"); ax.set_ylabel("測った距離〔cm〕")
ax.legend(fontsize=9, loc="upper right", frameon=True, framealpha=0.9)
ax.set_title("ゲインをかえた反応（まっすぐな壁、説明用の簡単なモデル）", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-compare.png", facecolor="white"); plt.close(fig)

# ---------- the table in the text ----------
table = [("ア", 0.02, 0.04, 0.005), ("イ", 0.02, 0.02, 0.005), ("ウ", 0.02, 0.08, 0.005),
         ("エ", 0.04, 0.04, 0.005), ("オ", 0.02, 0.04, 0.0), ("カ", 0.02, 0.04, 0.02)]
R = 250
for name, kp, kd, ki in table:
    o, crashed = run(kp, kd, ki); m = wallsim.metrics(wallsim.log_rows(o))
    o2, crashed2 = run(kp, kd, ki, walls=wallsim.circle(R), x=R - 50, T=20)
    room = (R - np.hypot(o2[:, 1], o2[:, 2]))[-120:].mean() - 50
    print(f"{name} KP {kp} D {kd} KI {ki}: rise {m['rise']:.2f} over {m['overshoot']:.1f} settle {m['settle']:.2f} "
          f"steady {m['steady']:+.2f} activity {m['activity']:.2f} | round room error {room:+.1f}")
