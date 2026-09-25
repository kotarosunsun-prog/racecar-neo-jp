---
title: "6-19 速度も PID で制御する"
free: true
---

6-18 では、ずっと同じ速さ（speed 0.5）で、曲がり角のあるコースを走りきりました。でも、まっすぐな所でも、曲がり角と同じ速さで走るのは、もったいないですね。この回では、**正面の壁までの距離**から速さを決めて、まっすぐな所では速く、曲がり角の前では遅く走るようにします。さらに、速さが変わっても、ハンドルの PID がうまく働くように、**速さに合わせてゲインを変える**方法を学びます。

## ① この回でできるようになること

1. ずっと同じ速さで走ると、何が困るかを説明できる
2. 正面の壁までの距離から、PID で速さを決めるプログラムを作れる
3. 速さが変わると、ハンドルの PID の効き方が変わる理由を説明できる
4. 速さに合わせて、ハンドルの PID のゲインを変えられる（ゲインスケジューリング）

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Speed control | 速さの制御 | 状況に合わせて、速さを変えること |
| Gain scheduling | ゲインスケジューリング | 速さなどに合わせて、PID のゲインを切りかえること |
| Encoder | エンコーダ | 車輪の回転を数えて、進んだ距離や速さを測るセンサー |
| Lap time | ラップタイム | コースを1周（またはスタートからゴールまで）走るのにかかった時間 |

## ③ 本文

:::message
この回と 6-20 では、**速い車**の説明用モデルを使います。speed 1.0 で 3 m/秒 まで出て、横向きの加速度が 5 m/秒² をこえると、タイヤが横にすべって、ハンドルを切っても曲がりきれなくなる車です。これまでのモデル（speed 1.0 で 1.5 m/秒、すべらない）では、ずっと speed 1.0 でも 6-18 のコースを走りきれてしまい、速さを変える意味が見えにくいからです。
実物の車の速さは、`rc.drive.set_max_speed()`（最初は 0.25）や、車体・床で変わります。この回の数字は、そのまま実物には使えません。考え方を学んでください。
:::

### ずっと同じ速さでは、速くできない

6-18 のプログラム（ずっと同じ速さ）で、速い車のモデルを、6-18 と同じコース（図1）で走らせました。

| 走り方 | 結果 | 壁にいちばん近づいた距離 |
|---|---|---|
| ずっと speed 0.5 | ゴールまで 23.3 秒 | 32.7 cm |
| ずっと speed 0.6 | ゴールまで 19.5 秒 | 39.7 cm |
| ずっと speed 0.7 | 広い所のあとの、右へ 90° 曲がる角でぶつかった | ― |
| ずっと speed 1.0 | 左へ 90° 曲がったすぐあとの、右へ 90° 曲がる角でぶつかった | ― |

speed 0.7 より速くすると、曲がり角を曲がりきれません。速く走ると、6-15 で考えた「反応の間に進む距離」が長くなるうえに、タイヤがすべって、大きく回りこむからです。

でも、コースの大部分は、まっすぐな所です。**曲がり角の前だけ遅くして、まっすぐな所では速く走れば**、もっと速くゴールできるはずです。

### 正面の壁までの距離で、速さを決める

曲がり角が近いかどうかは、**正面の壁までの距離**でわかります（6-15、6-18）。そこで、正面の壁までの距離から、PID で速さを決めます。

```python
# 速さの PID：正面の壁までの距離が FRONT_TARGET より遠いほど速く。命令は MIN_SPEED〜MAX_SPEED
speed_pid = PID(kp=0.005, ki=0.0, kd=0.0, out_min=MIN_SPEED, out_max=MAX_SPEED)
```

```python
    # 4. 正面の壁までの距離から、速さを決める
    speed = speed_pid.update(front - FRONT_TARGET, dt)
```

- ずれは「正面の壁までの距離 − `FRONT_TARGET`（60 cm）」です。正面の壁が遠いほど、ずれが大きく、速くなります
- 6-12 の `PID` クラスの `out_min`、`out_max` で、命令を `MIN_SPEED`（0.3）〜`MAX_SPEED`（1.0）の間にします。曲がり角の手前でも、0.3 より遅くはしません
- I と D は 0 にして、P だけで使います

P だけなので、speed は「0.005 ×（正面の壁までの距離 − 60）」を 0.3〜1.0 の間におさめたものです。

| 正面の壁まで | speed の命令 |
|---|---|
| 260 cm 以上 | 1.0（いちばん速い） |
| 200 cm | 0.70 |
| 150 cm | 0.45 |
| 120 cm 以下 | 0.3（いちばん遅い） |

