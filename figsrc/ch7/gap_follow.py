"""
gap_follow.py
LIDAR で正面 ±90° の「空き」を探し、選んだ空きの向きへ走る（Gap Follower、7-7〜7-11）。
gaps.py を同じフォルダに置いて使う。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from gaps import (front_view, find_gaps, widest_gap, deepest_gap, gap_center, gap_farthest,
                  add_bubble, extend_disparities)

rc = racecar_core.create_racecar()

FULL_TURN = 30.0     # 目標の向きがこの角度（度）より横にあったら、ハンドルをいっぱいに切る
THRESHOLD = 150.0    # これより遠くまで見える向きを「空き」とする（cm）
PICK = "widest"      # どの空きを選ぶか："widest"（いちばん広い）/ "deepest"（いちばん遠くまで見える）（7-8）
AIM = "center"       # 空きのどこを狙うか："center"（真ん中）/ "farthest"（いちばん遠い点）（7-8）
BUBBLE = 20.0        # 0 でなければ、いちばん近い点のまわりを、この半径（cm）でふさぐ（7-9）
HALF_WIDTH = 20.0    # 0 でなければ、物のはしで、近い距離を、この幅（cm）が入る角度だけのばす（7-10）
JUMP = 50.0          # となりの点との距離の差がこれより大きい所を、物のはしとみなす（7-10）
MIN_SPEED = 0.4      # いちばん遅いときの speed（7-11）
MAX_SPEED = 1.0      # いちばん速いときの speed（7-11。MIN_SPEED と同じなら、一定の速さ）
KV = 0.004           # 目標の向きの距離が 1 cm 遠いごとに、speed をどれだけ上げるか（7-11）

target = 0.0         # 目標の向き（度。右が＋）
speed = 0.0
n_gaps = 0


def start():
    rc.drive.stop()
    print(">> 空きを探して走ります")


def update():
    global target, speed, n_gaps
    angles, dists = front_view(rc.lidar.get_samples())
    if HALF_WIDTH > 0:
        dists = extend_disparities(angles, dists, HALF_WIDTH, JUMP)
    if BUBBLE > 0:
        dists = add_bubble(angles, dists, BUBBLE)

    gaps = find_gaps(dists, THRESHOLD)
    n_gaps = len(gaps)
    if n_gaps == 0:                       # 空きがない：止まる
        speed = 0.0
        rc.drive.stop()
        return

    if PICK == "widest":
        gap = widest_gap(gaps)
    else:
        gap = deepest_gap(gaps, dists)
    if AIM == "center":
        target = gap_center(gap, angles)
    else:
        target = gap_farthest(gap, angles, dists)

    # 目標の向きが遠くまで空いているほど速く（7-11）
    i = int(round((target - angles[0]) / (angles[1] - angles[0])))   # 目標の向きの点の番号
    speed = rc_utils.clamp(MIN_SPEED + KV * (dists[i] - THRESHOLD), MIN_SPEED, MAX_SPEED)
    angle = rc_utils.clamp(target / FULL_TURN, -1.0, 1.0)
    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    print(f"空き {n_gaps} 個　目標の向き {target:+6.1f}°　speed {speed:.2f}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
