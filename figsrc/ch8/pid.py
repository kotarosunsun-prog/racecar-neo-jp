"""
pid.py
PID 制御をまとめたクラス（6-12）。
使い方：
    from pid import PID
    pid = PID(kp=0.02, ki=0.005, kd=0.03)
    angle = pid.update(error, rc.get_delta_time())
"""


class PID:
    def __init__(self, kp, ki, kd, out_min=-1.0, out_max=1.0,
                 i_limit=None, i_zone=None, rate_frames=10):
        self.kp = kp                      # P のゲイン
        self.ki = ki                      # I のゲイン
        self.kd = kd                      # D のゲイン
        self.out_min = out_min            # 命令の下限
        self.out_max = out_max            # 命令の上限
        self.i_limit = i_limit            # 積分の大きさの上限（None なら上限なし）
        self.i_zone = i_zone              # ずれがこれより小さいときだけ、ためる（None ならいつでも）
        self.rate_frames = rate_frames    # 何コマ前のずれと比べて、速さを求めるか（6-9）
        self.reset()

    def reset(self):
        """ためた積分と、ずれの記録を消す（走り出すときや、切りかえるときに呼ぶ）"""
        self.integral = 0.0
        self.history = []                 # 最近の (時刻, ずれ)
        self.time = 0.0

    def update(self, error, dt, rate=None):
        """ずれ error と、1コマの時間 dt（秒）から、命令を返す。
        rate を渡すと、D の部分には、ずれの変わる速さのかわりに、それを使う"""
        self.time += dt

        # D：ずれの変わる速さ（記録の、いちばん古いものと新しいものを比べる）
        self.history.append((self.time, error))
        if len(self.history) > self.rate_frames + 1:
            self.history.pop(0)
        if rate is None:
            rate = 0.0
            if len(self.history) >= 2:
                t0, e0 = self.history[0]
                t1, e1 = self.history[-1]
                rate = (e1 - e0) / (t1 - t0)

        # I：ずれをためる。ただし、次のときはためない（積分の暴走をふせぐ）
        #  ・ずれが i_zone より大きいとき
        #  ・命令がもう上限（下限）をこえていて、さらに同じ向きにためようとするとき
        in_zone = self.i_zone is None or abs(error) < self.i_zone
        trial = self.kp * error + self.ki * (self.integral + error * dt) + self.kd * rate
        too_high = trial > self.out_max and self.ki * error > 0
        too_low = trial < self.out_min and self.ki * error < 0
        if in_zone and not (too_high or too_low):
            self.integral += error * dt
        if self.i_limit is not None:
            self.integral = max(-self.i_limit, min(self.i_limit, self.integral))

        # 3つを足して、上限・下限の中におさめる
        out = self.kp * error + self.ki * self.integral + self.kd * rate
        return max(self.out_min, min(self.out_max, out))
