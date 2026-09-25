---
title: "6-16 両側の壁の真ん中を走る"
free: true
---

Lab I の Expected Outcome には、「両側に壁が見えるときは、2つの壁の真ん中を走る」とありました（6-4）。この回では、右の壁だけでなく左の壁も測り、**通路の真ん中**を走るプログラムを作ります。真ん中を走ると、通路の幅が変わっても、目標の距離を決め直す必要がありません。あわせて、壁を測る関数を、別のファイル `walls.py` にまとめます。

## ① この回でできるようになること

1. 左の壁の向きと距離を、右の壁と同じ方法で求められる
2. 左右の距離から、通路の真ん中からのずれを求められる
3. 左右の壁の向きから、通路に対する車の向きを求められる
4. 壁を測る関数を別のファイルにまとめて、いくつものプログラムで使える

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Centerline | 通路の真ん中の線 | 左右の壁から同じ距離にある線 |
| Lateral offset | 横のずれ | 真ん中の線から、左右にどれだけずれているか |
| Module | モジュール | 関数などをまとめた、別の .py ファイル。`import` で読みこんで使う |
| Symmetry | 対称 | 左右をひっくり返しても同じ形になること |

## ③ 本文

### 右の壁だけにそって走ると、何が困るか

右の壁から 50 cm の所を走るやり方は、通路の幅によって、うまくいったり、いかなかったりします。

- 幅 100 cm の通路なら、右から 50 cm は、ちょうど真ん中
- 幅 250 cm の通路なら、右の壁によった所を走ることになる
- 幅 80 cm の通路なら、右から 50 cm の所は、左の壁から 30 cm しかない

さらに、通路の幅が急に広がって、右の壁が遠くへ離れると、右の壁を見失います。説明用の簡単なモデルで、幅が 150 → 100 → 250 → 150 cm と変わる通路を、右の壁から 50 cm で走らせると、幅が 250 cm に広がる所で右へ曲がりこみ、壁にぶつかりました（図1の灰色）。

### 左の壁も、同じように測る

左の壁も、右の壁と同じ2本の光線の方法（6-10）で測れます。左は 270°、左ななめ前は 30° 前の 300° です。右と左は**対称**なので、式はまったく同じです。壁の向きも、右と同じく「＋なら、その壁から離れる向きに走っている」になります。

そこで、左右どちらの壁も測れる関数 `side_wall(scan, side)` を作り、正面の距離を求める関数といっしょに、`walls.py` という別のファイルにまとめます。

```python:walls.py
"""
walls.py
LIDAR で、左右の壁の向きと距離、正面の距離を求める関数（6-16）。
使い方：
    from walls import side_wall, front_distance
"""

import math
import racecar_utils as rc_utils

THETA = 30        # 2本の光線の間の角度（度）
MAX_WALL = 300.0  # これより遠い壁は「見えない」とみなす（cm）
MAX_ANGLE = 45    # 壁の向きがこれより大きいときは、2本の光線が同じ壁に当たっていないとみなす（度）


def side_wall(scan, side):
    """side が "right" なら右の壁、"left" なら左の壁の、(向き〔度〕, 距離〔cm〕) を返す。
    向きが＋なら、その壁から離れる向きに走っている。見えなければ (None, None)"""
    if side == "right":
        a = rc_utils.get_lidar_average_distance(scan, 90 - THETA)    # 右ななめ前（60°）
        b = rc_utils.get_lidar_average_distance(scan, 90)            # 右（90°）
    else:
        a = rc_utils.get_lidar_average_distance(scan, 270 + THETA)   # 左ななめ前（300°）
        b = rc_utils.get_lidar_average_distance(scan, 270)           # 左（270°）
    if a == 0.0 or b == 0.0 or b > MAX_WALL:
        return None, None
    t = math.radians(THETA)
    alpha = math.atan2(a * math.cos(t) - b, a * math.sin(t))
    if abs(math.degrees(alpha)) > MAX_ANGLE:         # 壁がとぎれている（入り口や曲がり角）
        return None, None
    return math.degrees(alpha), b * math.cos(alpha)


def front_distance(scan, half_width=10):
    """正面（±half_width 度）で、いちばん近い物までの距離（cm）"""
    _, distance = rc_utils.get_lidar_closest_point(scan, (360 - half_width, half_width))
    return distance
```

