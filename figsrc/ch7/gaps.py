"""
gaps.py
LIDAR のデータから「空き」（車が進めそうな向きのまとまり）を見つけるための関数（第7章）。
7-6 から 7-10 で、1つずつ足していく。
"""

import math

import numpy as np

HALF_VIEW = 90        # 正面から左右それぞれ何度までを見るか
MAX_RANGE = 300.0     # これより遠い値と、0.0（測れなかった）は、この値にそろえる（cm）


def front_view(scan):
    """正面 ±HALF_VIEW° の点を、左はしから右はしの順に並べて、(角度, 距離) の配列で返す。
    角度は度で、正面が 0、右が＋、左が－。"""
    step = 360 / len(scan)                     # となりの点との角度（0.5°）
    k = int(HALF_VIEW / step)
    offsets = np.arange(-k, k + 1)             # -180 … 180（点の番号の、正面からのずれ）
    angles = offsets * step
    dists = scan[offsets % len(scan)].astype(float)
    dists[dists == 0] = MAX_RANGE              # 測れなかった所は、遠くまで何もないとみなす
    dists = np.minimum(dists, MAX_RANGE)       # 遠すぎる値は、MAX_RANGE にそろえる
    return angles, dists


def find_gaps(dists, threshold):
    """距離が threshold より大きい点が続く区間（空き）を、(はじめの番号, おわりの番号) のリストで返す"""
    gaps = []
    start = None
    for i, d in enumerate(dists):
        if d > threshold and start is None:
            start = i                          # 空きのはじまり
        if d <= threshold and start is not None:
            gaps.append((start, i - 1))        # 空きのおわり
            start = None
    if start is not None:
        gaps.append((start, len(dists) - 1))   # 右はしまで続く空き
    return gaps


def widest_gap(gaps):
    """いちばん幅の広い空き"""
    return max(gaps, key=lambda g: g[1] - g[0])


def deepest_gap(gaps, dists):
    """いちばん遠くまで見える点をふくむ空き"""
    return max(gaps, key=lambda g: dists[g[0]:g[1] + 1].max())


def gap_center(gap, angles):
    """空きの真ん中の角度"""
    return (angles[gap[0]] + angles[gap[1]]) / 2


def gap_farthest(gap, angles, dists):
    """空きの中で、いちばん遠い点の角度"""
    i = gap[0] + int(np.argmax(dists[gap[0]:gap[1] + 1]))
    return angles[i]


def add_bubble(angles, dists, radius):
    """いちばん近い点を中心に、半径 radius の円が見える向きを、ふさぐ（距離を 0 にする）"""
    i = int(np.argmin(dists))
    near = dists[i]
    if near <= radius:
        half = 90.0                            # 円の中にいる：大きくふさぐ
    else:
        half = math.degrees(math.asin(radius / near))
    out = dists.copy()
    out[np.abs(angles - angles[i]) <= half] = 0.0
    return out


def extend_disparities(angles, dists, half_width, jump):
    """となりの点との距離の差が jump より大きい所（物のはし）で、近いほうの距離を、
    車の幅の半分が入る角度だけ、遠いほうへのばす"""
    out = dists.copy()
    for i in range(len(dists) - 1):
        a, b = dists[i], dists[i + 1]
        if abs(a - b) <= jump:
            continue
        near = min(a, b)
        spread = math.degrees(math.atan2(half_width, near))   # 車の幅の半分が見える角度
        if a < b:            # 右どなりが遠い：近い距離を右へのばす
            mask = (angles > angles[i]) & (angles <= angles[i] + spread)
        else:                # 左どなりが遠い：近い距離を左へのばす
            mask = (angles < angles[i + 1]) & (angles >= angles[i + 1] - spread)
        out[mask] = np.minimum(out[mask], near)
    return out
