"""
auto_tune.py
壁沿い走行のゲイン（KP と、壁の向きのゲイン KA）を、勾配降下法で自動で探す（6-22）。
車と壁は、この中に書いた簡単なモデルで計算する（シミュレータは使わない）。
"""

import math

# ---- 車と壁のモデル（説明用の簡単なモデル）----
DT = 1 / 60          # 1コマの時間（秒）
V = 75.0             # 車の速さ（cm/秒）。speed 0.5 くらい
WHEELBASE = 30.0     # 前輪と後輪の間の長さ（cm）
MAX_STEER = math.radians(20)   # angle = 1 のときのタイヤの角度
STEER_LAG = 0.08     # タイヤが命令の角度に近づくまでの時間（秒）
MEASURE_EVERY = 6    # LIDAR の値が変わるのは、6コマ（0.1 秒）に1回
TARGET = 50.0        # 右の壁から保ちたい距離（cm）
START = 100.0        # はじめの距離（cm）
SECONDS = 8.0        # 走らせる時間（秒）
EFFORT = 20.0        # ハンドルを大きく切ることへの「罰」の重さ


def run(kp, ka):
    """ゲイン (kp, ka) で走らせて、(損失, 距離の記録) を返す"""
    d, alpha, steer = START, 0.0, 0.0     # 壁までの距離、壁の向き（ラジアン）、タイヤの角度
    seen_d, seen_alpha = d, alpha         # LIDAR で測った値（ときどきしか変わらない）
    total = 0.0
    history = []
    frames = int(SECONDS / DT)
    for f in range(frames):
        if f % MEASURE_EVERY == 0:
            seen_d, seen_alpha = d, alpha
        angle = kp * (seen_d - TARGET) + ka * math.degrees(seen_alpha)
        angle = max(-1.0, min(1.0, angle))
        # 車を1コマ動かす
        steer += (angle * MAX_STEER - steer) / STEER_LAG * DT
        alpha -= V / WHEELBASE * math.tan(steer) * DT
        d += V * math.sin(alpha) * DT
        # 損失：ずれの2乗 ＋ ハンドルの切りすぎの罰
        total += ((d - TARGET) / 10) ** 2 + EFFORT * angle ** 2
        history.append(d)
        if d < 12:                        # 壁にぶつかった
            return total / frames + 1000.0, history
    return total / frames, history


def loss(kp, ka):
    return run(kp, ka)[0]


# ---- 勾配降下法（5-8）----
LR = 0.00002         # 学習率
H = 0.0001           # 傾きを求めるために、少しだけ動かす量
kp, ka = 0.01, 0.01  # はじめの値（小さめ）

for step in range(301):
    L = loss(kp, ka)
    # 少しだけ動かして、傾きを求める（両側に動かして、差をとる）
    grad_kp = (loss(kp + H, ka) - loss(kp - H, ka)) / (2 * H)
    grad_ka = (loss(kp, ka + H) - loss(kp, ka - H)) / (2 * H)
    if step in (0, 1, 2, 5, 10, 20, 50, 100, 200, 300):
        print(f"{step:3d} 回め：KP = {kp:.4f}, KA = {ka:.4f}, 損失 = {L:.3f}")
    kp = kp - LR * grad_kp           # 傾きと反対向きに、少し動かす
    ka = ka - LR * grad_ka
