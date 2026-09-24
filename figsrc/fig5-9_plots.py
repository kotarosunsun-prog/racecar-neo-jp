"""Figures for 5-9: activation functions, and the hidden/output values of the red network over H."""
import os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/5-9"
z = np.linspace(-6, 6, 400)
fig, axs = plt.subplots(1, 3, figsize=(9.6, 2.9), dpi=200)
for ax, yv, t in [(axs[0], (z > 0).astype(float), "ステップ関数"), (axs[1], 1 / (1 + np.exp(-z)), "シグモイド関数"), (axs[2], np.maximum(0, z), "ReLU（レル）")]:
    ax.plot(z, yv, color="#2F9E44", lw=2.6); ax.set_title(t, fontsize=11); ax.grid(alpha=0.3); ax.set_xlabel("z")
    ax.axhline(0, color="#ADB5BD", lw=0.8); ax.axvline(0, color="#ADB5BD", lw=0.8)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
axs[0].set_ylabel("f(z)")
axs[2].set_ylim(-0.5, 6)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2-activation.png", facecolor="white"); plt.close(fig)

h = np.arange(0, 180)
n1 = (-h + 10 > 0).astype(float); n2 = (h - 170 > 0).astype(float); out = (n1 + n2 - 0.5 > 0).astype(float)
fig, axs = plt.subplots(3, 1, figsize=(7.6, 4.6), dpi=200, sharex=True)
for ax, v, name, col in [(axs[0], n1, "n1（H < 10 なら 1）", "#F08C00"), (axs[1], n2, "n2（H > 170 なら 1）", "#F08C00"), (axs[2], out, "出力：赤？", "#E03131")]:
    ax.fill_between(h, 0, v, step="mid", color=col, alpha=0.35); ax.step(h, v, where="mid", color=col, lw=2)
    ax.set_ylim(-0.1, 1.25); ax.set_yticks([0, 1]); ax.text(1.0, 1.02, name, transform=ax.transAxes, ha="right", va="bottom", fontsize=10)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
axs[2].set_xlabel("色合い H"); axs[2].set_xticks([0, 10, 30, 60, 90, 120, 150, 170, 179])
fig.suptitle("かくれ層の2つのニューロンと、出力の値", fontsize=11)
fig.tight_layout(); fig.savefig(f"{OUT}/fig4-red-output.png", facecolor="white"); plt.close(fig)
