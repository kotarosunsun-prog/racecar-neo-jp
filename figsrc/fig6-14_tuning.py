"""Figures for 6-14 (sim2d model, realistic LIDAR, speed 0.5).
fig1: the run of wall_follow_tune.py: KP is raised with the Y button every 10 s and the car is kicked with A.
fig2: step responses with the Ziegler-Nichols PI gains and with the hand-tuned gains."""
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
OUT = "../images/racecar-neo-jp/6-14"
W = [(100, -200, 100, 9000), (-100, -200, -100, 9000)]


class Tune:
    """what wall_follow_tune.py does, with the button presses given as a schedule (frame numbers)"""
    def __init__(self, y_frames, a_frames):
        self.kp, self.kick, self.f = 0.1, 0.0, 0
        self.y, self.a = set(y_frames), set(a_frames)
    def __call__(self, scan):
        self.f += 1
        if self.f in self.y:
            self.kp *= 1.2
        if self.f in self.a:
            self.kick = 0.3
        al, d = wallsim.right_wall(scan); self.d = d
        angle = 0.0
        if d is not None:
            angle = wallsim.rc_utils.clamp(self.kp * (d - 50) + 0.04 * al, -1.0, 1.0)
        if self.kick > 0:
            angle = 1.0
            self.kick -= wallsim.DT
        return angle


y_frames = [60 * s for s in (10, 20, 30)]
a_frames = [60 * s + 60 for s in (0, 10, 20, 30)]
ctrl = Tune(y_frames, a_frames)
o, crashed = wallsim.simulate(W, ctrl, 0.5, 44, x=50, extra=lambda c: (c.kp,))
t = o[:, 0]; e = (100 - o[:, 1]) - 50
fig, ax = plt.subplots(figsize=(10.8, 4.4), dpi=200)
ax.plot(t, e, color="#E8590C", lw=1.4)
ax.axhline(0, color="#868E96", lw=1)
for s in (0, 10, 20, 30):
    kp = o[np.argmax(t >= s + 0.5), 7]
    ax.axvspan(s, s + 10, color=("#F8F9FA" if (s // 10) % 2 == 0 else "#F1F3F5"), zorder=0)
    ax.text(s + 5, 11, f"KP {kp:.3f}", ha="center", fontsize=10, fontweight="bold", color="#343A40")
    ax.annotate("", xy=(s + 1.0, -9.5), xytext=(s + 1.0, -12.5), arrowprops=dict(arrowstyle="-|>", color="#1C7ED6", lw=1.6))
ax.text(1.2, -12.2, "A：わざと揺らす", fontsize=8.5, color="#1864AB", va="center")
ax.text(25.5, -9, "だんだん小さくなる", fontsize=9, color="#495057", ha="center")
ax.text(35.5, -9, "同じ大きさで続く", fontsize=9, color="#C92A2A", ha="center")
ax.set_xlim(0, 40); ax.set_ylim(-13.5, 13); ax.grid(alpha=0.3)
ax.set_xlabel("時間〔秒〕"); ax.set_ylabel("ずれ（距離 − 50）〔cm〕")
ax.set_title("KP を少しずつ大きくしながら、わざと揺らしてみる（壁の向きのゲイン 0.04、説明用の簡単なモデル）", fontsize=10.5)
for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-find-ku.png", facecolor="white"); plt.close(fig)
zc = [i for i in range(1, len(e)) if t[i] > 32 and np.sign(e[i]) != np.sign(e[i - 1]) and abs(e[i] - e[i - 1]) < 5]
print("crashed:", crashed, " amplitude 34-40 s:", round(np.abs(e[t > 34]).max(), 1))

# ---------- fig2: Ziegler-Nichols ----------
Ku, Tu = 0.17, 1.8
zn_pi = (0.45 * Ku, 0.54 * Ku / Tu)
print(f"ZN PI: KP {zn_pi[0]:.4f} KI {zn_pi[1]:.4f}")
S = [(100, -200, 100, 6000), (-100, -200, -100, 6000)]
runs = [(f"限界感度法の PI（KP {zn_pi[0]:.3f}、KI {zn_pi[1]:.3f}）", zn_pi[0], zn_pi[1], "#1C7ED6"),
        (f"その半分（KP {zn_pi[0] / 2:.3f}、KI {zn_pi[1] / 2:.3f}）", zn_pi[0] / 2, zn_pi[1] / 2, "#AE3EC9"),
        ("手で合わせた値（KP 0.04、KI 0.005）", 0.04, 0.005, "#E8590C")]
fig, ax = plt.subplots(figsize=(10.4, 4.4), dpi=200)
ax.axhspan(47.5, 52.5, color="#EBFBEE"); ax.axhline(50, color="#2F9E44", ls="--", lw=1.2)
for lab, kp, ki, col in runs:
    o, crashed = wallsim.simulate(S, wallsim.WallPID(PID(kp, ki, 0.04, i_zone=20)), 0.5, 12, x=0)
    rows = wallsim.log_rows(o); m = wallsim.metrics(rows)
    o2, _ = wallsim.simulate(wallsim.circle(250), wallsim.WallPID(PID(kp, ki, 0.04, i_zone=20)), 0.5, 20, x=200)
    room = (250 - np.hypot(o2[:, 1], o2[:, 2]))[-120:].mean() - 50
    ax.plot([r[0] for r in rows], [r[1] for r in rows], color=col, lw=1.8, label=lab)
    print(lab, {k: round(v, 2) for k, v in m.items()}, "round room", round(room, 1))
ax.set_xlim(0, 12); ax.set_ylim(20, 105); ax.grid(alpha=0.3)
ax.set_xlabel("時間〔秒〕"); ax.set_ylabel("測った距離〔cm〕")
ax.legend(fontsize=9, loc="upper right", frameon=True, framealpha=0.9)
ax.set_title("限界感度法で決めたゲインと、手で合わせたゲイン（壁の向き 0.04、説明用の簡単なモデル）", fontsize=10.5)
for s_ in ("top", "right"): ax.spines[s_].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-zn.png", facecolor="white"); plt.close(fig)

# ---------- the hand-tuning table ----------
for kp, kd, ki in [(0.02, 0.0, 0.0), (0.02, 0.02, 0.0), (0.02, 0.04, 0.0), (0.04, 0.04, 0.0), (0.08, 0.04, 0.0), (0.04, 0.04, 0.005)]:
    o, crashed = wallsim.simulate(S, wallsim.WallPID(PID(kp, ki, kd, i_zone=20)), 0.5, 12, x=0)
    o2, _ = wallsim.simulate(wallsim.circle(250), wallsim.WallPID(PID(kp, ki, kd, i_zone=20)), 0.5, 20, x=200)
    room = (250 - np.hypot(o2[:, 1], o2[:, 2]))[-120:].mean() - 50
    if crashed:
        print(f"KP {kp} wall {kd} KI {ki}: crashed at {o[-1, 0]:.1f} s")
    else:
        m = wallsim.metrics(wallsim.log_rows(o))
        print(f"KP {kp} wall {kd} KI {ki}: rise {m['rise']:.2f} over {m['overshoot']:.1f} settle {m['settle']:.2f} room {room:+.1f}")