:::message
**なぜ I を使わないの？**　ハンドルの PID は、「壁から 50 cm」のように、ずれを 0 にしたいので I を使いました（6-11）。速さの PID では、ずれ（正面の壁までの距離 − 60 cm）を 0 にしたいわけではありません。まっすぐな所ではずっと遠いので、I を入れると、積分がたまり続けてしまいます（6-12 のワインドアップ）。D も試しましたが、かえって少し遅くなりました（D のゲイン 0.001 で 18.6 秒）。
:::

### 速さが変わると、ハンドルの効き方が変わる

速さを変えるようにしただけのプログラムは、ゴールまで 18.4 秒でした。ずっと speed 0.6 の 19.5 秒より、少し速くなりました。

でも、まだ問題があります。ハンドルの PID のゲイン（KP 0.04、KI 0.005、KD 0.04）は、6-14 で **speed 0.5 のときに**合わせたものです。同じだけハンドルを切っても、速く走っているほど、

- 向きが速く変わり（同じ時間に、長い距離を曲がるので）
- その向きで、横に速くずれます（同じ時間に、長い距離を進むので）

つまり、速く走るほど、ハンドルが「効きすぎ」になります。6-8 で見たように、効きすぎると、ふらつきます。逆に、遅く走るときは、ハンドルが効かなくなります。

そこで、**速さに合わせて、ゲインを変えます**。これを**ゲインスケジューリング**といいます。

```python
    # 0. 速さに合わせて、ハンドルのゲインを変える（速いほど小さく）
    f = BASE_SPEED / max(speed, 0.2)
    steer_pid.kp = KP0 * f * f
    steer_pid.ki = KI0 * f * f
    steer_pid.kd = KD0 * f
```

- `BASE_SPEED` は、ゲインを合わせたときの速さ（0.5）です。`f` は「合わせたときの何分の1の速さか」の逆数です。speed 1.0 なら `f = 0.5` です
- KP と KI は $f^2$ 倍、KD は $f$ 倍にします。なぜ2乗なのかは、④で説明します
- `speed` は、前のコマで決めた速さの命令です。`max(speed, 0.2)` は、speed が 0 に近いときに、ゲインがとても大きくなるのを防ぎます

speed 1.0 のとき、KP は 0.04 × 0.25 = 0.01、KD は 0.04 × 0.5 = 0.02 になります。

### やってみよう：速さを変えて走る

6-18 の `wall_follow_course.py` に、速さの PID と、ゲインスケジューリングを足します。変えた所は、次のとおりです。

- 一定の `SPEED` のかわりに、`MAX_SPEED`、`MIN_SPEED`、`FRONT_TARGET`、`BASE_SPEED` を決める
- `speed_pid` を作り、`start()` で `reset()` する
- `update()` の最初に、ゲインを変える部分（0.）を、最後に、速さを決める部分（4.）を足す
- 状態や曲がる向きの表示のかわりに、`update_slow()` で、状態・正面の壁までの距離・speed を表示する

