"""
farthest_front.py
正面 ±90° だけを見て、遠すぎる値をそろえてから、いちばん遠い点の向きへハンドルを切る（7-6）。
gaps.py を同じフォルダに置いて使う。
"""

import sys

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from gaps import front_view

rc = racecar_core.create_racecar()

SPEED = 0.5          # 走る速さ（一定）
FULL_TURN = 30.0     # 目標の向きがこの角度（度）より横にあったら、ハンドルをいっぱいに切る

target = 0.0


def start():
    rc.drive.stop()
    print(">> 正面 ±90° の中で、いちばん遠い点の向きへ走ります")


def update():
    global target
    angles, dists = front_view(rc.lidar.get_samples())
    best = np.flatnonzero(dists == dists.max())          # いちばん遠い点（同じ距離の点が、いくつもあることがある）
    i = best[np.argmin(np.abs(angles[best]))]            # その中で、いちばん正面に近い点
    target = angles[i]
    angle = rc_utils.clamp(target / FULL_TURN, -1.0, 1.0)
    rc.drive.set_speed_angle(SPEED, angle)


def update_slow():
    print(f"目標の向き {target:+6.1f}°")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
