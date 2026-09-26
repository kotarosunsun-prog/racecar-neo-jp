"""
grand_prix.py
グランプリ（8-1）。線・壁・障害物・AR マーカーの区間を、ステートマシンで切りかえて走り、ゴールで止まる。
  LINE  ：床の線を PID でたどる（6-21）。線が LOST_TIME 秒続けて見えなければ WALL へ
  WALL  ：壁沿い走行（6-18）。前の帯の物が NEAR より近くなったら GAP へ（7-13）
  GAP   ：Gap Follower（7-10）。前の帯の物が FAR より遠くなったら WALL へ（7-13）
  MARKER：AR マーカーのほうを向いて近づく（6-3）。十分近づいたら、番号で TURN か FINISH へ
  TURN  ：決まった時間、決まった向きにハンドルを切る。終わったら WALL へ
  FINISH：止まる（もう動かない）
LINE・WALL・GAP のときに、知っている番号のマーカーが SEEN_HEIGHT より大きく写ったら MARKER へ。
WALL・GAP のときに、線が LINE_AREA より大きく見えたら LINE へ。
line_steer.py・wall_steer.py・gap_steer.py・walls.py・pid.py・gaps.py を同じフォルダに置いて使う。
"""

import sys
from enum import IntEnum

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from line_steer import LineSteer
from wall_steer import WallSteer
from gap_steer import gap_angle

rc = racecar_core.create_racecar()

# 状態ごとの速さ（8-2 で調整する）
LINE_SPEED = 0.5
WALL_SPEED = 0.5
GAP_SPEED = 0.5
MARKER_SPEED = 0.4
TURN_SPEED = 0.4

LOST_TIME = 0.5        # 線がこの時間（秒）続けて見えなければ、線の区間は終わり
LINE_AREA = 300        # WALL・GAP のとき、線のかたまりがこの面積（画素）より大きければ LINE へ
HALF_WIDTH = 20.0      # 前の帯の幅の半分（cm）（7-1）
NEAR = 150.0           # 前の帯の物がこれより近くなったら GAP へ（cm）（7-13）
FAR = 250.0            # 前の帯の物がこれより遠くなったら WALL へ（cm）（7-13）

# AR マーカーの番号の意味（この本のコースのきまり。実際のコースに合わせて変える）
TURN_ANGLE = {0: -1.0, 1: 1.0}   # 0：左へ曲がる、1：右へ曲がる（6-3）
FINISH_ID = 3                     # 3：ゴール。近づいたら止まる
SEEN_HEIGHT = 25       # マーカーがこの高さ（画素）より大きく写ったら、MARKER へ
NEAR_HEIGHT = 60       # マーカーがこの高さ（画素）より大きく写ったら、曲がる（または止まる）
KP_MARKER = 0.8        # マーカーのほうを向くための比例ゲイン（6-3）
TURN_TIME = 1.6        # 曲がり続ける時間（秒）


def lidar_angles(scan):
    """LIDAR の各点の角度（ラジアン）。0 が正面、時計回り。
    点の数は len(scan) から求める（720 点なら 0.5° ずつ）"""
    return np.radians(np.arange(len(scan)) * 360 / len(scan))


class State(IntEnum):
    LINE = 0
    WALL = 1
    GAP = 2
    MARKER = 3
    TURN = 4
    FINISH = 5


line = LineSteer()
wall = WallSteer()
state = State.LINE
lost = 0.0             # 線が見えなくなってからの時間（秒）
turn_left = 0.0        # TURN の残り時間（秒）
turn = 0.0             # TURN で切るハンドルの向き
ahead = 0.0
elapsed = 0.0          # スタートからの時間（秒）。区間ごとの時間を測るのに使う（8-2）


def distance_ahead(scan):
    """車の前の、幅 2 × HALF_WIDTH の帯の中で、いちばん近い物までの前向きの距離（7-1）"""
    angles = lidar_angles(scan)
    forward = scan * np.cos(angles)
    side = scan * np.sin(angles)
    inside = (scan > 0) & (forward > 0) & (np.abs(side) < HALF_WIDTH)
    if not inside.any():
        return 10000.0
    return float(forward[inside].min())


