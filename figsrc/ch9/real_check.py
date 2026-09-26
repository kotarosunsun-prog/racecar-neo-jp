"""
real_check.py
実機とシミュレータのちがいを、センサの値を表示して確かめる（9-1）。車は動かさない。
シミュレータ：racecar sim real_check.py　　実機：python3 real_check.py
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

frames = 0          # 1 秒の間に update() が呼ばれた回数
dt_max = 0.0        # 1 秒の間で、いちばん長かった 1 コマの時間（秒）


def start():
    rc.drive.set_max_speed(0.25)     # 実機では、はじめは上限を小さくしておく（9-1）
    rc.drive.stop()
    print(">> センサの値を 1 秒ごとに表示します（車は動かしません）")


def update():
    global frames, dt_max
    frames += 1
    dt_max = max(dt_max, rc.get_delta_time())
    rc.drive.stop()


def update_slow():
    global frames, dt_max
    scan = rc.lidar.get_samples()
    n = len(scan)
    front = rc_utils.get_lidar_average_distance(scan, 0)        # 正面（0° のまわりの平均）
    right = rc_utils.get_lidar_average_distance(scan, 90)
    zeros = int((scan == 0).sum())                               # 測れなかった点の数
    image = rc.camera.get_color_image()
    size = "なし" if image is None else f"{image.shape[1]}×{image.shape[0]}"
    print(f"LIDAR {n} 点（1 点 {360 / n:.2f}°、測れない点 {zeros}）　正面 {front:.0f} cm　右 {right:.0f} cm")
    if hasattr(rc, "vision"):                                   # シミュレータの rc には vision がない
        found = f"{len(rc.vision.get_detections())} 個"
    else:
        found = "（rc.vision なし）"
    print(f"  カメラ {size}　電圧 {rc.physics.get_battery_voltage():.2f} V　"
          f"車輪 {rc.physics.get_encoder_speed():.2f} m/秒　見つけた物 {found}")
    print(f"  update() {frames} 回/秒（いちばん長いコマ {dt_max * 1000:.0f} ミリ秒）")
    frames, dt_max = 0, 0.0


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
