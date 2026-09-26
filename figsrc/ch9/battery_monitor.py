"""
battery_monitor.py
右トリガーで前へ、左スティックでハンドル（手動運転）。そのあいだ、バッテリーの電圧を見はる（9-2）。
「注意」になったら速さの上限を半分に、「止まる」になったら前へ進まないようにする。
battery_guard.py を同じフォルダに置いて使う。実機専用（シミュレータでは電圧が 0.0 で、見はらない）。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
from battery_guard import BatteryGuard, CELLS, WARN, STOP

rc = racecar_core.create_racecar()

MAX_SPEED = 0.5        # トリガーをいっぱいに押したときの speed
guard = BatteryGuard()
state = ""
volts = []             # 1 秒の間の電圧の記録（平均と最小を表示する）


def start():
    rc.drive.set_max_speed(0.25)
    rc.drive.stop()
    print(">> 手動運転しながら、バッテリーの電圧を見はります")


def update():
    global state
    voltage = rc.physics.get_battery_voltage()
    volts.append(voltage)
    new_state = guard.update(voltage, rc.get_delta_time())
    if new_state != state:
        print(f"バッテリー：{new_state}（{voltage:.2f} V）")
        state = new_state

    speed = rc.controller.get_trigger(rc.controller.Trigger.RIGHT) * MAX_SPEED
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]
    if state == WARN:
        speed *= 0.5                   # 注意：ゆっくり走って、もどってくる
    if state == STOP:
        speed = 0.0                    # 止まる：もう前へ進まない
    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    if len(volts) > 0 and max(volts) > 0:
        average = sum(volts) / len(volts)
        print(f"  電圧 平均 {average:.2f} V（1 セル {average / CELLS:.2f} V）　いちばん低い {min(volts):.2f} V　"
              f"電流 {rc.physics.get_battery_current():.1f} A　{state}")
    volts.clear()


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
