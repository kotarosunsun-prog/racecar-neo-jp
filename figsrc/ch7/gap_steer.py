"""
gap_steer.py
7-10 までの Gap Follower のハンドルを決める部分を、関数にまとめたもの（7-13）。
gaps.py を同じフォルダに置いて使う。
"""

import racecar_utils as rc_utils
from gaps import front_view, find_gaps, widest_gap, gap_center, add_bubble, extend_disparities

FULL_TURN = 30.0     # 目標の向きがこの角度（度）より横にあったら、ハンドルをいっぱいに切る
THRESHOLD = 150.0    # これより遠くまで見える向きを「空き」とする（cm）
BUBBLE = 20.0        # いちばん近い点のまわりをふさぐ半径（cm）（7-9）
HALF_WIDTH = 20.0    # 物のはしで、近い距離をのばす幅（cm）（7-10）
JUMP = 50.0          # 物のはしとみなす、となりの点との距離の差（cm）（7-10）


def gap_angle(scan):
    """いちばん広い空きの真ん中へ向かう angle を返す。空きがなければ None"""
    angles, dists = front_view(scan)
    dists = extend_disparities(angles, dists, HALF_WIDTH, JUMP)
    dists = add_bubble(angles, dists, BUBBLE)
    gaps = find_gaps(dists, THRESHOLD)
    if len(gaps) == 0:
        return None
    target = gap_center(widest_gap(gaps), angles)
    return rc_utils.clamp(target / FULL_TURN, -1.0, 1.0)
