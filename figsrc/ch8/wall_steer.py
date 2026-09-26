"""
wall_steer.py
6-18 の wall_follow_course.py のハンドルを決める部分を、クラスにまとめたもの（7-13）。
walls.py と pid.py を同じフォルダに置いて使う。
"""

from enum import IntEnum

import racecar_utils as rc_utils
from pid import PID
from walls import side_wall, front_distance

HOLD = 10          # 新しい状態がこのコマ数だけ続いたら、切りかえる
FRONT_LIMIT = 200  # 正面の壁がこれより近いと、開いている側へ切りはじめる（cm）
KF = 0.02          # 正面の壁が 1 cm 近づくごとに、切る量


class State(IntEnum):
    BOTH = 0
    RIGHT = 1
    LEFT = 2
    NONE = 3


def seen_state(right, left):
    if right is not None and left is not None:
        return State.BOTH
    if right is not None:
        return State.RIGHT
    if left is not None:
        return State.LEFT
    return State.NONE


def open_side(scan):
    """右ななめ前と左ななめ前の、開いているほうを返す（＋1：右、－1：左）"""
    r = rc_utils.get_lidar_average_distance(scan, 45, 10)
    l = rc_utils.get_lidar_average_distance(scan, 315, 10)
    if r == 0.0:
        r = 1000.0
    if l == 0.0:
        l = 1000.0
    if r > l:
        return 1
    return -1


class WallSteer:
    """壁を見てハンドルの角度を決める。angle(scan, dt) を毎コマ呼ぶ"""

    def __init__(self):
        self.pid = PID(kp=0.04, ki=0.005, kd=0.04, i_zone=20)
        self.reset()

    def reset(self):
        self.pid.reset()
        self.state = State.BOTH
        self.candidate = State.BOTH
        self.count = 0
        self.target_right = 50.0
        self.target_left = 50.0

    def angle(self, scan, dt):
        right_angle, right = side_wall(scan, "right")
        left_angle, left = side_wall(scan, "left")

        # 1. 状態を決める（6-17）
        seen = seen_state(right, left)
        if seen == self.state:
            self.count = 0
        else:
            if seen == self.candidate:
                self.count += 1
            else:
                self.candidate = seen
                self.count = 1
            if self.count >= HOLD:
                self.state = seen
                self.count = 0
                self.pid.reset()
                if self.state == State.RIGHT:
                    self.target_right = right
                if self.state == State.LEFT:
                    self.target_left = left

        # 2. 状態に合わせて、ずれと向きを決める（6-16、6-17）
        angle = 0.0
        if self.state == State.BOTH and right is not None and left is not None:
            angle = self.pid.update((right - left) / 2, dt, rate=(right_angle - left_angle) / 2)
        elif self.state == State.RIGHT and right is not None:
            angle = self.pid.update(right - self.target_right, dt, rate=right_angle)
        elif self.state == State.LEFT and left is not None:
            angle = self.pid.update(self.target_left - left, dt, rate=-left_angle)

        # 3. 正面に壁が近づいたら、開いている側へ切る（6-18）
        front = front_distance(scan)
        if front < FRONT_LIMIT:
            angle += open_side(scan) * KF * (FRONT_LIMIT - front)
        return rc_utils.clamp(angle, -1.0, 1.0)
