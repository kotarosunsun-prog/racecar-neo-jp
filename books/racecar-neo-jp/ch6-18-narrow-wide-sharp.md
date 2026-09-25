---
title: "6-18 狭い通路・広い通路・急カーブ"
free: true
---

Lab I の自動採点には、90° の曲がり角（90 Degree）、せまい通路（Tight）、柱の並ぶ所（Posts）などのコースがありました（6-4）。この回では、6-17 の「状態で切りかえる」プログラムに、6-15 の「正面を見る」を組み合わせて、**急な曲がり角**を曲がれるようにします。あわせて、**せまい通路**と**広い通路**で気をつけることを考えます。

## ① この回でできるようになること

1. 90° の曲がり角で、横の壁だけでは曲がれない理由を説明できる
2. 正面に壁が近づいたとき、右と左のどちらへ曲がるべきかを、LIDAR で決められる
3. せまい通路・広い通路で、何に気をつければよいかを説明できる
4. 曲がり角・せまい所・広い所のあるコースを、最後まで走るプログラムを作れる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Sharp turn | 急カーブ | 90° のように、急に向きが変わる曲がり角 |
| Clearance | すき間（余裕） | 車と壁の間のあき |
| Open side | 開いている側 | 右ななめ前と左ななめ前のうち、遠くまで何もないほう |
| Corner case | 特別な場合 | ふつうの考え方ではうまくいかない、めずらしい場面 |

## ③ 本文

### 90° の曲がり角では、横の壁が消える

6-17 のプログラムで、曲がり角のある通路を走らせました（説明用の簡単なモデル、speed 0.5）。右へ 45° 曲がる所は曲がれましたが、左へ 90° 曲がる所で、正面の壁にぶつかりました（図1の灰色）。

90° の曲がり角では、曲がる側の壁が、急にとぎれます。6-17 のプログラムは、壁がとぎれると「見えている側の壁から、そのときの距離を保つ」ので、まっすぐ進み続けます。曲がる先の通路は、横の光線では見えません。

### 正面を見て、開いている側へ曲がる

6-15 では、右の壁にそって走るので、正面に壁が来たら「左へ」曲がりました。でも、両側の壁を見て走るときは、右へ曲がる角も、左へ曲がる角もあります。そこで、**右ななめ前（45°）と左ななめ前（315°）の距離を比べて、遠いほう（開いているほう）へ**曲がることにします。

```python
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
```

- `get_lidar_average_distance(scan, 45, 10)`：45° のまわり ±5° の平均です（3つめの引数が窓の広さ）
- 0.0（データなし）は、遠すぎて測れなかったということなので、とても遠い（1000 cm）とみなします

そして、6-15 と同じように、正面の壁が `FRONT_LIMIT` より近くなったら、近いほど強く、開いている側へ切ります。

```python
    # 3. 正面に壁が近づいたら、開いている側へ切る（6-15）
    front = front_distance(scan)
    if front < FRONT_LIMIT:
        side = open_side(scan)
        angle += side * KF * (FRONT_LIMIT - front)
```

### やってみよう：曲がり角のあるコースを走る

6-17 の `wall_follow_states.py` に、`open_side()` と、正面を見る部分を足します。正面の壁を見て曲がりはじめたときに、1回だけ表示するようにしています。