:::details wall_follow_speed.py の全体
```python:wall_follow_speed.py
"""
wall_follow_speed.py
6-18 の wall_follow_course.py に、速さの制御を足したもの（6-19）。
・正面の壁までの距離から、PID で速さを決める（壁が近いと遅く、遠いと速く）
・速さに合わせて、ハンドルの PID のゲインを変える
walls.py と pid.py を同じフォルダに置いて使う。
"""

import sys
from enum import IntEnum

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from pid import PID
from walls import side_wall, front_distance

rc = racecar_core.create_racecar()

MAX_SPEED = 1.0   # いちばん速いときの speed
MIN_SPEED = 0.3   # いちばん遅いときの speed（曲がり角でも、これより遅くしない）
FRONT_TARGET = 60 # 正面の壁までの距離が、この値に近づくほど遅くする（cm）
BASE_SPEED = 0.5  # ハンドルのゲインを合わせたとき（6-14）の speed
HOLD = 10         # 新しい状態がこのコマ数だけ続いたら、切りかえる
FRONT_LIMIT = 200 # 正面の壁がこれより近いと、開いている側へ切りはじめる（cm）
KF = 0.02         # 正面の壁が 1 cm 近づくごとに、切る量


class State(IntEnum):
    BOTH = 0      # 両側の壁が見える
    RIGHT = 1     # 右の壁だけ見える
    LEFT = 2      # 左の壁だけ見える
    NONE = 3      # どちらも見えない


# ハンドルの PID（BASE_SPEED のときのゲイン。走りながら、速さに合わせて変える）
KP0, KI0, KD0 = 0.04, 0.005, 0.04
steer_pid = PID(kp=KP0, ki=KI0, kd=KD0, i_zone=20)

# 速さの PID：正面の壁までの距離が FRONT_TARGET より遠いほど速く。命令は MIN_SPEED〜MAX_SPEED
speed_pid = PID(kp=0.005, ki=0.0, kd=0.0, out_min=MIN_SPEED, out_max=MAX_SPEED)
speed = MIN_SPEED        # 今の speed の命令

state = State.BOTH
candidate = State.BOTH   # 切りかえようとしている状態
count = 0                # candidate が続いているコマ数
target_right = 50.0      # 右の壁だけのとき、保つ距離
target_left = 50.0       # 左の壁だけのとき、保つ距離
front = 0.0              # 正面の壁までの距離（update_slow で表示する）


def seen_state(right, left):
    """見えている壁から、今の状態を決める"""
    if right is not None and left is not None:
        return State.BOTH
    if right is not None:
        return State.RIGHT
    if left is not None:
        return State.LEFT
    return State.NONE


def open_side(scan):
    """右ななめ前と左ななめ前の、開いているほうを返す（＋1：右、－1：左）"""
    r = rc_utils.get_lidar_average_distance(scan, 45, 10)
    l = rc_utils.get_lidar_average_distance(scan, 315, 10)
    if r == 0.0:
        r = 1000.0              # 何も見えない（とても遠い）
    if l == 0.0:
        l = 1000.0
    if r > l:
        return 1
    return -1


def start():
    global state, candidate, count, speed
    rc.drive.stop()
    steer_pid.reset()
    speed_pid.reset()
    speed = MIN_SPEED
    state = State.BOTH
    candidate = State.BOTH
    count = 0
    print(">> 正面の壁までの距離で速さを決め、速さに合わせてハンドルのゲインを変えます")


def update():
    global state, candidate, count, target_right, target_left, speed, front

    # 0. 速さに合わせて、ハンドルのゲインを変える（速いほど小さく）
    f = BASE_SPEED / max(speed, 0.2)
    steer_pid.kp = KP0 * f * f
    steer_pid.ki = KI0 * f * f
    steer_pid.kd = KD0 * f

    scan = rc.lidar.get_samples()
    right_angle, right = side_wall(scan, "right")
    left_angle, left = side_wall(scan, "left")

    # 1. 状態を決める（新しい状態が HOLD コマ続いたら切りかえる）
    seen = seen_state(right, left)
    if seen == state:
        count = 0
    else:
        if seen == candidate:
            count += 1
        else:
            candidate = seen
            count = 1
        if count >= HOLD:
            state = seen
            count = 0
            steer_pid.reset()                    # 前の状態でためた積分は使わない
            if state == State.RIGHT:
                target_right = right             # 切りかえたときの距離を保つ
            if state == State.LEFT:
                target_left = left

    # 2. 状態に合わせて、ずれと向きを決める
    angle = 0.0
    dt = rc.get_delta_time()
    if state == State.BOTH and right is not None and left is not None:
        angle = steer_pid.update((right - left) / 2, dt, rate=(right_angle - left_angle) / 2)
    elif state == State.RIGHT and right is not None:
        angle = steer_pid.update(right - target_right, dt, rate=right_angle)
    elif state == State.LEFT and left is not None:
        angle = steer_pid.update(target_left - left, dt, rate=-left_angle)
    # State.NONE（または、切りかえを待っている間に壁が見えないとき）は、まっすぐ

    # 3. 正面に壁が近づいたら、開いている側へ切る（6-15）
    front = front_distance(scan)
    if front < FRONT_LIMIT:
        side = open_side(scan)
        angle += side * KF * (FRONT_LIMIT - front)
    angle = rc_utils.clamp(angle, -1.0, 1.0)

    # 4. 正面の壁までの距離から、速さを決める
    speed = speed_pid.update(front - FRONT_TARGET, dt)

    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    print(f"状態 {state.name:5}　正面の壁まで {front:6.1f} cm　speed {speed:.2f}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```
:::

説明用のモデルで走らせると、1秒ごとに、次のように表示されました（ゴールを過ぎるまで）。

