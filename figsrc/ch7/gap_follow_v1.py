"""
gap_follow.py
LIDAR で正面 ±90° の「空き」を探し、いちばん広い空きの真ん中へ向かって走る（7-7）。
gaps.py を同じフォルダに置いて使う。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from gaps import front_view, find_gaps, widest_gap, gap_center

rc = racecar_core.create_racecar()

SPEED = 0.5          # 走る速さ（一定）
FULL_TURN = 30.0     # 目標の向きがこの角度（度）より横にあったら、ハンドルをいっぱいに切る
THRESHOLD = 150.0    # これより遠くまで見える向きを「空き」とする（cm）

target = 0.0         # 目標の向き（度。右が＋）
gaps = []
view = []            # 正面 ±90° の点の角度（update_slow() の表示に使う）


def start():
    rc.drive.stop()
    print(">> いちばん広い空きの真ん中へ走ります")


def update():
    global target, gaps, view
    angles, dists = front_view(rc.lidar.get_samples())
    view = angles
    gaps = find_gaps(dists, THRESHOLD)
    if len(gaps) == 0:                    # 空きがない：止まる
        rc.drive.stop()
        return
    gap = widest_gap(gaps)
    target = gap_center(gap, angles)
    angle = rc_utils.clamp(target / FULL_TURN, -1.0, 1.0)
    rc.drive.set_speed_angle(SPEED, angle)


def update_slow():
    text = "、".join(f"{view[a]:.0f}°〜{view[b]:.0f}°" for a, b in gaps)
    print(f"空き：{text}　目標の向き {target:+.1f}°")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
