"""
speed_log.py（実機用）
A ボタンを押すと、まっすぐ RUN_TIME 秒だけ走って止まる（9-4）。
走っているあいだ、speed の命令・車輪で測った速さ・バッテリーの電圧を、rc.telemetry で記録する。
記録は labs/logs フォルダに、CSV（表）と PNG（グラフ）で保存される。
Y ボタンで speed を 0.1 上げ、X ボタンで 0.1 下げる。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core

rc = racecar_core.create_racecar()

RUN_TIME = 2.0         # 1 回に走る時間（秒）
speed = 0.3            # 走るときの speed
running = False
timer = 0.0
fastest = 0.0          # 1 回の走りで、いちばん速かった速さ（m/秒）


def start():
    rc.drive.set_max_speed(0.25)
    rc.drive.stop()
    rc.telemetry.declare_variables("speed", "encoder_m_s", "voltage")
    print(f">> A ボタンで {RUN_TIME} 秒まっすぐ走ります。Y・X ボタンで speed を変えます（今 {speed:.1f}）")


def update():
    global speed, running, timer, fastest
    if not running:
        if rc.controller.was_pressed(rc.controller.Button.A):
            running, timer, fastest = True, 0.0, 0.0
            print(f"speed {speed:.1f} で走ります")
        if rc.controller.was_pressed(rc.controller.Button.Y):
            speed = min(speed + 0.1, 1.0)
            print(f"speed {speed:.1f}")
        if rc.controller.was_pressed(rc.controller.Button.X):
            speed = max(speed - 0.1, 0.1)
            print(f"speed {speed:.1f}")
        rc.drive.stop()
        return

    timer += rc.get_delta_time()
    measured = rc.physics.get_encoder_speed()
    fastest = max(fastest, measured)
    rc.telemetry.record(speed, measured, rc.physics.get_battery_voltage())
    rc.drive.set_speed_angle(speed, 0.0)
    if timer >= RUN_TIME:
        running = False
        rc.drive.stop()
        rc.telemetry.visualize()               # 実機では、自分で呼ばないとグラフが保存されない
        print(f"止まりました。いちばん速かったのは {fastest:.2f} m/秒")


def update_slow():
    pass


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