def find_marker(image):
    """知っている番号のマーカーのうち、いちばん大きく写っているものの (番号, 中心の列, 高さ) を返す（6-3）"""
    if image is None:
        return None
    best = None
    for marker in rc_utils.get_ar_markers(image):
        if marker.get_id() not in TURN_ANGLE and marker.get_id() != FINISH_ID:
            continue
        corners = marker.get_corners()
        height = corners[:, 0].max() - corners[:, 0].min()
        if best is None or height > best[2]:
            best = (marker.get_id(), corners[:, 1].mean(), height)
    return best


def change(new_state, why):
    """状態を切りかえて、入るときの処理をする（7-2）"""
    global state, lost
    state = new_state
    if new_state == State.LINE:
        line.reset()
        lost = 0.0
    if new_state == State.WALL:
        wall.reset()
    print(f"{new_state.name} へ（{why}）　{elapsed:.1f} 秒")


def start():
    global state, elapsed
    state = State.LINE
    elapsed = 0.0
    line.reset()
    wall.reset()
    rc.drive.stop()
    print(">> グランプリ：スタート")


def update():
    global lost, turn_left, turn, ahead, elapsed
    dt = rc.get_delta_time()
    elapsed += dt
    image = rc.camera.get_color_image()
    scan = rc.lidar.get_samples()
    ahead = distance_ahead(scan)
    marker = find_marker(image)

    # ---- 1. 状態を切りかえる ----
    if state in (State.LINE, State.WALL, State.GAP) and marker is not None and marker[2] > SEEN_HEIGHT:
        change(State.MARKER, f"マーカー {marker[0]} が見えた")
    elif state == State.LINE:
        if line.find_line(image) is None:
            lost += dt
            if lost > LOST_TIME:
                change(State.WALL, "線が見えなくなった")
        else:
            lost = 0.0
    elif state in (State.WALL, State.GAP):
        found = line.find_line(image)
        if found is not None and found[1] > LINE_AREA:
            change(State.LINE, "線が見えた")
        elif state == State.WALL and ahead < NEAR:
            change(State.GAP, f"前の物まで {ahead:.0f} cm")
        elif state == State.GAP and ahead > FAR:
            change(State.WALL, "前の帯に物がない" if ahead >= 10000 else f"前の物まで {ahead:.0f} cm")
    elif state == State.MARKER:
        if marker is None:
            change(State.WALL, "マーカーを見失った")
        elif marker[2] > NEAR_HEIGHT:
            if marker[0] == FINISH_ID:
                change(State.FINISH, "ゴールのマーカー")
            else:
                turn = TURN_ANGLE[marker[0]]
                turn_left = TURN_TIME
                change(State.TURN, f"マーカー {marker[0]} → {'右' if turn > 0 else '左'}へ曲がる")
    elif state == State.TURN:
        turn_left -= dt
        if turn_left <= 0:
            change(State.WALL, "曲がり終えた")

    # ---- 2. 今の状態で、速さとハンドルを決める ----
    wall_angle = wall.angle(scan, dt)          # 壁沿い走行の角度は、いつも計算しておく（7-13）
    speed, angle = 0.0, 0.0
    if state == State.LINE:
        a = line.angle(image, dt)
        speed, angle = LINE_SPEED, (line.last_angle if a is None else a)
    elif state == State.WALL:
        speed, angle = WALL_SPEED, wall_angle
    elif state == State.GAP:
        g = gap_angle(scan)
        speed, angle = GAP_SPEED, (wall_angle if g is None else g)
    elif state == State.MARKER:
        error = (marker[1] - 320) / 320
        speed, angle = MARKER_SPEED, rc_utils.clamp(KP_MARKER * error, -1.0, 1.0)
    elif state == State.TURN:
        speed, angle = TURN_SPEED, turn
    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    print(f"  {state.name}　前の物まで {min(ahead, 9999):.0f} cm")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