:::details wall_follow_course.py の全体
```python:wall_follow_course.py
"""
wall_follow_course.py
6-17 の「状態で切りかえる」に、正面の壁を見て、開いている側へ曲がる部分を足したもの（6-18）。
急な曲がり角・せまい通路・広い通路のあるコースを走る。walls.py と pid.py を同じフォルダに置いて使う。
"""

import sys
from enum import IntEnum

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from pid import PID
from walls import side_wall, front_distance

rc = racecar_core.create_racecar()

SPEED = 0.5       # 走る速さ（一定）
HOLD = 10         # 新しい状態がこのコマ数だけ続いたら、切りかえる
FRONT_LIMIT = 200 # 正面の壁がこれより近いと、開いている側へ切りはじめる（cm）
KF = 0.02         # 正面の壁が 1 cm 近づくごとに、切る量


class State(IntEnum):
    BOTH = 0      # 両側の壁が見える
    RIGHT = 1     # 右の壁だけ見える
    LEFT = 2      # 左の壁だけ見える
    NONE = 3      # どちらも見えない


steer_pid = PID(kp=0.04, ki=0.005, kd=0.04, i_zone=20)

state = State.BOTH
candidate = State.BOTH   # 切りかえようとしている状態
count = 0                # candidate が続いているコマ数
target_right = 50.0      # 右の壁だけのとき、保つ距離
target_left = 50.0       # 左の壁だけのとき、保つ距離
turning = False          # 正面の壁を見て曲がっている最中か


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
    global state, candidate, count, turning
    rc.drive.stop()
    steer_pid.reset()
    state = State.BOTH
    candidate = State.BOTH
    count = 0
    turning = False
    print(">> 見えている壁に合わせて走り、正面に壁が来たら開いている側へ曲がります")


def update():
    global state, candidate, count, target_right, target_left, turning

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
            print(f"状態を {state.name} にした")

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
        if not turning:
            print(f"正面の壁まで {front:.0f} cm：{'右' if side > 0 else '左'}へ曲がる")
        turning = True
    else:
        turning = False
    angle = rc_utils.clamp(angle, -1.0, 1.0)

    rc.drive.set_speed_angle(SPEED, angle)


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
```
:::

説明用の簡単なモデルで、図1のコースを走らせました。左へ 90° 曲がる角の前後で、次のように表示されました。

```text
正面の壁まで 195 cm：左へ曲がる
正面の壁まで 200 cm：左へ曲がる
状態を RIGHT にした
状態を NONE にした
状態を BOTH にした
正面の壁まで 200 cm：右へ曲がる
```

正面の壁に近づくと、左ななめ前が開いているのを見て、左へ曲がっています。曲がっている間は、左の壁が見えなくなって RIGHT になり、曲がり角のまん中では両側とも見えなくなって NONE になり、曲がり終えると、新しい通路の両側の壁が見えて BOTH にもどりました。最後の行は、次の右へ曲がる角です。

![曲がり角・せまい所・広い所のあるコースを上から見た図。幅 150 cm の通路が、右へ 45° 曲がり、左へ 90° 曲がり、右へ 90° 曲がって、幅 90 cm のせまい所、幅 300 cm の広い所を通り、右へ 90°、左へ 90° 曲がってゴールへ向かう。状態で切りかえるだけのプログラム（灰色）は、左へ 90° 曲がる角で、正面の壁にぶつかる。正面を見て、開いている側へ曲がるプログラム（オレンジ）は、最後まで走りきる。オレンジの線の上の赤い点は、正面の壁を見て曲げている所で、曲がり角の手前に集まっている](/images/racecar-neo-jp/6-18/fig1-course.png)
*図1　曲がり角・せまい所・広い所のあるコース（speed 0.5、説明用の簡単なモデル）*

このプログラムは、図1のコースを、壁から 43.9 cm 以上離れたまま、46.0 秒で走りきりました。

### せまい通路で気をつけること

- **真ん中を走る**：両側の壁が見えていれば、BOTH の状態で真ん中を走るので、通路のはばが変わっても大丈夫です。図1の幅 90 cm の所でも、両側の壁から 45 cm 前後を走りました
- **片側だけのときの距離**：RIGHT や LEFT で、そのときの距離を保つようにしたので、せまい通路でも、急に壁に寄ろうとはしません。ただし、「右の壁から 50 cm」のように決まった距離を使うときは、通路のはばの半分より小さくしておく必要があります
- **入り口の角**：通路が急にせまくなる所では、正面 ±10° の窓に、せまくなる所の角が入ることがあります。図1でも、幅 90 cm の所の手前で、正面を見て少し曲げています（赤い点）。気になるときは、正面の窓をせまく（たとえば ±5°）してみましょう

