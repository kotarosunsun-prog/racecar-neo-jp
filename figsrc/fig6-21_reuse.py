"""Figures for 6-21: the PID class of 6-12 reused (sim2d model).
fig1: line following on an S-shaped line at speed 0.5 (line_follow_pid.py), P only (KP 1.0, 6-2) vs PID (2.0, 1.0, 0.1).
fig2: stopping 30 cm before a cone (cone_park_pid.py): the camera view, and the gap for P / PI / PI with i_zone."""
import os, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import sim2d, wallsim
from pid_book import PID
rc_utils = wallsim.rc_utils
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-21"
BLUE = ((90, 50, 50), (120, 255, 255)); LINE_BGR = (205, 120, 40)
DT = wallsim.DT


def dist_to(p, px, py):
    best = 1e9
    for (x1, y1), (x2, y2) in zip(p[:-1], p[1:]):
        ex, ey = x2 - x1, y2 - y1; t = min(1, max(0, ((px - x1) * ex + (py - y1) * ey) / (ex * ex + ey * ey)))
        best = min(best, math.hypot(px - (x1 + t * ex), py - (y1 + t * ey)))
    return best


def run_line(pid, speed=0.5, T=16):
    """line_follow_pid.py: the angle changes only when the line is seen; the speed is constant"""
    line = sim2d.s_line(); p = np.array(line)
    w = sim2d.World([], x=0, y=0, heading_deg=90); cam = sim2d.FloorCamera(first_row=360); rng = np.random.default_rng(0)
    angle, rows = 0.0, []
    for _ in range(int(T * 60)):
        im = cam.render(w, [(line, 5.0, LINE_BGR)], rng=rng, seg_range=60)
        cr = rc_utils.crop(im, (360, 0), (480, 640))
        ct = rc_utils.get_largest_contour(rc_utils.find_contours(cr, BLUE[0], BLUE[1]), 30)
        e = np.nan
        if ct is not None:
            e = (rc_utils.get_contour_center(ct)[1] - 320) / 320
            angle = pid.update(e, DT)
        w.step(1 / 60, speed, angle)
        rows.append((w.t, w.x, w.y, e, angle, dist_to(p, w.x, w.y)))
    return np.array(rows), p


# ---------- fig1: line ----------
line_runs = [("P だけ（KP 1.0、6-2 と同じ）", (1.0, 0.0, 0.0), "#868E96"), ("P（KP 2.0）", (2.0, 0.0, 0.0), None),
             ("PI（KP 1.0、KI 1.0）", (1.0, 1.0, 0.0), None), ("PID（KP 2.0、KI 1.0、KD 0.1）", (2.0, 1.0, 0.1), "#E8590C")]
res = {}
for lab, g, col in line_runs:
    o, p = run_line(PID(*g)); res[lab] = o
    print(f"{lab}: lost {int(np.isnan(o[:,3]).sum())} mean|error| {np.nanmean(np.abs(o[:,3])):.3f} mean off {o[:,5].mean():.1f} cm max off {o[:,5].max():.1f} cm")
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.4, 5.0), dpi=200, gridspec_kw=dict(width_ratios=[1, 1.5]))
ax.plot(p[:, 0], p[:, 1], color="#339AF0", lw=7, alpha=0.35, solid_capstyle="butt", label="床の青い線")
for lab, g, col in line_runs:
    if col is None: continue
    o = res[lab]; ax.plot(o[:, 1], o[:, 2], color=col, lw=1.6, label=lab)
    ax2.plot(o[:, 0], o[:, 3], color=col, lw=1.4, label=lab)
ax.plot([0], [0], "o", color="#212529", ms=5); ax.text(10, -20, "スタート", fontsize=9)
ax.set_aspect("equal"); ax.set_xlim(-230, 330); ax.set_ylim(-50, 950); ax.grid(alpha=0.3)
ax.set_xlabel("横〔cm〕"); ax.set_ylabel("縦〔cm〕"); ax.legend(fontsize=8, loc="upper right", frameon=True, framealpha=0.95)
ax.set_title("線をたどった道すじ（speed 0.5）", fontsize=10.5)
ax2.axhline(0, color="#495057", lw=0.8)
ax2.set_xlim(0, 16); ax2.set_ylim(-1.1, 1.15); ax2.grid(alpha=0.3)
ax2.set_xlabel("時間〔秒〕"); ax2.set_ylabel("ずれ（画面の真ん中からの線の位置）")
ax2.text(3.3, 1.02, "右へ曲がる所", fontsize=9, color="#495057", ha="center")
ax2.text(8.0, 1.02, "左へ曲がる所", fontsize=9, color="#495057", ha="center")
ax2.text(14.0, 1.02, "右へ曲がる所", fontsize=9, color="#495057", ha="center")
ax2.legend(fontsize=8.5, loc="lower right", frameon=True, framealpha=0.95)
ax2.set_title("カメラで見たずれ", fontsize=10.5)
for a in (ax, ax2):
    for s in ("top", "right"): a.spines[s].set_visible(False)
