"""
drive_net.py
train_drive.py で学習させたニューラルネットワーク（drive_net.npz）で、ハンドルを決めて走る（6-23）。
LB ボタンを押している間は、人が左スティックで「自分ならこう切る」を示すと、
そのときの見え方といっしょに記録する（ネットワークの運転はそのまま）。B ボタンで drive_log.csv に書き足す。
features.py と drive_net.npz を同じフォルダに置いて使う。
"""

import sys

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from features import lidar_features

rc = racecar_core.create_racecar()

SPEED = 0.5                       # 記録したときと同じ速さで走る
net = np.load("drive_net.npz")
W1, b1, W2, b2 = net["W1"], net["b1"], net["W2"], float(net["b2"])
x_mean, x_std = net["x_mean"], net["x_std"]   # 学習のときと同じように、特徴をそろえる

angle = 0.0
rows = []         # 教えた記録：[特徴9つ, 人が示したハンドルの角度]


def start():
    rc.drive.stop()
    print(">> 学習したネットワークで走ります")


def update():
    global angle
    scan = rc.lidar.get_samples()
    x = (np.array(lidar_features(scan)) - x_mean) / x_std
    out = np.tanh(x @ W1 + b1) @ W2 + b2        # 前向きの計算だけ
    angle = rc_utils.clamp(float(out), -1.0, 1.0)
    rc.drive.set_speed_angle(SPEED, angle)

    # LB を押している間は、人が示した角度を記録する（車を動かすのは、ネットワークのまま）
    if rc.controller.is_down(rc.controller.Button.LB):
        teach = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]
        rows.append(lidar_features(scan) + [teach])
    if rc.controller.was_pressed(rc.controller.Button.B) and len(rows) > 0:
        with open("drive_log.csv", "a") as f:
            np.savetxt(f, np.array(rows), delimiter=",", fmt="%.4f")
        print(f"{len(rows)} コマ分を drive_log.csv に書き足しました")
        rows.clear()


def update_slow():
    print(f"angle {angle:+.2f}　教えたコマ数 {len(rows)}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
