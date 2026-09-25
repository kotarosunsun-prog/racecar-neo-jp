"""
features.py
LIDAR のデータから、ニューラルネットワークに入れる9つの数（特徴）を作る（6-23）。
record_drive.py と drive_net.py の両方で、この同じ関数を使う。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_utils as rc_utils

ANGLES = (0, 30, 60, 90, 120, 240, 270, 300, 330)   # 見る向き（度）。0 が正面、時計回り
FAR = 300.0                                         # これより遠い（または見えない）ときは、この値にする


def lidar_features(scan):
    """9つの向きの距離を、100 cm を 1 とする数にして、リストで返す"""
    features = []
    for a in ANGLES:
        d = rc_utils.get_lidar_average_distance(scan, a, 6)
        if d == 0.0 or d > FAR:
            d = FAR
        features.append(d / 100)
    return features