```text
状態 BOTH 　正面の壁まで  417.0 cm　speed 1.00
状態 BOTH 　正面の壁まで  329.7 cm　speed 1.00
状態 BOTH 　正面の壁まで  187.6 cm　speed 0.64
状態 BOTH 　正面の壁まで  243.3 cm　speed 0.92
状態 BOTH 　正面の壁まで  207.5 cm　speed 0.74
状態 RIGHT　正面の壁まで  111.9 cm　speed 0.30
状態 BOTH 　正面の壁まで  282.6 cm　speed 1.00
状態 BOTH 　正面の壁まで  244.2 cm　speed 0.92
状態 LEFT 　正面の壁まで   95.1 cm　speed 0.30
状態 BOTH 　正面の壁まで  203.5 cm　speed 0.72
状態 BOTH 　正面の壁まで  168.4 cm　speed 0.54
状態 BOTH 　正面の壁まで  122.1 cm　speed 0.31
状態 BOTH 　正面の壁まで  366.1 cm　speed 1.00
状態 BOTH 　正面の壁まで  115.3 cm　speed 0.30
状態 LEFT 　正面の壁まで  255.9 cm　speed 0.98
状態 BOTH 　正面の壁まで  181.5 cm　speed 0.61
状態 BOTH 　正面の壁まで  174.0 cm　speed 0.57
状態 BOTH 　正面の壁まで 1000000.0 cm　speed 1.00
```

まっすぐな所では speed 1.0 で走り、曲がり角が近づくと 0.3 まで落としています。最後の行の 1000000.0 cm は、ゴールの先が開いていて、正面の窓に何も見えないときの値です。`get_lidar_closest_point()` は、何も見えないと、とても大きな値を返します（5-3）。このときは、いちばん速い 1.0 になります。

![6-18 のコースを上から見た図と、車の速さのグラフ。左の図では、速さの PID とゲインの切りかえを使った車の通り道を、速さで色分けしている。まっすぐな所では黄色（約 3 m/秒）、曲がり角の手前では紫（約 1 m/秒）になる。ずっと speed 0.7 の車（灰色の点線）は、広い所のあとの、右へ 90° 曲がる角で壁にぶつかる。右のグラフでは、ずっと speed 0.6 の車が 1.8 m/秒 のまま 19.5 秒でゴールするのに対し、速さの PID の車は 1 m/秒 から 3 m/秒 の間で速さを変え、16.8 秒でゴールする](/images/racecar-neo-jp/6-19/fig1-speed.png)
*図1　曲がり角の前で速さを落とす（速い車、説明用の簡単なモデル）*

| 走り方 | ゴールまで | 壁にいちばん近づいた距離 |
|---|---|---|
| ずっと speed 0.6 | 19.5 秒 | 39.7 cm |
| 速さの PID（ゲインはそのまま） | 18.4 秒 | 32.9 cm |
| 速さの PID ＋ ゲインスケジューリング | 16.8 秒 | 33.8 cm |

ゲインスケジューリングを入れると、壁との距離はほとんど変わらずに、ゴールまでの時間が 1.6 秒ちぢみました。速いときにハンドルが効きすぎなくなり、ふらつきが減ったからです。ゴールまでのハンドルの切り方（angle の大きさ）の平均は、0.63 から 0.41 に小さくなり、speed の命令の平均は、0.65 から 0.70 に上がりました。

## ④ 数式・コード

### なぜ KP は速さの2乗で変えるのか

速さ $v$ で走る車が、ハンドルを切って、曲がり具合（曲率、半径の逆数）$\kappa$ で曲がるとします。

- 向き $\psi$ が変わる速さは、$\dfrac{d\psi}{dt} = v \kappa$ です（同じ時間に、長い距離を曲がる）
- 壁からの距離 $y$ が変わる速さは、向きのずれが小さければ、$\dfrac{dy}{dt} \approx v \psi$ です

2つを合わせると、$\dfrac{d^2 y}{dt^2} \approx v^2 \kappa$ です。ハンドルの効き目（距離の変わり方）は、**速さの2乗**に比例します。

曲率 $\kappa$ は、ハンドルの命令 angle にほぼ比例します。PID の命令は、angle $= K_P \, e + K_D \, \psi + \cdots$ でした（D のかわりに、壁の向き $\psi$ を使っています。6-10）。これを入れると、

$$
\frac{d^2 y}{dt^2} \approx c \left( v^2 K_P \, e + v^2 K_D \, \psi \right) = c \left( v^2 K_P \, e + v K_D \, \frac{dy}{dt} \right)
$$

（$c$ は、angle と曲率の比）となります。速さが変わっても同じ動き方にするには、$v^2 K_P$ と $v K_D$ を一定にすればよいので、

$$
K_P = K_{P0} \left( \frac{v_0}{v} \right)^2, \qquad K_D = K_{D0} \, \frac{v_0}{v}
$$

