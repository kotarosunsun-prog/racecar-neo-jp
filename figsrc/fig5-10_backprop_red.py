"""
backprop_red.py
色合い H から「赤かどうか」を答えるニューラルネットワークを、誤差逆伝播と勾配降下法で学習させる。
かくれ層はシグモイド関数のニューロン 3 つ、出力もシグモイド関数、損失は平均二乗誤差。
"""

import numpy as np

rng = np.random.default_rng(0)

# 作ったデータ：H と、赤かどうかの正解（赤 = 1）。赤のデータを少し多めに入れておく
h = np.concatenate([rng.uniform(0, 180, 200), rng.uniform(0, 10, 50), rng.uniform(170, 180, 50)])
y = ((h < 10) | (h > 170)).astype(float)
x = (h - 90) / 90                      # 入力を -1〜1 くらいにそろえる

HIDDEN = 3                             # かくれ層のニューロンの数
LR = 5.0                               # 学習率

# パラメータ：はじめは、でたらめな小さい値
W1 = rng.normal(0, 1, HIDDEN)          # 入力 → かくれ層 の重み
b1 = rng.normal(0, 1, HIDDEN)          # かくれ層のバイアス
W2 = rng.normal(0, 1, HIDDEN)          # かくれ層 → 出力 の重み
b2 = 0.0                               # 出力のバイアス


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


for step in range(20001):
    # ---- 前向きの計算（順伝播）----
    z1 = np.outer(x, W1) + b1          # かくれ層の z（データの数 × 3）
    a1 = sigmoid(z1)                   # かくれ層の出力
    z2 = a1 @ W2 + b2                  # 出力の z
    a2 = sigmoid(z2)                   # 出力：赤である確からしさ（0〜1）
    loss = np.mean((a2 - y) ** 2)      # 損失（平均二乗誤差）

    # ---- 後ろ向きの計算（逆伝播）：出力に近いほうから、傾きを順にかけていく ----
    d_a2 = 2 * (a2 - y) / len(x)       # 損失の、a2 についての傾き
    d_z2 = d_a2 * a2 * (1 - a2)        # シグモイド関数の傾き a(1-a) をかける
    d_W2 = a1.T @ d_z2                 # W2 についての傾き
    d_b2 = d_z2.sum()                  # b2 についての傾き
    d_a1 = np.outer(d_z2, W2)          # かくれ層の出力 a1 についての傾き
    d_z1 = d_a1 * a1 * (1 - a1)        # シグモイド関数の傾きをかける
    d_W1 = (d_z1 * x[:, None]).sum(axis=0)   # W1 についての傾き
    d_b1 = d_z1.sum(axis=0)            # b1 についての傾き

    if step in (0, 1000, 5000, 20000):
        print(f"{step:5d} 回め：損失 {loss:.4f}")

    # ---- 勾配降下法（5-8）で、すべてのパラメータを動かす ----
    W1 -= LR * d_W1
    b1 -= LR * d_b1
    W2 -= LR * d_W2
    b2 -= LR * d_b2

# ---- 学習したネットワークを、0〜179 のすべての H で試す ----
h_test = np.arange(180)
a_test = sigmoid(sigmoid(np.outer((h_test - 90) / 90, W1) + b1) @ W2 + b2)
correct = (a_test > 0.5) == ((h_test < 10) | (h_test > 170))
print(f"0〜179 の H で試した正解率：{correct.mean():.1%}")
for hv in (0, 5, 12, 90, 168, 175):
    print(f"  H = {hv:3d} → 赤である確からしさ {a_test[hv]:.2f}")