- `b > MAX_WALL`：真横の壁が 300 cm より遠いときは、「見えない」とします。6-6 の `right_wall_distance()` と同じ考え方です
- `abs(...) > MAX_ANGLE`：壁の向きが 45° より大きいときも、「見えない」とします。入り口や曲がり角で壁がとぎれると、ななめ前の光線だけが、とぎれた先の遠くの物に当たり、壁がとても大きくななめになっているように計算されてしまうからです（6-17）
- `front_distance()`：6-15 で使った、正面 ±10° でいちばん近い物までの距離です

### 真ん中からのずれと、通路に対する向き

右の壁までを $d_R$、左の壁までを $d_L$ とします。真ん中にいれば $d_R = d_L$ です。真ん中から左に $x$ cm ずれると、右は $x$ 増え、左は $x$ 減るので、

$$
\text{ずれ} = \frac{d_R - d_L}{2}
$$

で、真ん中からのずれ（＋なら左に寄っている）が求まります。ずれが＋なら、右へハンドルを切ればよいので、右の壁のときと同じ符号です。

向きも同じように考えます。右の壁の向き $\alpha_R$ は「＋なら右の壁から離れる（左へ向かう）」、左の壁の向き $\alpha_L$ は「＋なら左の壁から離れる（右へ向かう）」でした。そこで、

$$
\text{向き} = \frac{\alpha_R - \alpha_L}{2}
$$

とすると、「＋なら左へ向かっている」という、通路に対する車の向きになります。2つの壁の向きを平均しているので、片方だけのときより、ばらつきも小さくなります。

### やってみよう：通路の真ん中を走る

`walls.py` と `pid.py`（6-12）を同じフォルダに置いて、次のプログラムを作ります。

