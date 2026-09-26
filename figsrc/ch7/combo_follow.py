"""
combo_follow.py
壁沿い走行（WallSteer）と Gap Follower（gap_angle）を、前の帯の中の物までの距離で切りかえる（7-13）。
  WALL：ふだんは壁沿い走行。前の帯に物が NEAR より近づいたら GAP へ
  GAP ：Gap Follower。前の帯の物が FAR より遠くなったら WALL へもどる
wall_steer.py・gap_steer.py・walls.py・pid.py・gaps.py を同じフォルダに置いて使う。
"""

import sys
from enum import IntEnum

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
from wall_steer import WallSteer
from gap_steer import gap_angle

rc = racecar_core.create_racecar()

SPEED = 0.5
HALF_WIDTH = 20.0      # 前の帯の幅の半分（cm）（7-1）
NEAR = 150.0           # 前の帯の物がこれより近くなったら、GAP へ（cm）
FAR = 250.0            # 前の帯の物がこれより遠くなったら、WALL へ（cm）。NEAR とあいだをあける（6-17）
BLEND = False          # True にすると、切りかえずに、2つの角度を混ぜ合わせる


def lidar_angles(scan):
    """LIDAR の各点の角度（ラジアン）。0 が正面、時計回り。
    点の数は len(scan) から求める（シミュレータは 720 点、実機は 1080 点。9-3）"""
    return np.radians(np.arange(len(scan)) * 360 / len(scan))


class Mode(IntEnum):
    WALL = 0
    GAP = 1


wall = WallSteer()
mode = Mode.WALL
ahead = 0.0


def distance_ahead(scan):
    """車の前の、幅 2 × HALF_WIDTH の帯の中で、いちばん近い物までの前向きの距離（7-1）"""
    angles = lidar_angles(scan)
    forward = scan * np.cos(angles)
    side = scan * np.sin(angles)
    inside = (scan > 0) & (forward > 0) & (np.abs(side) < HALF_WIDTH)
    if not inside.any():
        return 10000.0
    return float(forward[inside].min())


def start():
    global mode
    mode = Mode.WALL
    wall.reset()
    rc.drive.stop()
    print(">> 壁沿い走行と Gap Follower を切りかえて走ります")


def update():
    global mode, ahead
    scan = rc.lidar.get_samples()
    dt = rc.get_delta_time()
    ahead = distance_ahead(scan)

    if mode == Mode.WALL and ahead < NEAR:
        mode = Mode.GAP
        print(f"GAP へ（前の物まで {ahead:.0f} cm）")
    elif mode == Mode.GAP and ahead > FAR:
        mode = Mode.WALL
        if not BLEND:
            wall.reset()                     # 壁沿い走行を、はじめからやり直す
        print(f"WALL へ（前の物まで {ahead:.0f} cm）")

    wall_angle = wall.angle(scan, dt)        # 壁沿い走行の角度は、いつも計算しておく
    g = gap_angle(scan)
    angle = wall_angle
    if BLEND:
        if g is not None:
            w = min(1.0, max(0.0, (ahead - NEAR) / (FAR - NEAR)))   # 前が空いているほど 1（壁沿い）に近い
            angle = w * wall_angle + (1 - w) * g
    elif mode == Mode.GAP and g is not None:
        angle = g
    rc.drive.set_speed_angle(SPEED, angle)


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
