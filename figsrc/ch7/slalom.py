"""
slalom.py
コーンスラローム（7-4）。青いコーンは左側を、もう1色のコーンは右側を通りぬける。
  APPROACH：いちばん近いコーンの、通りたい側へ PASS cm ずらした所をめざす
  RETURN  ：コーンが見えなくなったら、コーンの列のほうへ曲がりながら、次のコーンを探す
"""

import math
import sys
from enum import IntEnum

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

# 説明用のモデルの色。Lab H の赤いコーンの色の範囲は、5-1 の方法で自分で測る
BLUE = ((90, 50, 50), (120, 255, 255))      # 左側を通るコーン（Lab E・Lab F のひな形の青）
OTHER = ((140, 80, 80), (170, 255, 255))    # 右側を通るコーン（このモデルでは紫。Lab H では赤）
MIN_CONTOUR_AREA = 30
HALF_FOV = 34.7        # カメラの横の視野の半分（度）
PASS = 50.0            # コーンの中心から、どれだけ横を通るか（cm）
FULL_TURN = 30.0       # 目標の向きがこの角度（度）より横にあったら、ハンドルをいっぱいに切る
SPEED = 0.4
RETURN_TURN = 0.8      # RETURN で切るハンドルの大きさ


class State(IntEnum):
    APPROACH = 0
    RETURN = 1


state = State.RETURN
last_side = -1.0       # 最後に通ったコーンで、車がどちら側を通ったか（-1：左、+1：右）
aim = 0.0              # 目標の向き（度）


def nearest_cone():
    """見えているコーンのうち、いちばん大きく写っている（近い）ものを (色, 列 -1〜1) で返す。なければ None"""
    image = rc.camera.get_color_image()
    if image is None:
        return None
    best = None
    for color, (low, high) in (("blue", BLUE), ("other", OTHER)):
        contour = rc_utils.get_largest_contour(rc_utils.find_contours(image, low, high), MIN_CONTOUR_AREA)
        if contour is not None:
            area = rc_utils.get_contour_area(contour)
            if best is None or area > best[0]:
                col = rc_utils.get_contour_center(contour)[1]
                best = (area, color, (col - 320) / 320)
    if best is None:
        return None
    return best[1], best[2]


def cone_distance(scan, x):
    """カメラで見たコーンの向きの、±5° の中でいちばん近い物までの距離（7-3）"""
    a = round(x * HALF_FOV)
    _, d = rc_utils.get_lidar_closest_point(scan, ((a - 5) % 360, (a + 5) % 360))
    return d


def start():
    global state, last_side
    state = State.RETURN
    last_side = -1.0
    rc.drive.stop()
    print(">> スラロームをはじめます")


def update():
    global state, last_side, aim
    cone = nearest_cone()

    if state == State.APPROACH:
        if cone is None:                           # コーンの横をぬけた
            state = State.RETURN
            print("RETURN へ（コーンが見えなくなった）")
    elif state == State.RETURN:
        if cone is not None:
            state = State.APPROACH
            print(f"APPROACH へ（{'青' if cone[0] == 'blue' else 'もう1色'}のコーンが見えた）")

    if state == State.APPROACH:
        color, x = cone
        d = cone_distance(rc.lidar.get_samples(), x)
        side = -1.0 if color == "blue" else 1.0     # 青は左側（-1）、もう1色は右側（+1）を通る
        last_side = side
        aim = x * HALF_FOV + side * math.degrees(math.atan2(PASS, d))
        angle = rc_utils.clamp(aim / FULL_TURN, -1.0, 1.0)
    else:
        angle = -last_side * RETURN_TURN             # 通った側と反対へ切って、コーンの列にもどる
    rc.drive.set_speed_angle(SPEED, angle)


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
