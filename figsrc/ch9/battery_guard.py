"""
battery_guard.py
バッテリーの電圧を見はって、「注意」「止まる」を決めるクラス（9-2）。
使い方：
    from battery_guard import BatteryGuard
    guard = BatteryGuard()
    state = guard.update(rc.physics.get_battery_voltage(), rc.get_delta_time())
"""

CELLS = 2              # 直列につないだセルの数（2S のバッテリーなら 2。自分のバッテリーのラベルで確かめる）
WARN_PER_CELL = 3.6    # 1 セルあたりこれより低いと「注意」（V）
STOP_PER_CELL = 3.4    # 1 セルあたりこれより低いと「止まる」（V）。多くの低電圧カット（3.2 V）より余裕をもたせる
HOLD_TIME = 2.0        # この時間（秒）続けて低いときだけ、低いと判断する（加速したときの一瞬の電圧の落ちこみを無視する）

OK, WARN, STOP, NO_SENSOR = "OK", "注意", "止まる", "センサなし"


class BatteryGuard:
    def __init__(self):
        self.state = OK
        self.low_time = {WARN: 0.0, STOP: 0.0}     # それぞれのしきい値より低い時間が、続いている長さ（秒）

    def update(self, voltage, dt):
        """今の電圧（V）と 1 コマの時間（秒）から、状態を返す。一度「止まる」になったら、もどらない"""
        if voltage <= 0.0:                         # シミュレータは 0.0 を返す（電圧のセンサがない）
            return NO_SENSOR
        per_cell = voltage / CELLS
        for level, limit in ((WARN, WARN_PER_CELL), (STOP, STOP_PER_CELL)):
            if per_cell < limit:
                self.low_time[level] += dt
            else:
                self.low_time[level] = 0.0
        if self.low_time[STOP] >= HOLD_TIME:
            self.state = STOP
        elif self.state != STOP and self.low_time[WARN] >= HOLD_TIME:
            self.state = WARN
        return self.state
