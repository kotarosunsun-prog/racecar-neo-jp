"""
wall_only.py
WallSteer だけで走る（7-13 の比べる用。6-18 の wall_follow_course.py と同じ走り）。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
from wall_steer import WallSteer

rc = racecar_core.create_racecar()
SPEED = 0.5
wall = WallSteer()


def start():
    wall.reset()
    rc.drive.stop()


def update():
    rc.drive.set_speed_angle(SPEED, wall.angle(rc.lidar.get_samples(), rc.get_delta_time()))


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
