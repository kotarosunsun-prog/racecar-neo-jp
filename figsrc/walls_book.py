"""
walls.py
LIDAR で、左右の壁の向きと距離、正面の距離を求める関数（6-16）。
使い方：
    from walls import side_wall, front_distance
"""

import math
import racecar_utils as rc_utils

THETA = 30        # 2本の光線の間の角度（度）
MAX_WALL = 300.0  # これより遠い壁は「見えない」とみなす（cm）
MAX_ANGLE = 45    # 壁の向きがこれより大きいときは、2本の光線が同じ壁に当たっていないとみなす（度）


def side_wall(scan, side):
    """side が "right" なら右の壁、"left" なら左の壁の、(向き〔度〕, 距離〔cm〕) を返す。
    向きが＋なら、その壁から離れる向きに走っている。見えなければ (None, None)"""
    if side == "right":
        a = rc_utils.get_lidar_average_distance(scan, 90 - THETA)    # 右ななめ前（60°）
        b = rc_utils.get_lidar_average_distance(scan, 90)            # 右（90°）
    else:
        a = rc_utils.get_lidar_average_distance(scan, 270 + THETA)   # 左ななめ前（300°）
        b = rc_utils.get_lidar_average_distance(scan, 270)           # 左（270°）
    if a == 0.0 or b == 0.0 or b > MAX_WALL:
        return None, None
    t = math.radians(THETA)
    alpha = math.atan2(a * math.cos(t) - b, a * math.sin(t))
    if abs(math.degrees(alpha)) > MAX_ANGLE:         # 壁がとぎれている（入り口や曲がり角）
        return None, None
    return math.degrees(alpha), b * math.cos(alpha)


def front_distance(scan, half_width=10):
    """正面（±half_width 度）で、いちばん近い物までの距離（cm）"""
    _, distance = rc_utils.get_lidar_closest_point(scan, (360 - half_width, half_width))
    return distance
