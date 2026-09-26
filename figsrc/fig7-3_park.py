"""Figures and numbers for 7-3 (sim2d model): cone_park.py from six starting positions.
Run with an argument 'all' to also repeat every case with LIDAR noise seeds 1..3 (slow)."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch7"))
import ch7run as C
import sim2d, wallsim
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/7-3"
P = C.r._orig
BLUE = (205, 120, 40)
CASES = [("遠い", 0, 250), ("近い", 0, 45), ("とても遠い", 0, 500), ("少し左", -60, 200), ("右の遠く", 200, 350), ("近くて左", -40, 80)]
CAR_R, CONE_R = 12.0, 10.0


def run_case(cx, cy, T=20, seed=0):
    w = sim2d.World(sim2d.cone_segments(cx, cy), x=0, y=0, heading_deg=90, seed=seed, lidar_noise=0.0, lidar_rel_noise=0.02,
                    spin_hz=6, delay_frames=1)
    cam = sim2d.ConeCamera([(cx, cy, CONE_R, 30.0, BLUE)]); rng = np.random.default_rng(seed)
    w, out = C.run("cone_park.py", w, T, image=lambda f: cam.render(w, rng=rng))
    L = np.array(w.log)
    shown = np.hypot(L[:, 1] - cx, L[:, 2] - cy) - CONE_R - CAR_R     # what the simulator shows: cone surface to car surface
    ok = np.where((np.abs(shown - 30) < 1) & (np.abs(L[:, 4]) < 0.2))[0]
    return w, out, L, shown, (L[ok[0], 0] if len(ok) else None)


res = {}
for name, cx, cy in CASES:
    w, out, L, shown, t = run_case(cx, cy)
    res[name] = (L, shown, out, t)
    P(f"{name}: crashed={w.crashed} done {t if t is None else round(t, 2)} s, final shown {shown[-1]:.1f} cm,",
      [s for f, s in out if s.endswith("cm）")])
if len(sys.argv) > 1 and sys.argv[1] == "all":
    for seed in (1, 2, 3):
        P("seed", seed, [(n, None if (t := run_case(cx, cy, seed=seed)[4]) is None else round(t, 1)) for n, cx, cy in CASES])

# no cone at all: the program should keep searching
w = sim2d.World([], x=0, y=0, heading_deg=90, **wallsim.REAL)
w, out = C.run("cone_park.py", w, 10, image=lambda f: sim2d.ConeCamera([]).render(w))
L = np.array(w.log); P("no cone:", [s for f, s in out][:3], "moved", round(np.hypot(L[-1, 1], L[-1, 2]), 1))

# the calibration: LIDAR reading when the simulator would show 29 / 30 / 31 cm
src = open(os.path.join(C.HERE, "cone_park.py")).read()
ns = {"HALF_FOV": 34.7}
exec("import numpy as np\n" + src[src.index("def cone_distance"):src.index("def change")], ns)
for shown in (29, 30, 31):
    w = sim2d.World(sim2d.cone_segments(0, shown + CAR_R + CONE_R), x=0, y=0, heading_deg=90, lidar_noise=0.0, lidar_rel_noise=0.02, spin_hz=6, delay_frames=1)
    vals = []
    for _ in range(600):
        s = w.scan(); w.step(1 / 60, 0, 0); vals.append(ns["cone_distance"](s, 0.0))
    vals = np.array(vals[60:]); P(f"shown {shown} cm -> cone_distance mean {vals.mean():.2f} (min {vals.min():.2f}, max {vals.max():.2f})")

# ---------- fig1: camera view and paths ----------
fig = plt.figure(figsize=(11.0, 5.4), dpi=200)
axi = fig.add_axes([0.04, 0.2, 0.36, 0.62]); ax = fig.add_axes([0.46, 0.08, 0.5, 0.82])
w0 = sim2d.World([], x=0, y=0, heading_deg=90)
img = sim2d.ConeCamera([(-60, 200, CONE_R, 30.0, BLUE)]).render(w0, rng=np.random.default_rng(1))
axi.imshow(img[:, :, ::-1]); axi.set_xticks([0, 320, 639]); axi.set_yticks([0, 240, 479]); axi.tick_params(labelsize=8)
axi.set_title("「少し左」のスタートで見たコーン", fontsize=10)
cols = ["#1C7ED6", "#E8590C", "#2F9E44", "#AE3EC9", "#F08C00", "#C92A2A"]
for (name, cx, cy), c in zip(CASES, cols):
    L, shown, out, t = res[name]
    ax.plot(L[:, 1], L[:, 2], color=c, lw=1.8, label=f"{name}（{'%.1f 秒で成功' % t if t else '失敗'}）")
    ax.add_patch(plt.Circle((cx, cy), CONE_R, color=c, alpha=0.8))
ax.plot([0], [0], "o", color="#212529", ms=6); ax.annotate("", xy=(0, 40), xytext=(0, 0), arrowprops=dict(arrowstyle="->", lw=1.5))
ax.text(8, -25, "スタート（上向き）", fontsize=9)
ax.set_aspect("equal"); ax.set_xlim(-160, 330); ax.set_ylim(-60, 540); ax.grid(alpha=0.3)
ax.set_xlabel("横〔cm〕"); ax.set_ylabel("縦〔cm〕")
ax.legend(fontsize=8.5, loc="upper right", frameon=True, framealpha=0.95)
ax.set_title("6 つの置き方で、コーンの手前に止まる（丸がコーン）", fontsize=10.5)
fig.savefig(f"{OUT}/fig1-cases.png", facecolor="white"); plt.close(fig)

# ---------- fig2: one run over time with its states ----------
L, shown, out, t = res["右の遠く"]
fig, ax = plt.subplots(figsize=(10.0, 4.2), dpi=200)
ax.plot(L[:, 0], shown, color="#1C7ED6", lw=2)
ax.axhspan(29, 31, color="#D3F9D8"); ax.axhline(30, color="#2F9E44", ls="--", lw=1)
chg = [(f / 60, s.split(" ")[0]) for f, s in out if s.endswith("cm）")]
for tt, s in chg:
    ax.axvline(tt, color="#868E96", ls=":", lw=1); ax.text(tt + 0.1, 330, s, fontsize=8.5, rotation=90, va="top", color="#495057")
ax.set_xlim(0, 12); ax.set_ylim(0, 340); ax.grid(alpha=0.3)
ax.set_xlabel("時間〔秒〕"); ax.set_ylabel("コーンまで（画面の表示）〔cm〕")
ax.set_title("「右の遠く」のスタート：コーンまでの距離と、状態の切りかわり（緑が 30 ± 1 cm）", fontsize=10.5)
ins = ax.inset_axes([0.5, 0.2, 0.45, 0.5])
m = L[:, 0] > 4
ins.plot(L[m, 0], shown[m], color="#1C7ED6", lw=1.8); ins.axhspan(29, 31, color="#D3F9D8"); ins.axhline(30, color="#2F9E44", ls="--", lw=1)
ins.set_xlim(4, 12); ins.set_ylim(25, 45); ins.tick_params(labelsize=7.5); ins.grid(alpha=0.3); ins.set_title("4 秒から後を拡大", fontsize=8.5)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-states.png", facecolor="white"); plt.close(fig)
