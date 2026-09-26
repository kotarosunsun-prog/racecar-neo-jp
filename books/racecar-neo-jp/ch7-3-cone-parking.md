---
title: "7-3 コーンを見つけて駐車する"
free: true
---

この回の課題は、オンライン事前コースの **Lab G**「自動駐車（Autonomous Parking）」です。オレンジ色のコーンをカメラで見つけて近づき、コーンの **30 cm 手前**に止まります。6-21 で作った「コーンの手前で止まる」に、7-2 のステートマシンを組み合わせて、コーンを探すところから、止まったあとまでを1つのプログラムにします。

## ① この回でできるようになること

1. Lab G の課題と、自動採点の条件を説明できる
2. 探す・近づく・合わせる・止まるの4つの状態で、駐車のステートマシンを設計できる
3. カメラで見たコーンの向きから、LIDAR でコーンまでの距離を測れる
4. シミュレータの表示に合わせて、目標の距離を調整（較正）できる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Parking | 駐車 | 決まった所に、ぴったり止まること |
| Field of view (FOV) | 視野 | カメラに写る範囲の角度 |
| Calibration | 較正（こうせい） | 測った値と本当の値のずれを調べて、合わせること |
| Tolerance | 許される誤差 | 目標から、どれだけずれても合格になるか |

## ③ 本文

### Lab G の課題

課題のファイルは、labs フォルダの中の `lab_g/lab_g.py` です。原典の Expected Outcome には、次のように書かれています。

- 車は、カラーカメラでオレンジのコーンを見つけ、カラーカメラと LIDAR を使って、コーンまで走って駐車する
- 車は、いくつかの状態をもつステートマシンで動く。**終わりの状態（terminal state）を作ってはいけない**。コーンがないときに、プログラムが止まって（クラッシュして）はいけない

さらに、ひな形の `update()` には、「実物の RACECAR Neo に合わせるため、**深度カメラは使わない**」とあります。距離は LIDAR で測ります。

シミュレータのレベルは、**Neo Labs** の **Lab G: Autonomous Parking** です。探索モードでは、画面を左クリックすると、コーンを動かせます。自動採点モードでは、コーンの置き方がちがう6つのコースを順番に走ります。

| 順番 | コース | 点数 | 制限時間 |
|---|---|---|---|
| 1 | Far（遠い） | 4 | ― |
| 2 | Close（近い） | 4 | ― |
| 3 | Very Far（とても遠い） | 3 | 15 秒 |
| 4 | Slight left（少し左） | 3 | 15 秒 |
| 5 | Far right（右の遠く） | 3 | 15 秒 |
| 6 | Near and left（近くて左） | 3 | 15 秒 |

どのコースも、課題は「コーンから 30 cm の所に駐車する」です。シミュレータのソースコードを読むと、画面に表示されるコーンまでの距離が **30 cm から 1 cm 以内**で、しかも車が**ほぼ止まっている**と、合格になります。

:::message
Lab G は自動採点つきの課題なので、この本では、オレンジの色の範囲などの答えの数値は載せません。5-1 の `hsv_probe.py` で、シミュレータのコーンの色を測って決めましょう。説明用のモデルでは、6-21 と同じ青のコーンを使っています。
:::

### 状態を設計する

7-2 の手順で、まず表にします。

| 状態 | すること | 切りかわる条件 → 次の状態 |
|---|---|---|
| SEARCH | ゆっくり円をえがいて、コーンを探す | コーンが見えた → APPROACH |
| APPROACH | コーンのほうへハンドルを切り、距離に比例した速さで近づく | 目標まで 10 cm 以内 → PARK |
| PARK | PI で少しずつ距離を合わせる（6-21） | 目標から 20 cm 以上ずれた → APPROACH<br>ずれ 1 cm 以内が 1 秒続いた → PARKED |
| PARKED | 止まって待つ | 目標から 3 cm 以上ずれた → PARK |

