"""
cone_park.py
コーンを探して近づき、コーンの 30 cm 手前に止まる（7-3、Lab G）。4つの状態をステートマシンで切りかえる。
  SEARCH  ：コーンが見えるまで、ゆっくり円をえがいて探す
  APPROACH：コーンのほうへハンドルを切りながら近づく（速さは P だけ）
  PARK    ：目標の距離の近くで、PI で少しずつ合わせる
  PARKED  ：止まって待つ。距離がずれたら PARK へ、コーンを見失ったら SEARCH へ
pid.py を同じフォルダに置いて使う。
"""

import sys
from enum import IntEnum

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from pid import PID

rc = racecar_core.create_racecar()

CONE = ((90, 50, 50), (120, 255, 255))   # コーンの色（説明用のモデルでは青。Lab G のオレンジは自分で測る）
MIN_CONTOUR_AREA = 30                    # これより小さいかたまりは無視する
HALF_FOV = 34.7                          # カメラの横の視野の半分（度）。画面の右はしが、正面から右へ何度か
TARGET = 42.5                            # LIDAR で測った、コーンまでの距離の目標（cm）。画面の表示が 30 cm になる値
PARK_ZONE = 10.0                         # 目標までこの距離（cm）より近づいたら、APPROACH から PARK へ
DONE = 1.0                               # 目標とのずれがこれより小さい状態が、
HOLD_TIME = 1.0                          # この時間（秒）続いたら、PARKED へ


class State(IntEnum):
    SEARCH = 0
    APPROACH = 1
    PARK = 2
    PARKED = 3


steer_pid = PID(kp=1.0, ki=0.0, kd=0.0)
park_pid = PID(kp=0.01, ki=0.01, kd=0.0, i_zone=PARK_ZONE, out_min=-0.3, out_max=0.3)

state = State.SEARCH
timer = 0.0            # 今の状態になってからの時間（秒）
good_time = 0.0        # PARK で、ずれが DONE より小さい状態が続いている時間（秒）
distance = 0.0


def find_cone():
    """コーンの中心の列を -1〜1 で返す。見えなければ None"""
    image = rc.camera.get_color_image()
    if image is None:
        return None
    contours = rc_utils.find_contours(image, CONE[0], CONE[1])
    contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)
    if contour is None:
        return None
    center = rc_utils.get_contour_center(contour)     # (行, 列)
    half = rc.camera.get_width() / 2
    return (center[1] - half) / half


def cone_distance(scan, x):
    """カメラで見たコーンの向きの ±5° で、いちばん近い点に近い点だけを平均した距離（6-6 の方法）"""
    a = x * HALF_FOV                                  # コーンの向き（度。右が＋）
    i = round(a * len(scan) / 360)                    # その向きの点の番号
    near = scan[np.arange(i - 10, i + 11) % len(scan)]   # ±5°（21 点）。0° をまたいでもよいように % を使う
    near = near[near > 0]                             # 0.0（測れなかった点）は使わない
    if len(near) == 0:
        return 0.0
    closest = near.min()
    return float(near[near < closest + 5].mean())     # いちばん近い点から 5 cm 以内の点の平均


def change(new_state):
    global state, timer, good_time
    state = new_state
    timer = 0.0
    good_time = 0.0
    if state == State.PARK:
        park_pid.reset()
    print(f"{state.name} へ（コーンまで {distance:.1f} cm）")


def start():
    global state, timer
    state = State.SEARCH
    timer = 0.0
    rc.drive.stop()
    print(">> コーンを探して、30 cm 手前に止まります")


def update():
    global timer, good_time, distance
    dt = rc.get_delta_time()
    timer += dt
    x = find_cone()
    if x is not None:
        distance = cone_distance(rc.lidar.get_samples(), x)
        error = distance - TARGET

    # どの状態でも：コーンを見失ったら、探しなおす
    if x is None and state != State.SEARCH:
        change(State.SEARCH)

    speed, angle = 0.0, 0.0
    if state == State.SEARCH:
        speed, angle = 0.2, 1.0                        # ゆっくり右回りの円をえがく
        if x is not None:
            steer_pid.reset()
            change(State.APPROACH)
    elif state == State.APPROACH:
        angle = steer_pid.update(x, dt)
        speed = rc_utils.clamp(0.01 * error, -0.3, 0.5)
        if abs(error) < PARK_ZONE:
            change(State.PARK)
    elif state == State.PARK:
        angle = steer_pid.update(x, dt)
        speed = park_pid.update(error, dt)
        if abs(error) >= 2 * PARK_ZONE:
            change(State.APPROACH)
        else:
            good_time = good_time + dt if abs(error) < DONE else 0.0
            if good_time > HOLD_TIME:
                change(State.PARKED)
    elif state == State.PARKED:
        if abs(error) > 3 * DONE:
            change(State.PARK)

    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    print(f"{state.name:8}　コーンまで {distance:5.1f} cm")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
