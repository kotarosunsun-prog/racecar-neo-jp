"""
learn_threshold.py
色合い H の値から「緑の箱か、青の箱か」を見分けるしきい値を、データから選ぶ。
"""

import numpy as np

# 作ったデータ：いろいろな明るさ・向きで測った H の値（0 = 緑、1 = 青 が正解）
rng = np.random.default_rng(4)
h_green = rng.normal(72, 9, 60)      # 緑の箱の H
h_blue = rng.normal(100, 9, 60)      # 青の箱の H
h = np.concatenate([h_green, h_blue])
label = np.concatenate([np.zeros(60), np.ones(60)])

# 学習用とテスト用に分ける（まぜてから、4分の3を学習用に）
order = rng.permutation(len(h))
train, test = order[:90], order[90:]


def accuracy(threshold, idx):
    """しきい値より大きければ「青」と答えたときの正解率"""
    guess = (h[idx] > threshold).astype(float)
    return np.mean(guess == label[idx])


# 学習：0〜179 のしきい値をすべて試し、学習用データでいちばん正解率が高いものを選ぶ
best = max(range(180), key=lambda t: accuracy(t, train))

print(f"選んだしきい値：H > {best} なら青")
print(f"学習用データの正解率：{accuracy(best, train):.1%}")
print(f"テスト用データの正解率：{accuracy(best, test):.1%}")
