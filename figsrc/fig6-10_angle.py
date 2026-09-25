"""Figures for 6-10.
fig1: how two rays (60 and 90 degrees) give the wall direction alpha and the distance d (diagram).
fig2: a wall that bends 45 degrees to the right: P + D vs P + wall direction (sim2d model, realistic LIDAR, speed 0.5)."""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager as fm
import wallsim
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-10"

# ---------- fig1: geometry ----------
fig, ax = plt.subplots(figsize=(8.2, 6.2), dpi=200)
ALPHA = math.radians(12); D = 50.0; TH = math.radians(30)
nx, ny = math.cos(ALPHA), -math.sin(ALPHA)          # unit normal from the car to the wall
px, py = D * nx, D * ny                             # foot of the perpendicular
ux, uy = math.sin(ALPHA), math.cos(ALPHA)           # wall direction (alpha > 0: the wall goes away to the right)
ts = np.array([-45, 125])
ax.plot(px + ts * ux, py + ts * uy, color="#495057", lw=3.5)
ax.text(px + 118 * ux + 4, py + 118 * uy, "右の壁", fontsize=10, ha="left", va="center")
def hit(phi):                                        # ray at angle phi (clockwise from the front) hits the wall
    dx, dy = math.sin(phi), math.cos(phi)
    t = D / (dx * nx + dy * ny); return t, t * dx, t * dy
b, bx, by = hit(math.radians(90)); a, ax_, ay_ = hit(math.radians(60))
ax.plot([0, px], [0, py], color="#2F9E44", lw=1.8, ls="--")
ax.plot([0, bx], [0, by], color="#E8590C", lw=2.6); ax.plot([0, ax_], [0, ay_], color="#1C7ED6", lw=2.6)
ax.plot([bx, ax_], [by, ay_], "o", color="#212529", ms=5)
ax.text(bx * 0.72, by + 1.5, "b", color="#D9480F", fontsize=13, fontweight="bold", ha="center", va="bottom")
ax.text(ax_ * 0.55 - 1, ay_ * 0.55 + 2, "a", color="#1864AB", fontsize=13, fontweight="bold", ha="right", va="bottom")
ax.text(px * 0.72, py * 0.72 - 1.5, "d", color="#2B8A3E", fontsize=13, fontweight="bold", ha="center", va="top")
ax.text(bx + 3.5, by - 1, "B", fontsize=11, fontweight="bold", va="top"); ax.text(ax_ + 3.5, ay_, "A", fontsize=11, fontweight="bold")
ax.add_patch(patches.Arc((0, 0), 30, 30, theta1=0, theta2=30, color="#495057", lw=1.2))
ax.text(16.5, 3.2, "30°", fontsize=9, color="#495057")
ax.plot([bx, bx], [by, by + 88], color="#868E96", lw=1, ls=":")
ax.text(bx - 2, by + 88, "進む向きと\n同じ向きの線", fontsize=8.5, color="#495057", ha="right", va="top")
ax.add_patch(patches.Arc((bx, by), 110, 110, theta1=90 - math.degrees(ALPHA), theta2=90, color="#AE3EC9", lw=2.2))
ax.text(bx + 2, by + 58, "α", color="#9C36B5", fontsize=14, fontweight="bold", ha="left", va="bottom")
ax.add_patch(patches.FancyBboxPatch((-6, -12), 12, 24, boxstyle="round,pad=1.2", fc="#1C7ED6", ec="#1864AB", lw=1.3, zorder=0))
ax.annotate("", xy=(0, 40), xytext=(0, 15), arrowprops=dict(arrowstyle="-|>", color="#1864AB", lw=2))
ax.text(-2, 42, "進む向き", fontsize=9, color="#1864AB", ha="center", va="bottom")
legend = (f"b：真横（90°）の距離 = {b:.1f} cm\n"
          f"a：ななめ前（60°）の距離 = {a:.1f} cm\n"
          f"α：壁の向き = {math.degrees(ALPHA):.0f}°\n"
          f"d：本当の距離 = b × cos α = {D:.0f} cm")
ax.text(-78, 118, legend, fontsize=9.5, va="top", linespacing=1.6, bbox=dict(boxstyle="round", fc="white", ec="#ADB5BD"))
ax.text(-78, -48, "α ＞ 0：壁が前に行くほど遠ざかる\n　　　（車は壁から離れる向きに走っている）\nα ＜ 0：車は壁に近づく向きに走っている", fontsize=9,
        va="bottom", linespacing=1.5, bbox=dict(boxstyle="round", fc="#F8F9FA", ec="#ADB5BD"))