さらに、**どの状態でも**、コーンを見失ったら SEARCH にもどります（7-2 の④）。こうすると、「終わりの状態がない」「コーンがなくても止まらない」という Lab G の条件を、両方みたせます。PARKED も、ずれたら PARK にもどるので、終わりの状態ではありません。

### コーンの向きと距離

コーンの向きは、カメラの画像で、コーンの色のかたまりの中心の列から求めます（6-21）。列を −1〜1 にそろえたずれに、カメラの横の視野の半分をかけると、角度になります。シミュレータのカメラの横の視野は 69.4° なので、半分は 34.7° です。

$$
\text{コーンの向き} = \frac{\text{列} - 320}{320} \times 34.7°
$$

その向きの ±5° の LIDAR の点から、6-6 の「いちばん近い点に近い点だけの平均」で距離を求めます。いちばん近い点だけを使うより、ばらつきが小さくなります。

```python
def cone_distance(scan, x):
    """カメラで見たコーンの向きの ±5° で、いちばん近い点に近い点だけを平均した距離（6-6 の方法）"""
    a = x * HALF_FOV                                  # コーンの向き（度。右が＋）
    i = round(a * len(scan) / 360)                    # その向きの点の番号
    near = scan[np.arange(i - 10, i + 11) % len(scan)]   # ±5°（21 点）。0° をまたいでもよいように % を使う
    near = near[near > 0]                             # 0.0（測れなかった点）は使わない
    if len(near) == 0:
        return 0.0
    closest = near.min()
    return float(near[near < closest + 5].mean())     # いちばん近い点から 5 cm 以内の点の平均
```

コーンが左（向きが負）にあると、番号 `i` が負になります。`% len(scan)` で、720 点の後ろのほう（左側）の番号に直しています。

### 30 cm は、どこからの 30 cm か

シミュレータが表示する距離は、**コーンの表面から、車の表面まで**です。LIDAR は、車の中にある LIDAR から測るので、同じ場所にいても、LIDAR の値のほうが大きくなります。そこで、目標の `TARGET` は、「表示が 30 cm のときの、`cone_distance()` の値」にします。

説明用のモデルでは、車の中心から前のはしまでが 12 cm で、表示が 30 cm のとき、`cone_distance()` はおよそ 42.5 cm でした（29 cm のとき 41.5 cm、31 cm のとき 43.5 cm）。これで `TARGET = 42.5` にしました。

シミュレータでは、次のように合わせます。

1. `TARGET` をかりの値にして、プログラムを走らせる
2. PARKED になったら、画面の表示と、プログラムが表示した距離を読む
3. 表示が 31.2 cm なら、1.2 cm 遠すぎるので、`TARGET` を 1.2 小さくする。これを何回かくり返す

### プログラム

