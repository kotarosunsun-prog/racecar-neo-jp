"""
line_steer.py
6-21 の line_follow_pid.py のハンドルを決める部分を、クラスにまとめたもの（8-1）。
pid.py を同じフォルダに置いて使う。
"""

import racecar_utils as rc_utils
from pid import PID

BLUE = ((90, 50, 50), (120, 255, 255))   # 線の色（Lab E・Lab F のひな形の青）
MIN_CONTOUR_AREA = 30                      # これより小さいかたまりは無視する
CROP_FLOOR = ((360, 0), (480, 640))        # 画像の下の部分（車のすぐ前の床）


class LineSteer:
    """床の線を見てハンドルの角度を決める。angle(image, dt) を毎コマ呼ぶ"""

    def __init__(self):
        self.pid = PID(kp=2.0, ki=1.0, kd=0.1)
        self.reset()

    def reset(self):
        self.pid.reset()
        self.last_angle = 0.0

    def find_line(self, image):
        """線のいちばん大きいかたまりの (中心の列, 面積) を返す。見えなければ None"""
        if image is None:
            return None
        image = rc_utils.crop(image, CROP_FLOOR[0], CROP_FLOOR[1])
        contours = rc_utils.find_contours(image, BLUE[0], BLUE[1])
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)
        if contour is None:
            return None
        return rc_utils.get_contour_center(contour)[1], rc_utils.get_contour_area(contour)

    def angle(self, image, dt):
        """線が見えれば、PID で決めた angle を返す。見えなければ None"""
        found = self.find_line(image)
        if found is None:
            return None
        error = (found[0] - 320) / 320               # 左はし -1 〜 右はし +1（6-2）
        self.last_angle = self.pid.update(error, dt)
        return self.last_angle
