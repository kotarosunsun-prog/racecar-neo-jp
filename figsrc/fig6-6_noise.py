"""Figure for 6-6: four ways to measure the right wall while driving straight past a doorway and a row of posts
(sim2d model with 2 % noise and a LIDAR that spins 6 times a second)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager as fm
import sim2d, wallsim
from wallsim import rc_utils
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-6"


def course():
    segs = [(50, -200, 50, 300), (50, 300, 250, 300), (250, 300, 250, 400), (250, 400, 50, 400), (50, 400, 50, 600)]   # wall, doorway
    posts = list(range(650, 951, 60))
    for y in posts:                                                                                                       # posts (10 cm)
        segs += [(50, y, 60, y), (60, y, 60, y + 10), (60, y + 10, 50, y + 10), (50, y + 10, 50, y)]
    segs += [(200, 600, 200, 1000), (50, 600, 200, 600), (50, 1000, 200, 1000), (50, 1000, 50, 1400)]
    return segs, posts


segs, posts = course()
w = sim2d.World(segs, x=0, y=0, heading_deg=90, seed=1, **dict(wallsim.REAL, delay_frames=0))
w.v = 60.0
rows = []
for k in range(1150):
    s = w.scan()
    a, closest = rc_utils.get_lidar_closest_point(s, (45, 135))
    rows.append((w.y, float(s[180]), rc_utils.get_lidar_average_distance(s, 90), closest, wallsim.right_wall_distance(s)))
    w.step(wallsim.DT, 0.4, 0.0)
R = np.array(rows)
y = R[:, 0]

fig = plt.figure(figsize=(10.4, 7.6), dpi=200)
gs = fig.add_gridspec(3, 1, height_ratios=[0.8, 1.5, 1.5], hspace=0.28, left=0.09, right=0.98, top=0.905, bottom=0.08)
# course strip
ax0 = fig.add_subplot(gs[0])
for x1, y1, x2, y2 in segs:
    ax0.plot([y1, y2], [x1, x2], color="#495057", lw=2)
ax0.plot([0, 1150], [0, 0], color="#1C7ED6", lw=2, ls="--")
ax0.annotate("", xy=(140, 0), xytext=(40, 0), arrowprops=dict(arrowstyle="-|>", color="#1C7ED6", lw=2))
ax0.text(160, -12, "車はまっすぐ進む", color="#1864AB", fontsize=9, va="top")
ax0.text(350, 265, "入り口（奥に部屋）", ha="center", fontsize=9)
ax0.text(810, 215, "柱が並ぶ（すき間の奥に壁）", ha="center", fontsize=9)
ax0.text(10, 64, "右の壁（車の道すじから 50 cm）", fontsize=9, color="#495057", va="bottom")
ax0.set_xlim(0, 1150); ax0.set_ylim(-45, 300); ax0.axis("off")
ax0.set_title("上から見たコース（車の右側だけ。上にあるのが壁）", fontsize=10.5, loc="left")

def shade(ax):
    ax.axvspan(300, 400, color="#FFF3BF", alpha=0.7, lw=0)
    ax.axvspan(600, 1000, color="#E7F5FF", alpha=0.8, lw=0)

ax1 = fig.add_subplot(gs[1], sharex=ax0); shade(ax1)
ax1.plot(y, R[:, 1], color="#E8590C", lw=1.1, label="真横の1点（scan[180]）")
ax1.plot(y, R[:, 2], color="#AE3EC9", lw=1.4, label="真横の平均（get_lidar_average_distance）")
ax1.axhline(50, color="#868E96", ls="--", lw=1)
ax1.set_ylim(0, 270); ax1.set_ylabel("測った距離〔cm〕"); ax1.grid(alpha=0.3)
ax1.legend(fontsize=9, loc="upper right", frameon=True, framealpha=0.9)
ax1.set_title("真横だけを見る方法：入り口や柱のすき間で、奥の壁まで測ってしまう", fontsize=10.5, loc="left")

ax2 = fig.add_subplot(gs[2], sharex=ax0); shade(ax2)
ax2.plot(y, R[:, 3], color="#1C7ED6", lw=1.2, label="いちばん近い点（45°〜135°）")
ax2.plot(y, R[:, 4], color="#2F9E44", lw=1.6, label="近い点だけの平均（この回の方法）")
ax2.axhline(50, color="#868E96", ls="--", lw=1)
ax2.text(20, 50.6, "本当の距離 50 cm", fontsize=8.5, color="#495057", va="bottom")
ax2.set_ylim(44, 76); ax2.set_ylabel("測った距離〔cm〕"); ax2.grid(alpha=0.3)
ax2.set_xlabel("進んだ距離〔cm〕")
ax2.legend(fontsize=9, loc="upper right", frameon=True, framealpha=0.9)
ax2.set_title("右側でいちばん近い点を使う方法（たての目もりを広げている）", fontsize=10.5, loc="left")
ax2.set_xlim(0, 1150)
for a in (ax1, ax2):
    for s_ in ("top", "right"): a.spines[s_].set_visible(False)
fig.suptitle("4つの測り方をくらべる（説明用の簡単なモデル：ノイズ 2%、LIDAR は1秒に6回転）", fontsize=11, y=0.985)
fig.savefig(f"{OUT}/fig1-compare.png", facecolor="white"); plt.close(fig)

wall = (y > 0) & (y < 280)
for name, i in [("single", 1), ("avg", 2), ("closest", 3), ("near-avg", 4)]:
    door = R[(y > 310) & (y < 390), i]; post = R[(y > 660) & (y < 940), i]
    print(f"{name:9} wall mean {R[wall, i].mean():6.2f} sd {R[wall, i].std():5.2f} | doorway {door.min():6.1f}..{door.max():6.1f} | posts {post.min():6.1f}..{post.max():6.1f}")
