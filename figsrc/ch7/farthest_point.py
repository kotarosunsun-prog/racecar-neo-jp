"""
farthest_point.py
LIDAR のすべての点（シミュレータでは 720 点）の中で、いちばん遠い点の向きへハンドルを切る（7-5）。
"""

import sys

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

SPEED = 0.5          # 走る速さ（一定）
FULL_TURN = 30.0     # いちばん遠い点がこの角度（度）より横にあったら、ハンドルをいっぱいに切る

target = 0.0         # いちばん遠い点の角度（度。正面が 0、右が＋、左が－）
far = 0.0            # いちばん遠い点までの距離


def start():
    rc.drive.stop()
    print(">> いちばん遠い点の向きへ走ります")


def update():
    global target, far
    scan = rc.lidar.get_samples()
    i = int(np.argmax(scan))                   # いちばん遠い点の番号（0.0 = 測れなかった点は、選ばれない）
    far = float(scan[i])
    target = i * 360 / len(scan)               # 0〜360°
    if target > 180:
        target -= 360                          # -180〜180° にする（左が－）
    angle = rc_utils.clamp(target / FULL_TURN, -1.0, 1.0)
    rc.drive.set_speed_angle(SPEED, angle)


def update_slow():
    print(f"いちばん遠い点：{target:+6.1f}° の向き、{far:6.1f} cm")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