fig.suptitle("PID クラスでライントレース（説明用の簡単なモデル）", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-line.png", facecolor="white"); plt.close(fig)


# ---------- fig2: cone ----------
CX, CY = 60.0, 300.0
CONE = [(CX, CY, 10.0, 30.0, LINE_BGR)]


def run_cone(speed_pid, T=20):
    """cone_park_pid.py"""
    w = sim2d.World(sim2d.cone_segments(CX, CY), x=0, y=0, heading_deg=90, lidar_noise=0.0, lidar_rel_noise=0.02,
                    spin_hz=6, delay_frames=1, speed_deadband=0.15)
    cam = sim2d.ConeCamera(CONE); rng = np.random.default_rng(0)
    steer_pid = PID(kp=1.0, ki=0.0, kd=0.0)
    w.scan(); cam.render(w, rng=rng)                     # start(): nothing moves
    rows = []
    for _ in range(int(T * 60)):
        scan = w.scan(); im = cam.render(w, rng=rng)
        ct = rc_utils.get_largest_contour(rc_utils.find_contours(im, BLUE[0], BLUE[1]), 30)
        _, dist = rc_utils.get_lidar_closest_point(scan, (340, 20))
        if ct is None:
            steer_pid.reset(); speed_pid.reset(); speed, angle = 0.0, 0.0
        else:
            x = (rc_utils.get_contour_center(ct)[1] - 320) / 320
            angle = steer_pid.update(x, DT); speed = speed_pid.update(dist - 30.0, DT)
        w.step(DT, speed, angle)
        rows.append((w.t, math.hypot(w.x - CX, w.y - CY) - 10.0, speed))
    return np.array(rows)


cone_runs = [("P だけ（KP 0.01）", PID(0.01, 0.0, 0.0, out_min=-0.3, out_max=0.5), "#868E96"),
             ("PI（KP 0.01、KI 0.01）", PID(0.01, 0.01, 0.0, out_min=-0.3, out_max=0.5), "#1C7ED6"),
             ("PI ＋ i_zone 10", PID(0.01, 0.01, 0.0, i_zone=10, out_min=-0.3, out_max=0.5), "#E8590C")]
fig = plt.figure(figsize=(11.4, 4.6), dpi=200)
axi = fig.add_axes([0.05, 0.12, 0.34, 0.76]); axg = fig.add_axes([0.46, 0.13, 0.52, 0.75])
w0 = sim2d.World([], x=0, y=100, heading_deg=95)
img = sim2d.ConeCamera(CONE).render(w0, rng=np.random.default_rng(1))
ct = rc_utils.get_largest_contour(rc_utils.find_contours(img, BLUE[0], BLUE[1]), 30)
row, col = rc_utils.get_contour_center(ct)
axi.imshow(img[:, :, ::-1]); axi.set_xticks([0, 320, 639]); axi.set_yticks([0, 240, 479]); axi.tick_params(labelsize=8)
axi.plot([320, 320], [0, 479], color="white", ls=":", lw=1.2); axi.plot([col], [row], "o", color="#E03131", ms=6)
axi.annotate("", xy=(col, 150), xytext=(320, 150), arrowprops=dict(arrowstyle="<->", color="#FFD43B", lw=2))
axi.text((col + 320) / 2, 130, f"ずれ = ({col} − 320) ÷ 320 = {(col - 320) / 320:+.2f}", ha="center", fontsize=8.5,
         bbox=dict(boxstyle="round", fc="white", ec="#ADB5BD"))
axi.set_title("カメラで見たコーン（200 cm 手前、少し左を向いている）", fontsize=9.5)
print("cone view: center", row, col)
for lab, sp, c in cone_runs:
    o = run_cone(sp)
    axg.plot(o[:, 0], o[:, 1], color=c, lw=1.8, label=f"{lab}：最後 {o[-1, 1]:.1f} cm")
    print(f"{lab}: final {o[-1,1]:.1f} closest {o[:,1].min():.1f}")
axg.axhline(30, color="#2F9E44", ls="--", lw=1); axg.text(0.3, 27, "目標 30 cm", ha="left", va="top", fontsize=9, color="#2B8A3E")
axg.set_xlim(0, 20); axg.set_ylim(0, 120); axg.grid(alpha=0.3)
axg.set_xlabel("時間〔秒〕"); axg.set_ylabel("コーンまでのすき間〔cm〕")
axg.legend(fontsize=8.5, loc="upper right", frameon=True, framealpha=0.95)
axg.set_title("コーンの手前で止まる（速さの PID、説明用の簡単なモデル）", fontsize=10.5)
for s in ("top", "right"): axg.spines[s].set_visible(False)
fig.savefig(f"{OUT}/fig2-cone.png", facecolor="white"); plt.close(fig)
