"""Figure for 6-4: what the wall follower does (top view) and the loop we build in 6-5 .. 6-10 (hand-drawn diagram)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager as fm
import numpy as np
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/6-4"

fig = plt.figure(figsize=(10.8, 5.4), dpi=200)
# ---- left: top view ----
ax = fig.add_axes([0.01, 0.04, 0.36, 0.86])
WALL = 100
ax.add_patch(patches.Rectangle((WALL, -40), 12, 370, fc="#CED4DA", ec="#495057", lw=1.5, hatch="///"))
ax.plot([WALL - 50] * 2, [-40, 330], color="#2F9E44", ls="--", lw=1.8)
ax.text(WALL - 53, 322, "目標の線\n（壁から 50 cm）", color="#2B8A3E", fontsize=9, ha="right", va="top",
        bbox=dict(fc="white", ec="none", alpha=0.9, pad=1))
cx, cy = 5, 120
for k in range(-8, 9):
    ax.plot([cx, WALL], [cy, cy + (WALL - cx) * np.tan(np.radians(k * 6))], color="#FFC9C9", lw=0.8, zorder=1)
ax.add_patch(patches.FancyBboxPatch((cx - 13, cy - 24), 26, 48, boxstyle="round,pad=2", fc="#1C7ED6", ec="#1864AB", lw=1.5, zorder=3))
ax.annotate("", xy=(cx, cy + 58), xytext=(cx, cy + 27), arrowprops=dict(arrowstyle="-|>", color="#1864AB", lw=2), zorder=4)
ax.text(cx, cy + 62, "進む向き", ha="center", fontsize=9, color="#1864AB")
ax.text(cx, cy, "車", ha="center", va="center", color="white", fontsize=10, zorder=5)
ax.annotate("", xy=(WALL, cy - 50), xytext=(cx, cy - 50), arrowprops=dict(arrowstyle="<->", color="#E8590C", lw=2))
ax.text((cx + WALL) / 2, cy - 57, "LIDAR で\n測った距離 d", ha="center", va="top", fontsize=10, color="#D9480F",
        bbox=dict(fc="white", ec="none", alpha=0.9, pad=1))
ax.annotate("", xy=(WALL - 50, cy + 110), xytext=(cx, cy + 110), arrowprops=dict(arrowstyle="<->", color="#AE3EC9", lw=2))
ax.text(cx - 14, cy + 117, "ずれ = d − 50", ha="left", va="bottom", fontsize=10, color="#9C36B5",
        bbox=dict(fc="white", ec="none", alpha=0.9, pad=1))
ax.text(WALL + 6, 340, "右の壁", ha="center", fontsize=10)
ax.set_xlim(-30, 125); ax.set_ylim(-50, 355); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("上から見た壁沿い走行", fontsize=11)

# ---- right: the loop ----
ax2 = fig.add_axes([0.40, 0.02, 0.59, 0.90]); ax2.set_xlim(0, 100); ax2.set_ylim(0, 100); ax2.axis("off")
boxes = [
    (84, "① 測る", "LIDAR で、右の壁までの距離 d を求める", "6-5・6-6"),
    (64, "② 比べる", "ずれ = d − 目標の距離", "6-7"),
    (44, "③ 決める", "ずれ（と、その変わり方）から angle を決める", "6-7・6-9・6-10"),
    (24, "④ 送る", "rc.drive.set_speed_angle(speed, angle)\nupdate() の最後に1回だけ", ""),
]
X0, X1 = 22, 97
for y, head, body, page in boxes:
    ax2.add_patch(patches.FancyBboxPatch((X0, y - 7), X1 - X0, 14, boxstyle="round,pad=0.8", fc="#F8F9FA", ec="#868E96", lw=1.3))
    ax2.text(X0 + 2.5, y, head, fontsize=11, va="center", fontweight="bold", color="#212529")
    ax2.text(X0 + 17, y, body, fontsize=9.2, va="center", color="#343A40")
    if page:
        ax2.text(X1 - 1, y + 5, page, fontsize=8.5, ha="right", va="center", color="#1864AB",
                 bbox=dict(boxstyle="round,pad=0.25", fc="#E7F5FF", ec="none"))
for y in (76, 56, 36):
    ax2.annotate("", xy=((X0 + X1) / 2, y - 1.6), xytext=((X0 + X1) / 2, y + 1.4), arrowprops=dict(arrowstyle="-|>", color="#495057", lw=1.6))
ax2.plot([X0 - 1, X0 - 7, X0 - 7], [24, 24, 84], color="#E8590C", lw=1.8)
ax2.annotate("", xy=(X0 - 0.8, 84), xytext=(X0 - 7.2, 84), arrowprops=dict(arrowstyle="-|>", color="#E8590C", lw=1.8))
ax2.text(X0 - 9, 54, "車が動くと\n距離が\n変わる\n↓\n次のコマで\nまた測る", fontsize=9, color="#D9480F", ha="right", va="center", linespacing=1.3)
ax2.text((X0 + X1) / 2, 8, "⑤ 調べる：記録をとってグラフにし、走り方を確かめる（6-8）", fontsize=9.5, color="#495057", ha="center", va="center",
         bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#ADB5BD", ls="--"))
ax2.set_title("update() の中で、毎コマくり返すこと", fontsize=11)
fig.savefig(f"{OUT}/fig1-overview.png", facecolor="white"); plt.close(fig)
print("ok")
