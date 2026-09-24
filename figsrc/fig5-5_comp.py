"""Figure for 5-5: accelerometer-only vs gyro-only vs complementary filter on synthetic pitch data."""
import os, io, contextlib, runpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/5-5"; os.makedirs(OUT, exist_ok=True)
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("fig5-5_comp_demo.py")
t, true, acc, gyro_only, fused = g["t"], g["true"], g["acc"], g["gyro_only"], g["fused"]
fig, ax = plt.subplots(figsize=(8.2, 5.0), dpi=200)
ax.axvspan(4, 5, color="#FFE8CC", zorder=0)
ax.text(4.5, 19.3, "加速中", ha="center", fontsize=10, color="#D9480F")
ax.plot(t, acc, color="#F08C00", lw=0.8, alpha=0.8, label="加速度だけ（ばらつく・加速中にずれる）")
ax.plot(t, gyro_only, color="#1C7ED6", lw=1.8, label="ジャイロだけ（なめらかだが、だんだんずれる）")
ax.plot(t, fused, color="#2F9E44", lw=2.6, label="相補フィルタ（α = 0.98）")
ax.plot(t, true, color="#212529", lw=1.6, ls="--", label="本当の傾き")
ax.set_xlabel("時間〔秒〕"); ax.set_ylabel("前後の傾き〔度〕"); ax.set_ylim(-6, 21); ax.set_xlim(0, 12)
ax.grid(alpha=0.3); ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=9, frameon=False)
ax.set_title("同じ動きを3つの方法で測った結果（説明用に作ったデータ）", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1-comp-filter.png", facecolor="white"); plt.close(fig)
