"""
detect_stop.py（実機用）
壁に沿って走り（WallSteer、7-13）、Edge TPU が「stop sign」（止まれの標識）を見つけたら、3 秒止まってから、また走る（9-5）。
  DRIVE：壁に沿って走る。近くの標識を CONFIRM_TIME 秒続けて見たら STOP へ
  STOP ：止まる。STOP_TIME 秒たったら PASS へ
  PASS ：標識を気にせずに走る。PASS_TIME 秒たったら DRIVE へ（同じ標識で、もう一度止まらないように）
wall_steer.py・walls.py・pid.py を同じフォルダに置いて使う。RB を押している間だけ、プログラムの命令が車に届く。
"""

import sys
from enum import IntEnum

sys.path.insert(1, "../../library")
import racecar_core
from wall_steer import WallSteer

rc = racecar_core.create_racecar()

TARGET = "stop sign"   # はじめから入っているモデル（COCO）の名前
MIN_SCORE = 0.5        # これより自信が低い答えは使わない
NEAR_HEIGHT = 60       # 枠の高さがこれより大きい（近い）標識だけを相手にする（画素）
CONFIRM_TIME = 0.2     # この時間（秒）続けて見えたら、本当にあると考える
LOST_TIME = 0.3        # この時間（秒）続けて見えなかったら、見えていた時間を 0 にもどす
STOP_TIME = 3.0        # 止まる時間（秒）
PASS_TIME = 3.0        # 止まったあと、標識を気にしない時間（秒）
SPEED = 0.4


class State(IntEnum):
    DRIVE = 0
    STOP = 1
    PASS = 2


state = State.DRIVE
timer = 0.0            # 今の状態になってからの時間（秒）
seen_time = 0.0        # 標識が続けて見えている時間（秒）
lost_time = 0.0        # 標識が続けて見えていない時間（秒）
wall = WallSteer()


def near_sign():
    """近くの TARGET のうち、いちばん自信の高い検出結果を返す。なければ None"""
    best = None
    for det in rc.vision.get_detections():
        if det.class_id == TARGET and det.score >= MIN_SCORE and det.bbox[3] >= NEAR_HEIGHT:
            if best is None or det.score > best.score:
                best = det
    return best


def set_state(new_state):
    global state, timer
    print(f"{new_state.name} へ")
    state = new_state
    timer = 0.0


def start():
    rc.drive.set_max_speed(0.25)      # はじめは上限を小さくしておく（9-1）
    rc.drive.stop()
    set_state(State.DRIVE)
    print(">> 壁に沿って走り、止まれの標識で 3 秒止まります（RB を押している間）")


def update():
    global timer, seen_time, lost_time
    dt = rc.get_delta_time()
    timer += dt
    scan = rc.lidar.get_samples()
    angle = wall.angle(scan, dt)

    # 標識が「続けて」見えている時間を数える（見えたり見えなかったりしても、LOST_TIME までは数え続ける）
    if near_sign() is not None:
        seen_time += dt
        lost_time = 0.0
    else:
        lost_time += dt
        if lost_time > LOST_TIME:
            seen_time = 0.0

    speed = SPEED
    if state == State.DRIVE:
        if seen_time >= CONFIRM_TIME:
            set_state(State.STOP)
    elif state == State.STOP:
        speed = 0.0
        if timer >= STOP_TIME:
            set_state(State.PASS)
    elif state == State.PASS:
        if timer >= PASS_TIME:
            set_state(State.DRIVE)

    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    sign = near_sign()
    print(f"  {state.name}　見えている時間 {seen_time:.2f} 秒　" + ("標識なし" if sign is None else str(sign)))


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