```python:cone_park.py
"""
cone_park.py
コーンを探して近づき、コーンの 30 cm 手前に止まる（7-3、Lab G）。4つの状態をステートマシンで切りかえる。
  SEARCH  ：コーンが見えるまで、ゆっくり円をえがいて探す
  APPROACH：コーンのほうへハンドルを切りながら近づく（速さは P だけ）
  PARK    ：目標の距離の近くで、PI で少しずつ合わせる
  PARKED  ：止まって待つ。距離がずれたら PARK へ、コーンを見失ったら SEARCH へ
pid.py を同じフォルダに置いて使う。
"""

import sys
from enum import IntEnum

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from pid import PID

rc = racecar_core.create_racecar()

CONE = ((90, 50, 50), (120, 255, 255))   # コーンの色（説明用のモデルでは青。Lab G のオレンジは自分で測る）
MIN_CONTOUR_AREA = 30                    # これより小さいかたまりは無視する
HALF_FOV = 34.7                          # カメラの横の視野の半分（度）。画面の右はしが、正面から右へ何度か
TARGET = 42.5                            # LIDAR で測った、コーンまでの距離の目標（cm）。画面の表示が 30 cm になる値
PARK_ZONE = 10.0                         # 目標までこの距離（cm）より近づいたら、APPROACH から PARK へ
DONE = 1.0                               # 目標とのずれがこれより小さい状態が、
HOLD_TIME = 1.0                          # この時間（秒）続いたら、PARKED へ


class State(IntEnum):
    SEARCH = 0
    APPROACH = 1
    PARK = 2
    PARKED = 3


steer_pid = PID(kp=1.0, ki=0.0, kd=0.0)
park_pid = PID(kp=0.01, ki=0.01, kd=0.0, i_zone=PARK_ZONE, out_min=-0.3, out_max=0.3)

state = State.SEARCH
timer = 0.0            # 今の状態になってからの時間（秒）
good_time = 0.0        # PARK で、ずれが DONE より小さい状態が続いている時間（秒）
distance = 0.0


def find_cone():
    """コーンの中心の列を -1〜1 で返す。見えなければ None"""
    image = rc.camera.get_color_image()
    if image is None:
        return None
    contours = rc_utils.find_contours(image, CONE[0], CONE[1])
    contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)
    if contour is None:
        return None
    center = rc_utils.get_contour_center(contour)     # (行, 列)
    half = rc.camera.get_width() / 2
    return (center[1] - half) / half


def cone_distance(scan, x):
    """カメラで見たコーンの向きの ±5° で、いちばん近い点に近い点だけを平均した距離（6-6 の方法）"""
    a = x * HALF_FOV                                  # コーンの向き（度。右が＋）
    i = round(a * len(scan) / 360)                    # その向きの点の番号
    near = scan[np.arange(i - 10, i + 11) % len(scan)]   # ±5°（21 点）。0° をまたいでもよいように % を使う
    near = near[near > 0]                             # 0.0（測れなかった点）は使わない
    if len(near) == 0:
        return 0.0
    closest = near.min()
    return float(near[near < closest + 5].mean())     # いちばん近い点から 5 cm 以内の点の平均


def change(new_state):
    global state, timer, good_time
    state = new_state
    timer = 0.0
    good_time = 0.0
    if state == State.PARK:
        park_pid.reset()
    print(f"{state.name} へ（コーンまで {distance:.1f} cm）")


def start():
    global state, timer
    state = State.SEARCH
    timer = 0.0
    rc.drive.stop()
    print(">> コーンを探して、30 cm 手前に止まります")


def update():
    global timer, good_time, distance
    dt = rc.get_delta_time()
    timer += dt
    x = find_cone()
    if x is not None:
        distance = cone_distance(rc.lidar.get_samples(), x)
        error = distance - TARGET

    # どの状態でも：コーンを見失ったら、探しなおす
    if x is None and state != State.SEARCH:
        change(State.SEARCH)

    speed, angle = 0.0, 0.0
    if state == State.SEARCH:
        speed, angle = 0.2, 1.0                        # ゆっくり右回りの円をえがく
        if x is not None:
            steer_pid.reset()
            change(State.APPROACH)
    elif state == State.APPROACH:
        angle = steer_pid.update(x, dt)
        speed = rc_utils.clamp(0.01 * error, -0.3, 0.5)
        if abs(error) < PARK_ZONE:
            change(State.PARK)
    elif state == State.PARK:
        angle = steer_pid.update(x, dt)
        speed = park_pid.update(error, dt)
        if abs(error) >= 2 * PARK_ZONE:
            change(State.APPROACH)
        else:
            good_time = good_time + dt if abs(error) < DONE else 0.0
            if good_time > HOLD_TIME:
                change(State.PARKED)
    elif state == State.PARKED:
        if abs(error) > 3 * DONE:
            change(State.PARK)

    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    print(f"{state.name:8}　コーンまで {distance:5.1f} cm")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

- APPROACH の速さは、`0.01 × ずれ` を −0.3〜0.5 にしたものです（P だけ）。遠くでは 0.5 で速く近づき、近づくと遅くなります
- PARK では、6-21 の PI（`i_zone` つき）で合わせます。PARK に入ったときに `park_pid.reset()` して、前の PARK でためた積分を消します
- `good_time` は、ずれが `DONE`（1 cm）より小さい状態が続いた時間です。LIDAR の値のばらつきで、たまたま1コマだけ 1 cm 以内になっても、PARKED にはなりません

説明用のモデルで、「右の遠く」にコーンを置いて走らせると、次のように表示されました。

```text
>> コーンを探して、30 cm 手前に止まります
APPROACH へ（コーンまで 382.4 cm）
APPROACH　コーンまで 382.4 cm
APPROACH　コーンまで 338.1 cm
APPROACH　コーンまで 258.2 cm
APPROACH　コーンまで 190.7 cm
APPROACH　コーンまで 115.0 cm
PARK へ（コーンまで 52.3 cm）
PARK    　コーンまで  52.3 cm
PARK    　コーンまで  38.4 cm
PARK    　コーンまで  42.7 cm
PARK    　コーンまで  44.2 cm
PARK    　コーンまで  42.8 cm
PARKED へ（コーンまで 41.7 cm）
PARKED  　コーンまで  41.8 cm
PARKED  　コーンまで  41.8 cm
```

![左は、スタートの位置で、少し左の遠くにあるコーンを見たカメラの画像。灰色の壁と床の境目のあたりに、青い台形のコーンが画面の左寄りに写っている。右は、6 つの置き方で走らせた道すじを上から見た図。遠い（250 cm 先）、近い（45 cm 先）、とても遠い（500 cm 先）、少し左、右の遠く、近くて左のそれぞれで、車はコーンのほうへ向きを変えながら近づき、コーンの手前で止まっている。どれも成功で、かかった時間は 3.8〜10.6 秒](/images/racecar-neo-jp/7-3/fig1-cases.png)
*図1　6 つの置き方で、コーンの手前に止まる（説明用の簡単なモデル）*

![「右の遠く」のスタートでの、画面に表示されるコーンまでの距離の時間変化。0 秒で APPROACH になり、330 cm からほぼ一定の速さで近づく。5 秒で PARK になり、少し行き過ぎて 26 cm まで近づいてから、ゆっくりもどって 32 cm まで離れ、9.5 秒ごろに 30 cm の近くで止まって PARKED になる。拡大図では、緑の帯（30 ± 1 cm）の中に落ち着いている](/images/racecar-neo-jp/7-3/fig2-states.png)
*図2　「右の遠く」のスタート：コーンまでの距離と、状態の切りかわり*

説明用のモデルで、コーンの置き方を6通りにして走らせました。コースの置き方は、シミュレータの自動採点のコースをまねて、この本で決めたものです。

| 置き方 | コーンの位置（スタートから） | 成功するまで |
|---|---|---|
| 遠い | 250 cm 前 | 7.2 秒 |
| 近い | 45 cm 前 | 3.8 秒 |
| とても遠い | 500 cm 前 | 10.6 秒 |
| 少し左 | 200 cm 前、60 cm 左 | 6.6 秒 |
| 右の遠く | 350 cm 前、200 cm 右 | 9.5 秒 |
| 近くて左 | 80 cm 前、40 cm 左 | 4.0 秒 |

「成功」は、表示の距離が 30 ± 1 cm で、車の速さがほぼ 0 になったときです。LIDAR のばらつきを変えて、さらに3回ずつ走らせても、24 回すべて成功しました（どれも 15 秒以内）。「近い」では、はじめからコーンが近すぎるので、APPROACH と PARK で後ろへ下がって合わせています。コーンを置かずに走らせると、SEARCH のまま円をえがき続け、プログラムは止まりませんでした。

## ④ 数式・コード

### 色のかたまりの面積で、距離を見積もる

ひな形の `update_contour()` は、コーンの輪郭の中心 `contour_center` と、面積 `contour_area` を求めるようになっています。コーンまでの距離 $d$ が2倍になると、画像の中のコーンは、たても横も半分になるので、面積は $\frac{1}{4}$ になります。

$$
\text{面積} \propto \frac{1}{d^2}, \qquad d \approx \frac{k}{\sqrt{\text{面積}}}
$$

$k$ は、ある距離で面積を1回測れば決まります。LIDAR がほかの物を見てしまうときの確かめや、LIDAR が使えないときの代わりに使えます。ただし、コーンが画面のはしで切れていると、面積が小さくなって、遠く見えてしまいます。

### 画面の下を切りとる

ひな形の Part 2 には、「画像を画面の下のほうに切りとる」とあります（6-2 の `crop`）。コーンより上に写る、コーンと似た色の物（部屋の飾りなど）を、見のがすためです。切りとる行の範囲は、近くのコーンのいちばん上が切れない所にしましょう。

## ⑤ つまずきポイント

### いつまでも PARKED にならない

LIDAR の値は、止まっていても 1 cm くらいばらつきます。`DONE` を小さくしすぎると、なかなか「1 cm 以内が 1 秒続く」になりません。`cone_distance()` のように、近い点の平均を使うと、ばらつきが小さくなります。

### 目標のすぐ手前で止まって、動かない

車は、speed がとても小さいと、摩擦で動かないことがあります（6-11）。6-21 で見たように、PI の I が効くまで時間がかかります。PARK の `ki` を少し大きくするか、`i_zone` の中でだけ I をためるようにします。

### コーンの向きが 0° 付近で、エラーになる

`rc_utils.get_lidar_closest_point(scan, (始まり, 終わり))` の窓で、始まりの角度が 359.75° 以上 360° 未満になると、ライブラリの中で空の配列を調べることになり、エラーで止まります。コーンのほぼ正面の向き（−0.25°〜0°）を、小数のまま `% 360` して渡すと、この範囲に入ることがあります。この回の `cone_distance()` のように、番号を `%` で計算して自分で取り出すか、窓の角度を整数にしておきましょう。

### 見つけたコーンがすぐ見えなくなる

SEARCH の円が大きすぎると、コーンが一瞬しか画面に入りません。SEARCH の speed を小さくするか、ハンドルをいっぱいに切りましょう。

## ⑥ 確認問題

**問1**　コーンの中心が、列 480 に写りました。コーンは、正面から右へ何度の向きにありますか（横の視野の半分は 34.7°）。

:::details 答え
$(480 - 320) \div 320 \times 34.7 \approx 17.4°$（右）です。
:::

**問2**　`TARGET = 42.5` で PARKED になったとき、シミュレータの表示は 28.6 cm でした。`TARGET` をいくつに直しますか。

:::details 答え
1.4 cm 近すぎるので、`TARGET` を 1.4 大きくして、43.9 にします。
:::

**問3**　Lab G の条件「終わりの状態を作ってはいけない」を、このプログラムはどうやってみたしていますか。

:::details 答え
PARKED になっても、距離が 3 cm 以上ずれたら PARK にもどり、コーンを見失ったら SEARCH にもどります。どの状態からも、ほかの状態へ出る道があるので、「ここに入ったら二度と出ない」終わりの状態はありません。
:::

## ⑦ 原典

- Lab G の課題（Expected Outcome、深度カメラは使わない、ボタンの表示、`update_contour()` の Part 2）：[racecar-neo-prereq-labs](https://github.com/MITRacecarNeo/racecar-neo-prereq-labs) の `labs/lab_g/lab_g.py`
- Lab G のレベルと自動採点のコース・点数・制限時間：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `LevelCollection.cs`
- 合格の条件（表示の距離が 30 cm から 1 cm 以内、ほぼ止まっている）と、距離の測り方（コーンの表面から車の表面まで）：同じく `DistanceConeObjective.cs`・`DistanceCone.cs`・`Prefabs/Obstacles/Autograder/DistanceConeObjective.prefab`・`Constants.cs`
- カメラの視野（横 69.4°、たて 42.5°）：同じく `CameraModule.cs`
- `get_lidar_closest_point()` の窓の扱い：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）

`cone_park.py`・図1・図2と表の数字は、この本で作った説明用の簡単なモデル（上から見た2次元の車、コーンを写すカメラ、LIDAR の計算）によるものです。
