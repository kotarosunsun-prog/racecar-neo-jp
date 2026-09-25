"""
train_drive.py
drive_log.csv（record_drive.py の記録）から、「見え方 → ハンドルの角度」を答える
ニューラルネットワークを学習させ、重みを drive_net.npz に保存する（6-23）。
かくれ層は tanh のニューロン 16 個、出力は1つ（そのままの値）、損失は平均二乗誤差。
"""

import numpy as np

rng = np.random.default_rng(0)

data = np.loadtxt("drive_log.csv", delimiter=",")
x = data[:, :-1]                  # 見え方（特徴9つ）
y = data[:, -1]                   # そのとき人が決めたハンドルの角度

# 特徴ごとに、平均 0、ばらつき 1 になるようにそろえる（走るときも、同じ平均とばらつきを使う）
x_mean = x.mean(axis=0)
x_std = x.std(axis=0) + 1e-6
x = (x - x_mean) / x_std

# 5コマに1コマを、学習に使わない「確かめ用」にする
test = np.arange(len(x)) % 5 == 0
x_train, y_train = x[~test], y[~test]
x_test, y_test = x[test], y[test]

HIDDEN = 16                       # かくれ層のニューロンの数
LR = 0.1                          # 学習率

W1 = rng.normal(0, 0.5, (x.shape[1], HIDDEN))   # 入力 → かくれ層 の重み
b1 = np.zeros(HIDDEN)                           # かくれ層のバイアス
W2 = rng.normal(0, 0.5, HIDDEN)                 # かくれ層 → 出力 の重み
b2 = 0.0                                        # 出力のバイアス


def predict(x):
    return np.tanh(x @ W1 + b1) @ W2 + b2


for step in range(5001):
    # ---- 前向きの計算 ----
    a1 = np.tanh(x_train @ W1 + b1)       # かくれ層の出力
    out = a1 @ W2 + b2                    # 出力：ハンドルの角度の予想
    loss = np.mean((out - y_train) ** 2)

    # ---- 後ろ向きの計算（5-10）----
    d_out = 2 * (out - y_train) / len(y_train)
    d_W2 = a1.T @ d_out
    d_b2 = d_out.sum()
    d_a1 = np.outer(d_out, W2)
    d_z1 = d_a1 * (1 - a1 ** 2)           # tanh の傾きは 1 - a^2
    d_W1 = x_train.T @ d_z1
    d_b1 = d_z1.sum(axis=0)

    if step in (0, 100, 1000, 5000):
        test_loss = np.mean((predict(x_test) - y_test) ** 2)
        print(f"{step:4d} 回め：学習用の損失 {loss:.4f}　確かめ用の損失 {test_loss:.4f}")

    W1 -= LR * d_W1
    b1 -= LR * d_b1
    W2 -= LR * d_W2
    b2 -= LR * d_b2

np.savez("drive_net.npz", W1=W1, b1=b1, W2=W2, b2=b2, x_mean=x_mean, x_std=x_std)
print(f"{len(x_train)} コマで学習し、drive_net.npz に保存しました")
