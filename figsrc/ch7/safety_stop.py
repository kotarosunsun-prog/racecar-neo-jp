"""
safety_stop.py
人がコントローラーで運転し、車の前の帯の中に物が近づいたら、プログラムが前へ進むのを止める（7-1）。
右トリガー：前へ　左トリガー：後ろへ　左スティック：ハンドル
"""

import sys

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core

rc = racecar_core.create_racecar()

MAX_SPEED = 1.0        # トリガーをいっぱいに押したときの speed
HALF_WIDTH = 20.0      # 帯の幅の半分：車の幅の半分 ＋ 余裕（cm）
STOP_BASE = 15.0       # 止まっているときでも、これより近づかない（cm）
STOP_PER_SPEED = 60.0  # speed 1.0 あたり、止まるのに必要な距離（cm）。ブレーキテストで決める


def lidar_angles(scan):
    """LIDAR の各点の角度（ラジアン）。0 が正面、時計回り。
    点の数は len(scan) から求める（720 点なら 0.5° ずつ）"""
    return np.radians(np.arange(len(scan)) * 360 / len(scan))


stopped = False        # 安全停止が働いているか
ahead = 0.0            # 帯の中でいちばん近い物までの、前向きの距離


def distance_ahead(scan):
    """車の前の、幅 2 × HALF_WIDTH の帯の中で、いちばん近い物までの前向きの距離（なければ 10000）"""
    angles = lidar_angles(scan)
    forward = scan * np.cos(angles)          # 前向きの距離
    side = scan * np.sin(angles)             # 横向きの距離（＋：右）
    inside = (scan > 0) & (forward > 0) & (np.abs(side) < HALF_WIDTH)
    if not inside.any():
        return 10000.0
    return float(forward[inside].min())


def start():
    global stopped
    stopped = False
    rc.drive.stop()
    print(">> 右トリガーで前へ。前に物が近づくと、自動で止まります")


def update():
    global stopped, ahead
    rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    speed = (rt - lt) * MAX_SPEED
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]

    # 安全停止：前へ進もうとしていて、帯の中の物が、止まるのに必要な距離より近いなら、前へは進ませない
    ahead = distance_ahead(rc.lidar.get_samples())
    need = STOP_BASE + STOP_PER_SPEED * max(speed, 0.0)
    if speed > 0 and ahead < need:
        speed = 0.0
        if not stopped:
            print(f"安全停止！　前の物まで {ahead:.1f} cm")
        stopped = True
    else:
        stopped = False

    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    print(f"前の物まで {ahead:7.1f} cm　安全停止 {'中' if stopped else 'なし'}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
