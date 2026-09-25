"""
record_drive.py
人がコントローラーで運転しながら、LIDAR の見え方と、そのときのハンドルの角度を記録する（6-23）。
右トリガー：前へ（いっぱいに押すと speed 0.5）　左スティック：ハンドル
B ボタン：それまでの記録を drive_log.csv の最後に書き足す（何回走っても、記録がたまっていく）
features.py を同じフォルダに置いて使う。
"""

import sys

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
from features import lidar_features

rc = racecar_core.create_racecar()

MAX_SPEED = 0.5   # 右トリガーをいっぱいに押したときの speed
rows = []         # 記録：1コマごとに [特徴9つ, ハンドルの角度]


def start():
    rows.clear()
    rc.drive.stop()
    print(">> 右トリガーで前へ、左スティックでハンドル。B ボタンで記録を保存します")


def update():
    speed = rc.controller.get_trigger(rc.controller.Trigger.RIGHT) * MAX_SPEED
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]
    rc.drive.set_speed_angle(speed, angle)

    # 走っているときだけ、見え方と、人が決めたハンドルの角度を記録する
    if speed > 0.4:
        scan = rc.lidar.get_samples()
        rows.append(lidar_features(scan) + [angle])

    if rc.controller.was_pressed(rc.controller.Button.B) and len(rows) > 0:
        with open("drive_log.csv", "a") as f:         # "a"：前の記録の後ろに書き足す
            np.savetxt(f, np.array(rows), delimiter=",", fmt="%.4f")
        print(f"{len(rows)} コマ分を drive_log.csv に書き足しました")
        rows.clear()


def update_slow():
    print(f"記録したコマ数 {len(rows)}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
