"""Figures for 7-4: slalom.py on a straight and a curved line of cones (sim2d model)."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ch7"))
import ch7run as C
import courses7 as K
import sim2d, wallsim
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/7-4"
P = C.r._orig
FILL = {"blue": "#1C7ED6", "other": "#9C36B5"}


def run(cones, T=25, subs=(), seed=0):
    segs = []
    for x, y, c in cones: segs += sim2d.cone_segments(x, y)
    w = sim2d.World(segs, x=0, y=0, heading_deg=90, seed=seed, **wallsim.REAL)
    cam = sim2d.ConeCamera([(x, y, 10.0, 30.0, K.BLUE_BGR if c == "blue" else K.OTHER_BGR) for x, y, c in cones]); rng = np.random.default_rng(seed)
    w, out = C.run("slalom.py", w, T, image=lambda f: cam.render(w, rng=rng), subs=subs)
    L = np.array(w.log); res = []
    for x, y, c in cones:
        idx = np.where(L[:, 2] >= y)[0]
        if not len(idx): res.append("—"); continue
        left = L[idx[0], 1] < x
        res.append(("左" if left else "右") + ("○" if left == (c == "blue") else "×"))
    return w, out, L, res


SHOW = 1                                           # the seed drawn in the figure (RETURN_TURN 0.6 fails on the curved row)
runs = {}
for seed in (0, 1, 2, 3):
    for kind in ("straight", "curved"):
        for lab, subs in (("RETURN_TURN 0.8", []), ("RETURN_TURN 0.6", [("RETURN_TURN = 0.8 ", "RETURN_TURN = 0.6 ")])):
            w, out, L, res = run(K.slalom_cones(kind), subs=subs, seed=seed)
            if seed == SHOW: runs[(kind, lab)] = (L, res, w.crashed, out)
            P("seed", seed, kind, lab, "crashed" if w.crashed else "", res, round(len(L) / 60, 1), [t for f, t in out][:3], flush=True)

fig = plt.figure(figsize=(11.2, 6.2), dpi=200)
axi = fig.add_axes([0.03, 0.3, 0.34, 0.5])
w0 = sim2d.World([], x=0, y=0, heading_deg=90)
cones = K.slalom_cones("curved")
img = sim2d.ConeCamera([(x, y, 10.0, 30.0, K.BLUE_BGR if c == "blue" else K.OTHER_BGR) for x, y, c in cones]).render(w0, rng=np.random.default_rng(1))
axi.imshow(img[:, :, ::-1]); axi.set_xticks([0, 320, 639]); axi.set_yticks([0, 240, 479]); axi.tick_params(labelsize=8)
axi.set_title("スタートで見たコーン（曲がった列）", fontsize=10)
for k, (kind, title) in enumerate((("straight", "まっすぐな列"), ("curved", "曲がった列"))):
    ax = fig.add_axes([0.42 + k * 0.29, 0.07, 0.26, 0.84])
    for lab, col, ls in (("RETURN_TURN 0.8", "#E8590C", "-"), ("RETURN_TURN 0.6", "#868E96", "--")):
        L, res, crashed, out = runs[(kind, lab)]
        ok = sum(r.endswith("○") for r in res)
        ax.plot(L[:, 1], L[:, 2], color=col, lw=1.8, ls=ls, label=f"{lab}：{ok}/6 本" + ("\n（ぶつかった）" if crashed else ""))
        if crashed: ax.plot(L[-1, 1], L[-1, 2], "x", color=col, ms=9, mew=2.5)
    for x, y, c in K.slalom_cones(kind):
        ax.add_patch(plt.Circle((x, y), 10, color=FILL[c]))
    ax.plot([0], [0], "o", color="#212529", ms=5)
    ax.set_aspect("equal"); ax.set_xlim(-230, 230); ax.set_ylim(-60, 1150); ax.grid(alpha=0.3)
    ax.set_xlabel("横〔cm〕"); ax.set_title(title, fontsize=10.5)
    ax.legend(fontsize=8.5, loc="upper left", frameon=True, framealpha=0.95)
    if k == 0: ax.set_ylabel("縦〔cm〕")
fig.suptitle("コーンスラローム：青は左側、紫（Lab H では赤）は右側を通る（説明用の簡単なモデル）", fontsize=11)
fig.savefig(f"{OUT}/fig1-slalom.png", facecolor="white"); plt.close(fig)
