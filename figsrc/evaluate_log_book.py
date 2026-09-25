"""
evaluate_log.py
wall_log.csv を読んで、反応のよさを数で表す（6-13）。
はじめの距離から TARGET へ近づいていく走り（ステップ応答）を調べる。
"""

import csv

TARGET = 50.0     # 目標の距離（cm）
BAND = 2.5        # この幅（± cm）の中に入り続けたら「落ち着いた」とみなす

times, dists, angles = [], [], []
with open("wall_log.csv") as f:
    for row in csv.DictReader(f):
        times.append(float(row["time"]))
        dists.append(float(row["distance"]))
        angles.append(float(row["angle"]))

step = dists[0] - TARGET                        # はじめのずれ
ratio = [(d - TARGET) / step for d in dists]    # はじめのずれを 1 としたときの、今のずれ

# 1. 立ち上がり時間：ずれが、はじめの 90% から 10% になるまでの時間
t90 = next(t for t, r in zip(times, ratio) if r <= 0.9)
t10 = next(t for t, r in zip(times, ratio) if r <= 0.1)
rise = t10 - t90

# 2. 行き過ぎ量：目標をこえて、反対側にいちばん行った量
overshoot = max(0.0, -min(ratio)) * abs(step)

# 3. 整定時間：最後に BAND の外にいた時刻（そのあとは、ずっと BAND の中）
outside = [t for t, d in zip(times, dists) if abs(d - TARGET) > BAND]
settle = outside[-1] if outside else 0.0

# 4. 残ったずれ：最後の 2 秒のずれの平均
last = [d - TARGET for t, d in zip(times, dists) if t > times[-1] - 2.0]
steady = sum(last) / len(last)

# 5. ハンドルの動き：1秒あたりに、angle がどれだけ動いたかの合計
moves = sum(abs(a1 - a0) for a0, a1 in zip(angles[:-1], angles[1:]))
activity = moves / (times[-1] - times[0])

print(f"はじめのずれ   {step:+6.1f} cm")
print(f"立ち上がり時間 {rise:6.2f} 秒")
print(f"行き過ぎ量     {overshoot:6.1f} cm（はじめのずれの {overshoot / abs(step) * 100:.0f}%）")
print(f"整定時間       {settle:6.2f} 秒（± {BAND} cm）")
print(f"残ったずれ     {steady:+6.2f} cm")
print(f"ハンドルの動き {activity:6.2f}（1秒あたり）")
