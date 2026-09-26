"""
brake_test.py
決まった speed で壁に向かってまっすぐ走り、正面の壁が BRAKE_AT より近くなったら speed を 0 にする。
止まるまでに進んだ距離を表示する（7-1）。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

SPEED = 0.5            # 試す速さ
BRAKE_AT = 150.0       # 正面の壁がこれより近くなったら、ブレーキ（cm）

braking = False        # ブレーキをかけたあとか
front_at_brake = 0.0   # ブレーキをかけたときの、正面の壁までの距離
last_front = 0.0       # 0.5 秒前の、正面の壁までの距離（止まったかを調べる）
done = False           # 結果を表示したか


def front_distance(scan):
    """正面 ±5° の平均の距離（ばらつきを小さくするため、いちばん近い点ではなく平均を使う）"""
    return rc_utils.get_lidar_average_distance(scan, 0, 10)


def start():
    global braking, done
    braking = False
    done = False
    rc.drive.stop()
    rc.set_update_slow_time(0.5)
    print(f">> speed {SPEED} で走り、壁まで {BRAKE_AT:.0f} cm でブレーキをかけます")


def update():
    global braking, front_at_brake
    front = front_distance(rc.lidar.get_samples())
    if not braking and 0 < front < BRAKE_AT:
        braking = True
        front_at_brake = front
        print(f"ブレーキ！　正面の壁まで {front:.1f} cm")
    if braking:
        rc.drive.set_speed_angle(0.0, 0.0)
    else:
        rc.drive.set_speed_angle(SPEED, 0.0)


def update_slow():
    global last_front, done
    front = front_distance(rc.lidar.get_samples())
    if braking and not done and abs(front - last_front) < 1.0:
        print(f"止まった：正面の壁まで {front:.1f} cm　ブレーキから {front_at_brake - front:.1f} cm 進んだ")
        done = True
    last_front = front


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
