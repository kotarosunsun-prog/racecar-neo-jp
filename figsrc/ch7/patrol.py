"""
patrol.py
部屋の中を、ぶつからないように走り回る（7-2）。3つの状態を、ステートマシンで切りかえる。
  FORWARD：まっすぐ進む。前に物が近づいたら BACK へ
  BACK   ：少し下がる。1 秒たつか、後ろに物が近づいたら TURN へ
  TURN   ：空いているほうへ曲がりながら進む。1.5 秒たったら FORWARD へ（前に物が近づいたら BACK へ）
"""

import sys
from enum import IntEnum

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

HALF_WIDTH = 20.0      # 前と後ろの帯の幅の半分（cm）
NEAR = 50.0            # 前の物がこれより近くなったら、止まって下がる（cm）
BACK_TIME = 1.0        # 下がる時間（秒）
TURN_TIME = 1.5        # 曲がる時間（秒）


def lidar_angles(scan):
    """LIDAR の各点の角度（ラジアン）。0 が正面、時計回り。
    点の数は len(scan) から求める（シミュレータは 720 点、実機は 1080 点。9-3）"""
    return np.radians(np.arange(len(scan)) * 360 / len(scan))


class State(IntEnum):
    FORWARD = 0
    BACK = 1
    TURN = 2


state = State.FORWARD
timer = 0.0            # 今の状態になってからの時間（秒）
turn_dir = 1.0         # TURN で切るハンドルの向き（+1：右、-1：左）


def distance_in_band(scan, direction):
    """車の前（direction = +1）か後ろ（-1）の帯の中で、いちばん近い物までの距離（なければ 10000）"""
    angles = lidar_angles(scan)
    along = scan * np.cos(angles) * direction
    side = scan * np.sin(angles)
    inside = (scan > 0) & (along > 0) & (np.abs(side) < HALF_WIDTH)
    if not inside.any():
        return 10000.0
    return float(along[inside].min())


def change(new_state, scan):
    """状態を切りかえる。切りかえたときに1回だけすること（入るときの処理）も、ここに書く"""
    global state, timer, turn_dir
    state = new_state
    timer = 0.0
    if state == State.TURN:
        # 右ななめ前と左ななめ前をくらべて、空いているほうへ曲がる
        right = rc_utils.get_lidar_average_distance(scan, 45, 20)
        left = rc_utils.get_lidar_average_distance(scan, 315, 20)
        right = 1000.0 if right == 0.0 else right
        left = 1000.0 if left == 0.0 else left
        turn_dir = 1.0 if right > left else -1.0
    print(f"{state.name} へ")


def start():
    global state, timer
    state = State.FORWARD
    timer = 0.0
    rc.drive.stop()
    print(">> 部屋の中を走り回ります")


def update():
    global timer
    timer += rc.get_delta_time()
    scan = rc.lidar.get_samples()
    front = distance_in_band(scan, 1)
    back = distance_in_band(scan, -1)

    if state == State.FORWARD:
        speed, angle = 0.5, 0.0
        if front < NEAR:
            change(State.BACK, scan)
    elif state == State.BACK:
        speed, angle = -0.4, 0.0
        if timer > BACK_TIME or back < 30:
            change(State.TURN, scan)
    elif state == State.TURN:
        speed, angle = 0.4, turn_dir
        if front < NEAR:
            change(State.BACK, scan)
        elif timer > TURN_TIME:
            change(State.FORWARD, scan)

    rc.drive.set_speed_angle(speed, angle)


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