### 広い通路で気をつけること

- **見える距離**：`walls.py` の `MAX_WALL`（300 cm）より遠い壁は、見えないことになります。図1の幅 300 cm の所は、真ん中から両側の壁まで 150 cm なので、BOTH のままです。はばが 600 cm をこえると、真ん中では両側とも見えなくなり、NONE（まっすぐ）になります
- **広い所では、どこを走るか**：とても広い所では、真ん中より、どちらかの壁にそって走ったほうが、次の曲がり角を見つけやすいこともあります。コースに合わせて、`MAX_WALL` や、状態ごとの走り方を決めましょう

## ④ 数式・コード

### 45° の光線で、どこまで先が見えるか

幅 $w$ の通路の真ん中を走っているとき、45° の光線は、横に $w/2$ 進むあいだに、前にも $w/2$ 進んで、壁に当たります。長さは $\dfrac{w}{2} \times \sqrt{2}$ です。幅 150 cm なら約 106 cm です。曲がり角で片側の壁がとぎれると、その側の 45° の光線だけが遠くまで届くので、開いている側がわかります。

### 曲がりはじめる距離と、速さ

6-15 と同じく、`FRONT_LIMIT` は、回転半径と、反応の間に進む距離で決まります。速く走ると、反応の間に進む距離が長くなり、さらに実物の車では、タイヤが横にすべって、同じハンドルでも大きく曲がれなくなります。速さを上げるときは、曲がり角の前で速さを落とすのが確実です。これを 6-19 で学びます。

## ⑤ つまずきポイント

### 行き止まりや、T 字路で迷う

`open_side()` は、「遠いほう」を選ぶだけです。行き止まりでは、どちらも近いので、正しく曲がれません。T 字路のように、両側が開いている所では、ばらつきで選ぶ側が変わることもあります。Lab I のコースは1本道なので、この方法で走れますが、分かれ道のあるコースでは、6-3 の AR マーカーのような目印を使います。

### 曲がり角で、状態がせわしなく切りかわる

曲がり角では、壁の見え方が大きく変わるので、状態がいくつも切りかわります。`HOLD` が小さすぎると、チャタリングが起きやすくなります（6-17）。

### 曲がりきれずに、外側の壁にこする

速く走ると、曲がりはじめるのが間に合いません。まずはゆっくりの SPEED で、確実に曲がれることを確かめてから、速くしていきましょう。

## ⑥ 確認問題

**問1**　右ななめ前（45°）の平均が 320 cm、左ななめ前（315°）の平均が 110 cm でした。`open_side()` は何を返しますか。

:::details 答え
`1`（右）です。右ななめ前のほうが遠いので、右が開いています。
:::

**問2**　`FRONT_LIMIT = 200`、`KF = 0.02` で、正面の壁まで 170 cm、`open_side()` が `-1` でした。angle にいくつ足されますか。

:::details 答え
$-1 \times 0.02 \times (200 - 170) = -0.6$ です。左へ 0.6 だけ切ります。
:::

**問3**　幅 700 cm の広い部屋の真ん中を走っているとき、`MAX_WALL = 300` なら、状態は何になりますか。

:::details 答え
両側の壁まで 350 cm で、どちらも `MAX_WALL` より遠いので、NONE（まっすぐ）になります。
:::

## ⑦ 原典

- Lab I のコース（90 Degree、Tight、Posts など）：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `LevelCollection.cs`
- `get_lidar_average_distance()`（3つめの引数で窓の広さを決める）・`get_lidar_closest_point()`・`clamp()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）

図1と `wall_follow_course.py` の表示は、この本で作った説明用の簡単なモデル（上から見た2次元の車と壁、LIDAR の計算）によるものです。