ax.set_xlim(-80, 100); ax.set_ylim(-50, 122); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("2本の光線から、壁の向き α と本当の距離 d を求める", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-two-rays.png", facecolor="white"); plt.close(fig)
alpha_calc = math.degrees(math.atan2(a * math.cos(TH) - b, a * math.sin(TH)))
print(f"a={a:.2f} b={b:.2f} alpha={alpha_calc:.2f} d={b * math.cos(math.radians(alpha_calc)):.2f}")

# ---------- fig2: a wall bending to the right ----------
s = math.sqrt(0.5); L = 900
WALLS = [(100, -200, 100, 600), (100, 600, 100 + L * s, 600 + L * s)]
fig = plt.figure(figsize=(10.8, 5.0), dpi=200)
axA = fig.add_axes([0.03, 0.1, 0.40, 0.78]); axB = fig.add_axes([0.53, 0.14, 0.45, 0.7])
for x1, y1, x2, y2 in WALLS: axA.plot([x1, x2], [y1, y2], color="#495057", lw=3)
runs = [("P ＋ D（6-9：KP 0.02、KD 0.03）", wallsim.PD(0.02, 0.03, 10), "#868E96"),
        ("P ＋ 壁の向き（この回：KP 0.02、KA 0.04）", wallsim.Angle(0.02, 0.04), "#E8590C")]
for lab, ctrl, col in runs:
    o, crashed = wallsim.simulate(WALLS, ctrl, 0.5, 12, x=50)
    axA.plot(o[:, 1], o[:, 2], color=col, lw=2.2, label=lab)
    trav = np.r_[0, np.cumsum(np.hypot(np.diff(o[:, 1]), np.diff(o[:, 2])))]
    axB.plot(trav, o[:, 6], color=col, lw=2.2, label=lab)
    after = o[o[:, 2] > 500, 6]
    print(lab, "crashed" if crashed else "", f"after the bend: {after.min():.1f}..{after.max():.1f} cm")
axA.plot([50], [0], "o", color="#212529", ms=5); axA.text(40, 30, "スタート", fontsize=9, ha="right", va="center")
axA.text(115, 380, "右の壁", fontsize=10)
axA.text(250, 430, "ここから壁が\n右へ 45° 曲がる", fontsize=9, color="#495057")
axA.annotate("", xy=(106, 596), xytext=(245, 470), arrowprops=dict(arrowstyle="-|>", color="#868E96", lw=1.2))
axA.set_aspect("equal"); axA.set_xlim(-60, 600); axA.set_ylim(-40, 1050); axA.grid(alpha=0.25)
axA.set_xlabel("横〔cm〕"); axA.set_ylabel("縦〔cm〕"); axA.set_title("上から見た道すじ", fontsize=11)
axB.axhline(50, color="#2F9E44", ls="--", lw=1.2); axB.text(5, 51, "目標 50 cm", fontsize=9, color="#2B8A3E", va="bottom")
axB.axvline(600, color="#ADB5BD", ls=":", lw=1.2); axB.text(595, 33, "壁が曲がる所（縦 600 cm）", fontsize=9, color="#495057", ha="right")
axB.set_ylim(30, 90); axB.set_xlim(0, 1000); axB.grid(alpha=0.3)
axB.set_xlabel("進んだ距離〔cm〕"); axB.set_ylabel("壁までの本当の距離〔cm〕")
axB.legend(fontsize=9, loc="upper left", frameon=False); axB.set_title("壁までの距離", fontsize=11)
for s_ in ("top", "right"): axB.spines[s_].set_visible(False)
fig.suptitle("右へ曲がる壁にそって走る（speed 0.5、説明用の簡単なモデル）", fontsize=11, y=0.985)
fig.savefig(f"{OUT}/fig2-bend.png", facecolor="white"); plt.close(fig)

# ---------- numbers quoted in the text ----------
import sim2d
w = sim2d.World([(50, -500, 50, 3000)], x=0, y=0, heading_deg=90, seed=3, **dict(wallsim.REAL, delay_frames=0))
tilt = np.array([90 - wallsim.rc_utils.get_lidar_closest_point(w.scan(), (45, 135))[0] for _ in range(600)])
print(f"tilt from the closest point (parallel car, 600 frames): mean {tilt.mean():.2f} sd {tilt.std():.2f} min {tilt.min():.1f} max {tilt.max():.1f}")
for head in (90, 80, 70, 100):
    w = sim2d.World([(100, -200, 100, 3500)], x=30, y=0, heading_deg=head, **dict(wallsim.REAL, delay_frames=0))
    r = np.array([wallsim.right_wall(w.scan()) for _ in range(60)])
    print(f"two rays, heading {head}: alpha mean {r[:, 0].mean():+.2f} sd {r[:, 0].std():.2f}; d mean {r[:, 1].mean():.2f} sd {r[:, 1].std():.2f}")
for name, walls in [("left bend", [(100, -200, 100, 600), (100, 600, 100 - L * s, 600 + L * s)])]:
    for lab, ctrl in [("P+D", wallsim.PD(0.02, 0.03, 10)), ("P+angle", wallsim.Angle(0.02, 0.04))]:
        o, crashed = wallsim.simulate(walls, ctrl, 0.5, 12, x=50)
        print(name, lab, "crashed" if crashed else "", f"closest to the wall after the bend: {o[o[:, 2] > 500, 6].min():.1f} cm")