```python:wall_follow_center.py
"""
wall_follow_center.py
左右の壁の真ん中を走る（6-16）。walls.py と pid.py を同じフォルダに置いて使う。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from pid import PID
from walls import side_wall

rc = racecar_core.create_racecar()

SPEED = 0.5       # 走る速さ（一定）

# ハンドルの PID（6-14 で合わせた値）。kd には「壁の向き（度）」のゲインを入れる
steer_pid = PID(kp=0.04, ki=0.005, kd=0.04, i_zone=20)

right = None      # 右の壁までの距離（update_slow で表示する）
left = None       # 左の壁までの距離
angle = 0.0


def start():
    rc.drive.stop()
    steer_pid.reset()
    print(">> 左右の壁の真ん中を走ります")


def update():
    global right, left, angle

    scan = rc.lidar.get_samples()
    right_angle, right = side_wall(scan, "right")
    left_angle, left = side_wall(scan, "left")

    if right is None or left is None:
        angle = 0.0                                   # 片側でも見えないときは、まっすぐ（6-17 で考える）
    else:
        error = (right - left) / 2                    # ＋：真ん中より左にいる
        rate = (right_angle - left_angle) / 2         # ＋：左の壁のほうへ向かっている
        angle = steer_pid.update(error, rc.get_delta_time(), rate=rate)

    rc.drive.set_speed_angle(SPEED, angle)


def update_slow():
    if right is None or left is None:
        print("両側の壁が見えない")
    else:
        print(f"右 {right:5.1f} cm　左 {left:5.1f} cm　真ん中からのずれ {(right - left) / 2:+5.1f} cm　angle {angle:+.2f}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

- `from walls import side_wall`：同じフォルダの `walls.py` から、`side_wall()` を読みこみます。6-12 の `pid.py` と同じやり方です
- 目標の距離（TARGET）がなくなりました。目標は「右と左が同じ」ことだからです

説明用の簡単なモデルで、幅 150 cm の通路の、真ん中より 30 cm 右からスタートさせると、はじめの 6 秒は次のように表示されました。

```text
>> 左右の壁の真ん中を走ります
右  45.2 cm　左 103.6 cm　真ん中からのずれ -29.2 cm　angle -1.00
右  57.0 cm　左  90.8 cm　真ん中からのずれ -16.9 cm　angle +0.17
右  78.4 cm　左  71.7 cm　真ん中からのずれ  +3.3 cm　angle +0.35
右  77.1 cm　左  72.6 cm　真ん中からのずれ  +2.3 cm　angle -0.01
右  74.5 cm　左  75.3 cm　真ん中からのずれ  -0.4 cm　angle -0.03
右  74.6 cm　左  73.6 cm　真ん中からのずれ  +0.5 cm　angle +0.04
右  50.5 cm　左  49.7 cm　真ん中からのずれ  +0.4 cm　angle -0.07
```

最後の行は、幅が 100 cm にせまくなった所です。左右の距離はどちらも 50 cm くらいに変わりましたが、真ん中からのずれは 0 のままです。

![幅や向きが変わる通路を上から見た図。通路は、幅 150 cm でまっすぐ始まり、幅 100 cm にせまくなり、左へ 45° 曲がってから、また上へ向きを変え、幅 250 cm に広がり、右へ 45° 曲がって、幅 150 cm にもどる。緑の点線が通路の真ん中。左右の真ん中を走る車（オレンジ）は、曲がり角で少しふくらむものの、終わりまでほぼ真ん中の線にそって走る。右の壁から 50 cm で走る車（灰色）は、はじめは右よりを走り、幅が 250 cm に広がる所で右へ曲がりこんで、壁にぶつかる](/images/racecar-neo-jp/6-16/fig1-center.png)
*図1　幅や向きが変わる通路を走る（speed 0.5、説明用の簡単なモデル）*

真ん中を走るプログラムは、幅 100 cm でも 250 cm でも、目標の距離を変えずに、壁から 35 cm 以上離れたまま、最後まで走りきりました。

## ④ 数式・コード

### 片側だけより、ばらつきが小さくなるわけ

右の壁の距離と左の壁の距離には、それぞれ別のばらつきがあります。2つを使って $(d_R - d_L) / 2$ を計算すると、たがいに関係のないばらつきは、打ち消し合う分があるので、$\dfrac{1}{\sqrt{2}}$ 倍くらいに小さくなります（6-6 の平均と同じ考え方）。壁の向きも同じです。

### 真ん中ではなく、少しずらして走りたいとき

たとえば「真ん中より 20 cm 右」を走りたいときは、ずれを次のようにします。

```python
error = (right - left) / 2 + 20      # 20 cm 右が目標
```

右に 20 cm ずれた所では、$(d_R - d_L) / 2 = -20$ になるので、そこで error が 0 になります。

## ⑤ つまずきポイント

### 左の壁の角度をまちがえる

左ななめ前は、270° より「前」なので、270 + 30 = **300°** です。240° にすると、左ななめ**後ろ**を見てしまい、壁の向きの符号が逆になります。

### 通路のはばが MAX_WALL の2倍より広い

`side_wall()` は、300 cm より遠い壁を「見えない」とします。通路の幅が 600 cm より広いと、真ん中を走っている間、どちらの壁も見えなくなります。どうするかは、6-17・6-18 で考えます。

### 片側の壁がとぎれると、まっすぐ走ってしまう

このプログラムは、片側でも壁が見えないと、angle を 0 にします。入り口や曲がり角で片側の壁がとぎれると、そのまままっすぐ進みます。状態を切りかえて対応する方法を、次の 6-17 で学びます。

## ⑥ 確認問題

**問1**　右の壁まで 90 cm、左の壁まで 60 cm でした。真ん中からのずれは何 cm で、どちらにハンドルを切りますか。

:::details 答え
$(90 - 60) \div 2 = +15$ cm です。＋なので、真ん中より左に寄っています。右にハンドルを切ります。
:::

**問2**　右の壁の向きが +4°、左の壁の向きが −4° でした。車は通路に対して、どちらを向いていますか。

:::details 答え
$(4 - (-4)) \div 2 = +4°$ なので、左へ向かっています（右の壁から離れ、左の壁に近づく向き）。
:::

**問3**　真ん中を走るプログラムで、目標の距離（TARGET）がいらないのはなぜですか。

:::details 答え
目標が「右と左の距離が同じになること」だからです。通路の幅が変わっても、目標を決め直す必要がありません。
:::

## ⑦ 原典

- Lab I の課題（両側に壁があるときは、真ん中を走る）：**Lab I - Wall Follower**（`labs/lab_i/lab_i.py`）：[racecar-neo-prereq-labs](https://github.com/MITRacecarNeo/racecar-neo-prereq-labs)（MIT License）
- `get_lidar_average_distance()`・`get_lidar_closest_point()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）

図1と `wall_follow_center.py` の表示は、この本で作った説明用の簡単なモデル（上から見た2次元の車と壁、LIDAR の計算）によるものです。
