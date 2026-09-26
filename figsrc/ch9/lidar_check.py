"""
lidar_check.py
LIDAR を 8 つの向き（45° ずつ）に分けて、測れなかった点（0.0）の割合と、いちばん近い物までの距離を表示する（9-3）。
ガラス・鏡・黒い物・遠すぎる所は、0.0 になりやすい。コースを走る前に、車を置いて確かめる。車は動かさない。
"""

import sys

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core

rc = racecar_core.create_racecar()

NAMES = ["前", "右前", "右", "右後ろ", "後ろ", "左後ろ", "左", "左前"]


def start():
    rc.drive.stop()
    print(">> 向きごとに、測れなかった点の割合と、いちばん近い物までの距離を表示します")


def update():
    rc.drive.stop()


def update_slow():
    scan = rc.lidar.get_samples()
    n = len(scan)                                    # 点の数（720）
    angles = np.arange(n) * 360 / n                  # 各点の角度（度）。0 が正面、時計回り
    sector = ((angles + 22.5) // 45).astype(int) % 8  # 前（-22.5°〜22.5°）が 0、そこから時計回りに 1、2、…
    words = []
    for k in range(8):
        part = scan[sector == k]
        zero = 100 * np.mean(part == 0)              # 0.0 の点の割合（%）
        near = part[part > 0].min() if (part > 0).any() else 0.0
        words.append(f"{NAMES[k]} {zero:3.0f}% {near:4.0f}cm")
    print(" | ".join(words))


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
