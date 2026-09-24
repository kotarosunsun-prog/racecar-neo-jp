"""
comp_demo.py
作ったデータで、相補フィルタのはたらきを確かめる（実機・シミュレータは使わない）。
本当の傾きは 0° → 10° → 0° と変わる。加速度から求めた傾きはばらつきが大きく、
車が加速している間はうそのずれが出る。ジャイロには、少しずつずれていくくせ（バイアス）がある。
"""

import numpy as np

DT = 1 / 60          # 1コマの時間（秒）
ALPHA = 0.98         # ジャイロをどれだけ信じるか（0〜1）

rng = np.random.default_rng(0)
t = np.arange(0, 12, DT)                                   # 0〜12秒
true = np.interp(t, [0, 2, 3, 7, 8, 12], [0, 0, 10, 10, 0, 0])   # 本当の傾き（度）
rate = np.gradient(true, DT)                               # 本当の、傾きが変わる速さ（度/秒）

gyro = rate + 0.8 + rng.normal(0, 0.5, len(t))             # ジャイロ：バイアス 0.8 度/秒 ＋ ばらつき
acc = true + rng.normal(0, 2.0, len(t))                    # 加速度から求めた傾き：ばらつき 2 度
acc[(t > 4) & (t < 5)] += 6                                # 4〜5秒は加速中で、うそのずれが出る


def complementary(angle, gyro_rate, acc_angle, dt, alpha):
    """1コマ分の相補フィルタ：ジャイロで進めて、加速度で少しだけ引き戻す"""
    return alpha * (angle + gyro_rate * dt) + (1 - alpha) * acc_angle


gyro_only = np.zeros(len(t))
fused = np.zeros(len(t))
for k in range(1, len(t)):
    gyro_only[k] = gyro_only[k - 1] + gyro[k] * DT                         # ジャイロだけ（足し合わせる）
    fused[k] = complementary(fused[k - 1], gyro[k], acc[k], DT, ALPHA)     # 相補フィルタ


def rms(x):
    return np.sqrt(np.mean((x - true) ** 2))   # 本当の傾きとのずれの大きさ（二乗平均の平方根）


print(f"加速度だけ　のずれ：{rms(acc):.2f} 度")
print(f"ジャイロだけのずれ：{rms(gyro_only):.2f} 度（12秒後には {gyro_only[-1] - true[-1]:.1f} 度ずれている）")
print(f"相補フィルタのずれ：{rms(fused):.2f} 度")