とします（$v_0$ はゲインを合わせたときの速さ、$K_{P0}, K_{D0}$ はそのときのゲイン）。I は P と同じく、ずれ $e$ にかけるので、$K_I$ も $\left( v_0 / v \right)^2$ 倍にします。プログラムの `f` が $v_0 / v$ です。

### 速いほど、遠くを見る

6-15 で、P と「壁の向き」の組み合わせは、$L = \dfrac{K_A}{K_P} \times \dfrac{180}{\pi}$ だけ先を見ているのと同じだとわかりました（$K_P = K_A = 0.04$ で 57 cm）。6-12 からは、壁の向きのゲイン $K_A$ を、PID の $K_D$ として入れています。ゲインスケジューリングでは、

$$
\frac{K_D}{K_P} = \frac{K_{D0} f}{K_{P0} f^2} = \frac{K_{D0}}{K_{P0}} \cdot \frac{v}{v_0}
$$

なので、見る距離 $L$ は速さに比例します。speed 1.0 では 114 cm 先、speed 0.3 では 34 cm 先を見ることになります。人が自転車に乗るときも、速いときほど遠くを見ますね。

### 速さの「本当の」PID

このプログラムの速さの PID は、正面の壁までの距離を見て、speed の**命令**を決めています。車の本当の速さは、測っていません。

実物の車では、`rc.physics.get_encoder_speed()` で、車輪の回転から測った速さ（m/秒）がわかります。これを使えば、「目標の速さ」と「測った速さ」のずれで PID をかける、本当の速さの制御ができます。坂道や、電池の減り具合で、同じ命令でも速さが変わるときに役立ちます（第9章）。シミュレーターでは、`get_encoder_speed()` はいつも 0.0 を返すので、この方法は使えません。

## ⑤ つまずきポイント

### 曲がり角で、遅くなりきれない

車はすぐには遅くなれません（6-15 の遅れ）。速い車ほど、`FRONT_TARGET` を大きくするか、速さの PID の KP を小さくして、遠くから遅くしはじめる必要があります。まずは `MAX_SPEED` を小さくして走らせ、確実に曲がれることを確かめてから、少しずつ上げましょう。

### ゲインスケジューリングで、遅いときにふらつく

`f` が大きくなると（遅いとき）、KP は $f^2$ 倍に大きくなります。speed 0.3 で `f` は約 1.67、KP は約 2.8 倍です。`MIN_SPEED` をあまり小さくすると、ゲインが大きくなりすぎて、ふらつきます。`max(speed, 0.2)` のように、下限を決めておきましょう。

### 実物の車で、急に速くしない

実物の車は、speed 1.0 だと、とても速く走ります。最初は `rc.drive.set_max_speed()` をそのまま（0.25）にして、広い所で試しましょう。速い車がぶつかると、車も壁も、人もけがをします。

## ⑥ 確認問題

**問1**　`FRONT_TARGET = 60`、速さの PID の KP が 0.005 で、正面の壁まで 150 cm のとき、speed の命令はいくつですか（`MIN_SPEED = 0.3`、`MAX_SPEED = 1.0`）。

:::details 答え
$0.005 \times (150 - 60) = 0.45$ です。0.3〜1.0 の間なので、そのまま 0.45 です。
:::

**問2**　`BASE_SPEED = 0.5`、`KP0 = 0.04`、`KD0 = 0.04` で、speed が 0.25 のとき、KP と KD はいくつになりますか。

:::details 答え
$f = 0.5 / 0.25 = 2$ なので、KP は $0.04 \times 2^2 = 0.16$、KD は $0.04 \times 2 = 0.08$ です。遅いときは、ハンドルが効きにくいので、ゲインを大きくします。
:::

**問3**　速さが2倍になると、同じハンドルの命令で、壁からの距離の変わり方（$d^2y/dt^2$）は何倍になりますか。

:::details 答え
速さの2乗に比例するので、4倍です。だから KP を $1/4$ にします。
:::

## ⑦ 原典

- `rc.drive.set_speed_angle()`・`rc.drive.set_max_speed()`・`rc.physics.get_encoder_speed()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `drive.py`・`physics.py`（GPL-3.0）
- ゲインスケジューリングと、車のハンドルの制御の考え方：K. J. Åström, R. M. Murray, *Feedback Systems: An Introduction for Scientists and Engineers*, Princeton University Press（2008）

図1と `wall_follow_speed.py` の表示は、この本で作った説明用の簡単なモデル（上から見た2次元の車と壁、LIDAR の計算）によるものです。速い車のモデル（speed 1.0 で 3 m/秒、横向きの加速度 5 m/秒² まで）も、この本で決めたもので、実物の車の値ではありません。
