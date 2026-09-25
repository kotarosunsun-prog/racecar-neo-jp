---
title: "6-20 タイムアタック"
free: true
---

Lab I には、ゴールまでの時間を測る**レースモード**と、走りきった時間で点数が増えたり減ったりする**タイムボーナス**があります（6-4）。この回では、6-19 のプログラムの設定を変えながら、速く、しかも確実に走るための**調整の進め方**を学びます。

## ① この回でできるようになること

1. レースモードと自動採点で、何がどう測られるかを説明できる
2. 設定を1つずつ変えて、何回も走らせて比べられる
3. 速さと余裕（壁との距離）のかね合いを考えて、設定を選べる
4. 区間ごとの時間から、どこで時間がかかっているかを見つけられる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Time attack | タイムアタック | できるだけ短い時間でゴールすることをめざして走ること |
| Checkpoint | チェックポイント | コースの途中にある、通過を記録する場所 |
| Split time | 区間タイム | チェックポイントからチェックポイントまでにかかった時間 |
| Margin | 余裕 | ぶつかるまでに、どれだけのゆとりがあるか |
| Trade-off | かね合い | 一方をよくすると、もう一方が悪くなる関係 |

## ③ 本文

:::message
この回の数字は、6-19 と同じ、この本の説明用モデル（速い車）と、6-18 のコースで測ったものです。シミュレータの Lab I のコースとは、車もコースもちがいます。**シミュレータでの設定は、この回の進め方で、自分で探してください。**
:::

### Lab I では、時間がこう測られる

シミュレータの **Lab I: Wall Follower** には、チェックポイントが4つあります。モードごとに、時間の測られ方と、使える機能がちがいます。

| モード | 時間の測られ方 | 調整に使える機能 |
|---|---|---|
| Exploration（探索） | 測らない | Tab キーで次のチェックポイントへ、Caps Lock キーで今のチェックポイントへもどる |
| Race（レース） | スタートからゴールまでの時間と、チェックポイントごとの区間タイムを表示する。いちばんよい時間が、区間ごとにも記録される | ― |
| Autograder（自動採点） | Full Course と Challenge: Organic で、走りきった時間からタイムボーナスが決まる | ― |

気をつけることが3つあります。

- **ぶつかったら終わり**：どのモードでも、壁にふれると失敗です。自動採点では、そこでそのコースが終わり、タイムボーナスはもらえません
- **タイムボーナスは、区切りで決まる**：Full Course は、20 秒以内なら +1、30 秒以内なら +0.5 です（6-4）。同じ区切りの中なら、0.5 秒速くしても点数は変わりません
- **レースモードでは、コントローラーの入力がプログラムに届かない**：ボタンは「押されていない」、スティックとトリガーは 0 として届きます。6-14 の `wall_follow_tune.py` のように、ボタンでゲインを変えるプログラムは、Exploration で使いましょう

:::message
左の Alt キーを押すたびに、シミュレータの時間の進みが半分（スローモーション）になり、右の Alt キーで2倍にもどせます（1倍まで）。速い車が曲がり角でどう動いているかを、目で確かめるときに便利です。
:::

### まず、記録を取れるようにする

調整では、「どの設定で走らせたか」と「結果はどうだったか」を、必ずいっしょに記録します。6-19 の `wall_follow_speed.py` に、次の3つを足します。

1. スタートのときに、設定（大文字の数字）を表示する
2. スタートからの時間を数える
3. いちばん近づいた物までの距離を覚えておく

```python
front = 0.0              # 正面の壁までの距離
elapsed = 0.0            # スタートからの時間（秒）
closest = 1000.0         # いちばん近づいた物までの距離（cm）
```

```python
    elapsed = 0.0
    closest = 1000.0
    print(f">> MAX_SPEED {MAX_SPEED}  MIN_SPEED {MIN_SPEED}  FRONT_TARGET {FRONT_TARGET}  "
          f"FRONT_LIMIT {FRONT_LIMIT}  KF {KF}  速さの KP {speed_pid.kp}")
```

```python
    # 記録：スタートからの時間と、いちばん近づいた物までの距離
    elapsed += dt
    _, near = rc_utils.get_lidar_closest_point(scan)
    closest = min(closest, near)
```

```python
def update_slow():
    print(f"{elapsed:5.1f} 秒　speed {speed:.2f}　いちばん近づいた物まで {closest:5.1f} cm")
```

- `get_lidar_closest_point(scan)` は、窓を指定しないと、まわり 360° の中でいちばん近い点の（角度、距離）を返します（5-3）。距離だけを使うので、角度は `_` で受け取って捨てます
- この距離は、LIDAR から物までの距離です。車の横はばの分だけ、車の外側と壁のすき間はもっとせまくなります。設定どうしを比べるための目安として使います

:::details wall_follow_race.py の全体
```python:wall_follow_race.py
"""
wall_follow_race.py
6-19 の wall_follow_speed.py に、タイムアタックの記録を足したもの（6-20）。
・スタートのときに、設定（大文字の数字）を表示する
・スタートからの時間と、いちばん近づいた物までの距離を、1秒ごとに表示する
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
front = 0.0              # 正面の壁までの距離
elapsed = 0.0            # スタートからの時間（秒）
closest = 1000.0         # いちばん近づいた物までの距離（cm）


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
    global state, candidate, count, speed, elapsed, closest
    rc.drive.stop()
    steer_pid.reset()
    speed_pid.reset()
    speed = MIN_SPEED
    state = State.BOTH
    candidate = State.BOTH
    count = 0
    elapsed = 0.0
    closest = 1000.0
    print(f">> MAX_SPEED {MAX_SPEED}  MIN_SPEED {MIN_SPEED}  FRONT_TARGET {FRONT_TARGET}  "
          f"FRONT_LIMIT {FRONT_LIMIT}  KF {KF}  速さの KP {speed_pid.kp}")


def update():
    global state, candidate, count, target_right, target_left, speed, front, elapsed, closest

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

    # 記録：スタートからの時間と、いちばん近づいた物までの距離
    elapsed += dt
    _, near = rc_utils.get_lidar_closest_point(scan)
    closest = min(closest, near)

    # 4. 正面の壁までの距離から、速さを決める
    speed = speed_pid.update(front - FRONT_TARGET, dt)

    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    print(f"{elapsed:5.1f} 秒　speed {speed:.2f}　いちばん近づいた物まで {closest:5.1f} cm")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```
:::

説明用のモデルで走らせると、次のように表示されました（ゴールを過ぎるまで）。

```text
>> MAX_SPEED 1.0  MIN_SPEED 0.3  FRONT_TARGET 60  FRONT_LIMIT 200  KF 0.02  速さの KP 0.005
  0.0 秒　speed 1.00　いちばん近づいた物まで  72.1 cm
  1.0 秒　speed 1.00　いちばん近づいた物まで  70.5 cm
  2.0 秒　speed 0.64　いちばん近づいた物まで  67.2 cm
  3.0 秒　speed 0.92　いちばん近づいた物まで  59.8 cm
  4.0 秒　speed 0.74　いちばん近づいた物まで  57.8 cm
  5.0 秒　speed 0.30　いちばん近づいた物まで  57.8 cm
  6.0 秒　speed 1.00　いちばん近づいた物まで  49.6 cm
  7.0 秒　speed 0.92　いちばん近づいた物まで  49.5 cm
  8.0 秒　speed 0.30　いちばん近づいた物まで  49.5 cm
  9.0 秒　speed 0.72　いちばん近づいた物まで  49.5 cm
 10.0 秒　speed 0.54　いちばん近づいた物まで  49.5 cm
 11.0 秒　speed 0.31　いちばん近づいた物まで  39.6 cm
 12.0 秒　speed 1.00　いちばん近づいた物まで  33.7 cm
 13.0 秒　speed 0.30　いちばん近づいた物まで  33.7 cm
 14.0 秒　speed 0.98　いちばん近づいた物まで  33.7 cm
 15.0 秒　speed 0.61　いちばん近づいた物まで  33.7 cm
 16.0 秒　speed 0.57　いちばん近づいた物まで  33.7 cm
 17.0 秒　speed 1.00　いちばん近づいた物まで  33.7 cm
```

ゴールまでの時間は、レースモードの表示で確かめます。いちばん近づいた距離は、シミュレータには表示されないので、このプログラムの表示を記録します。

### 1回だけでは決められない

同じプログラムを、LIDAR のばらつきだけを変えて 20 回走らせると、ゴールまでの時間は 16.5〜17.8 秒と、1.3 秒もちがいました。いちばん近づいた距離も、回ごとに変わります。シミュレータの LIDAR にも、2% ほどの誤差が入ります（6-6）。1回だけ速かった設定を選ぶと、本番では遅かったり、ぶつかったりします。**1つの設定を、何回か走らせてから比べましょう。**

### 1つずつ変えて比べる

6-19 のプログラム（MAX_SPEED 1.0、FRONT_TARGET 60、FRONT_LIMIT 200、速さの KP 0.005）を「もと」にして、数字を**1つだけ**変え、それぞれ 20 回ずつ走らせました。

| 変えた所 | 成功 | 平均〔秒〕 | いちばん遅い〔秒〕 | いちばん近づいた〔cm〕 |
|---|---|---|---|---|
| もと（6-19） | 20/20 | 17.2 | 17.8 | 27.0 |
| FRONT_LIMIT 150 | 3/20 | 20.0 | 20.5 | 11.3 |
| FRONT_LIMIT 250 | 20/20 | 16.2 | 17.4 | 16.2 |
| FRONT_LIMIT 300 | 20/20 | 16.7 | 17.6 | 26.6 |
| FRONT_TARGET 30 | 20/20 | 15.5 | 16.5 | 14.4 |
| FRONT_TARGET 100 | 17/20 | 20.4 | 21.3 | 11.3 |
| 速さの KP 0.007 | 19/20 | 15.2 | 16.0 | 11.8 |
| MAX_SPEED 0.9 | 20/20 | 17.9 | 18.5 | 25.2 |

「平均」と「いちばん遅い」は、ぶつからなかった回だけで計算しています。「いちばん近づいた」は、20 回の中でいちばん壁に近づいたときの、車の中心から壁までの距離です。このモデルの車は、半径 12 cm の円なので、12 cm より近づくとぶつかります。

表から、次のことがわかります。

- **速くすると、余裕が減りやすい**：FRONT_TARGET を 30 にすると、平均 1.7 秒速くなりましたが、壁まで 14.4 cm まで近づきました。20 回とも成功しましたが、ぎりぎりです
- **遅くしても、安全になるとは限らない**：FRONT_TARGET を 100 にすると、遅くなったうえに、3回ぶつかりました。記録を調べると、広い所の先の、右へ 90° 曲がる角で、左へ曲がってぶつかっていました。ゆっくり近づくあいだに車が少し左を向き、左ななめ前の光線が、広い所の奥のすみまで届いたので、`open_side()` が「左が開いている」と判断したのです。6-18 の⑤で見た、`open_side()` の弱点です
- **速さも余裕も、よくなることもある**：FRONT_LIMIT を 300 にして、正面の壁が遠いうちから曲がりはじめるようにすると、余裕をほとんど減らさずに、平均 0.5 秒速くなりました

![6-18 のコースで、設定ごとに 20 回ずつ走らせた結果を、横軸にゴールまでの平均の時間、縦軸に 20 回の中で壁にいちばん近づいた距離をとって表した図。左ほど速く、上ほど余裕がある。もと（6-19）は 17.2 秒・27.0 cm、FRONT_LIMIT 300 は 16.7 秒・26.6 cm、FRONT_LIMIT 300 と FRONT_TARGET 50 の組み合わせはオレンジの点で 16.3 秒・22.0 cm。FRONT_TARGET 30 や FRONT_LIMIT 250 は速いが 15 cm 前後まで近づく。速さの KP 0.007 と、FRONT_LIMIT 300 と FRONT_TARGET 40 の組み合わせは1回ずつ、FRONT_TARGET 100 は3回、FRONT_LIMIT 150 は17回ぶつかり、赤いばつ印で、12 cm より下のぶつかる範囲にある。20 cm に余裕の目安の点線がある](/images/racecar-neo-jp/6-20/fig1-tradeoff.png)
*図1　速さと余裕（どの設定も 20 回ずつ、速い車、説明用の簡単なモデル）*

### よかった変更を組み合わせる

次に、よかった FRONT_LIMIT 300 に、ほかの変更を1つずつ組み合わせました。

| 変えた所 | 成功 | 平均〔秒〕 | いちばん遅い〔秒〕 | いちばん近づいた〔cm〕 |
|---|---|---|---|---|
| FRONT_LIMIT 300 ＋ FRONT_TARGET 40 | 19/20 | 16.1 | 17.1 | 11.6 |
| FRONT_LIMIT 300 ＋ FRONT_TARGET 50 | 20/20 | 16.3 | 17.9 | 22.0 |
| FRONT_LIMIT 300 ＋ 速さの KP 0.006 | 20/20 | 15.9 | 17.3 | 12.9 |

FRONT_TARGET は、30 にしたときは 20 回とも成功しましたが、FRONT_LIMIT 300 と組み合わせて 40 にすると、1回ぶつかりました。**1つずつならよかった変更でも、組み合わせるとよいとは限りません**。組み合わせたら、また何回も走らせて確かめます。

### どれを選ぶか

図1で、20 回とも成功し、しかも 20 cm 以上の余裕がある設定（点線より上の青とオレンジの点）の中で、いちばん左にあるのは、オレンジの **FRONT_LIMIT 300 ＋ FRONT_TARGET 50** です。もとより平均 0.9 秒速く、余裕は 22.0 cm あります。

図1のいちばん左の点（速さの KP 0.007）は、平均 15.2 秒でいちばん速いのですが、20 回に1回ぶつかりました。自動採点は1回きりです。ぶつかればタイムボーナスはもらえません。このコースでは、どの設定でも 20 秒以内なので、タイムボーナスの区切りは同じです。**区切りが変わらないなら、速さより、確実に走りきることを選びます。**

「20 cm」の目安は、この本で決めたものです。シミュレータや実物の車では、自分で目安を決めましょう。実物の車は、床やタイヤ、電池の減り具合で動きが変わるので、シミュレータより大きな余裕が必要です。

### 区間ごとの時間で、遅い所を見つける

レースモードでは、チェックポイントごとの区間タイムが表示されます。説明用のコースも、4つの区間に分けて、区間ごとの時間を比べました（図2）。

![3つの走り方の区間ごとの時間を、横の帯グラフで表した図。区間は、① 45° の角、② 90° の角2つ、③ せまい所・広い所、④ 90° の角2つとゴール。ずっと speed 0.6 は、5.3、5.3、4.5、4.4 秒で合計 19.5 秒。もと（6-19）は、3.7、5.4、3.6、4.2 秒で合計 16.8 秒。FRONT_LIMIT 300 と FRONT_TARGET 50 の組み合わせは、3.9、4.5、3.9、3.1 秒で合計 15.3 秒](/images/racecar-neo-jp/6-20/fig2-splits.png)
*図2　区間ごとの時間（1回目の走り、説明用の簡単なモデル）*

- 6-19 の速さの PID は、まっすぐな所が長い区間 ① と ③ で速くなりましたが、90° の角が2つ続く区間 ② では、ずっと speed 0.6 と変わりませんでした
- FRONT_LIMIT 300 ＋ FRONT_TARGET 50 は、90° の角のある区間 ② と ④ で速くなりました

このように、区間ごとに見ると、**どこで時間がかかっているか**と、**変更がどこに効いたか**がわかります。シミュレータでは、遅い区間を見つけたら、Exploration で Tab キーと Caps Lock キーを使って、その区間だけを何回も練習できます。

### タイムアタックの進め方

1. **まず、確実に走りきる**：遅めの設定で、Lab I の自動採点のすべてのコース（45 Degree、90 Degree、Tight、Posts、Full Course）を走りきれることを確かめます
2. **変える数字を、プログラムの上にまとめる**：`MAX_SPEED` や `FRONT_LIMIT` のように、大文字の名前にしておきます
3. **1回に1つだけ変える**：2つ同時に変えると、どちらが効いたのかわかりません
4. **1つの設定を、何回か走らせる**：たとえば5回ずつ走らせて、成功した回数・平均・いちばん遅い時間・いちばん近づいた距離を記録します
5. **区間タイムで、遅い所を探す**：遅い区間に効きそうな数字を選んで、3. にもどります
6. **余裕を残して選ぶ**：いちばん速い設定ではなく、何回走ってもぶつからない中で速い設定を選びます
7. **最後に、もう一度すべてのコースで確かめる**：Full Course に合わせた設定が、Tight や Posts でも走れるとは限りません

記録は、次のような表にしておくと、あとで見返せます。

| 日付 | 変えた所 | 成功 | 平均〔秒〕 | いちばん遅い〔秒〕 | いちばん近づいた〔cm〕 | 気づいたこと |
|---|---|---|---|---|---|---|
|  |  | ／ |  |  |  |  |

## ④ 数式・コード

### 記録から、平均とばらつきを計算する

走らせた時間を、設定ごとにリストに書き写せば、Python で平均やばらつきを計算できます。ぶつかった回は `None` と書きます。

```python:summarize_runs.py
"""
summarize_runs.py
設定ごとに記録したゴールまでの時間（秒）から、成功した回数・平均・ばらつきを計算する（6-20）。
ぶつかった回は None と書く。
"""

import statistics

runs = {
    "もと（6-19）": [16.8, 17.1, 17.6, 17.1, 17.6, 16.9, 16.8, 17.4, 17.0, 17.2],
    "速さの KP 0.007": [15.5, 14.5, 15.3, None, 15.0, 15.3, 15.3, 15.5, 14.9, 14.8],
    "FRONT_LIMIT 300 + FRONT_TARGET 50": [15.3, 17.6, 15.8, 15.6, 15.9, 15.7, 16.0, 15.7, 16.1, 17.4],
}

for name, times in runs.items():
    ok = [t for t in times if t is not None]      # ぶつからなかった回だけ
    print(name)
    print(f"  成功 {len(ok)}/{len(times)} 回")
    print(f"  平均 {statistics.mean(ok):.2f} 秒　ばらつき（標準偏差） {statistics.stdev(ok):.2f} 秒")
    print(f"  いちばん速い {min(ok)} 秒　いちばん遅い {max(ok)} 秒")
```

```text
もと（6-19）
  成功 10/10 回
  平均 17.15 秒　ばらつき（標準偏差） 0.30 秒
  いちばん速い 16.8 秒　いちばん遅い 17.6 秒
速さの KP 0.007
  成功 9/10 回
  平均 15.12 秒　ばらつき（標準偏差） 0.34 秒
  いちばん速い 14.5 秒　いちばん遅い 15.5 秒
FRONT_LIMIT 300 + FRONT_TARGET 50
  成功 10/10 回
  平均 16.11 秒　ばらつき（標準偏差） 0.77 秒
  いちばん速い 15.3 秒　いちばん遅い 17.6 秒
```

- `statistics.mean()` は平均、`statistics.stdev()` は**標準偏差**（ばらつきの大きさ）を計算します。値が平均から、だいたいどれくらい離れているかを表します
- FRONT_LIMIT 300 ＋ FRONT_TARGET 50 は、平均は速いのですが、ばらつきが大きく、いちばん遅い回はもとと同じ 17.6 秒でした。平均だけでなく、ばらつきや、いちばん遅い回も見ておきましょう

### ぶつかる見こみ

20 回のうち1回ぶつかった設定は、1回走らせたときにぶつかる見こみが、だいたい $\dfrac{1}{20} = 5\%$ です。自動採点で Full Course を1回走るなら、20 回に1回は、タイムボーナスをのがすことになります。

逆に、20 回とも成功しても、ぶつかる見こみが 0 だとはいえません。5回しか試していないなら、なおさらです。だからこそ、壁との距離の「余裕」も見ておきます。余裕が小さい設定は、試した回数では運よくぶつからなかっただけかもしれません。

## ⑤ つまずきポイント

### レースモードで、ボタンが効かない

レースモードでは、コントローラーの入力がプログラムに届きません。ボタンで設定を変えたり、スタートの合図をボタンにしたりしているプログラムは、レースモードでは動きません。ボタンを使う調整は Exploration で行い、決まった数字をプログラムに書きこんでから、レースモードで走らせましょう。

### 速い設定にしたら、ほかのコースで失敗した

Full Course に合わせて速くすると、Tight（せまい通路）や Posts（柱）で失敗することがあります。自動採点は、すべてのコースを同じプログラムで走ります。設定を変えたら、すべてのコースを走らせて確かめましょう。

### 速かった1回の結果にだまされる

1回だけ速かった設定は、たまたまかもしれません。何回か走らせて、平均といちばん遅い回を見てから決めましょう。

## ⑥ 確認問題

**問1**　ある設定を 10 回走らせたら、8回ゴールし、2回ぶつかりました。1回走らせたときにぶつかる見こみは、だいたい何 % ですか。

:::details 答え
$\dfrac{2}{10} = 20\%$ です。5回に1回はぶつかる設定なので、自動採点には使えません。
:::

**問2**　Full Course で、設定 A は 20 回とも成功し、平均 15.5 秒、いちばん近づいた距離 14.4 cm でした。設定 B は 20 回とも成功し、平均 16.3 秒、22.0 cm でした。自動採点に使うなら、どちらを選びますか。理由も答えましょう。

:::details 答え
B です。どちらも 20 秒以内なので、タイムボーナスの区切り（+1）は同じです。それなら、壁との余裕が大きい B のほうが、本番でぶつかる心配が少なくなります。
:::

**問3**　FRONT_TARGET と FRONT_LIMIT を同時に変えたら、速くなりました。この結果から、何がわかって、何がわからないでしょうか。

:::details 答え
2つをいっしょに変えると速くなることはわかりますが、どちらが効いたのか（または両方が効いたのか）はわかりません。1回に1つずつ変えて比べる必要があります。また、1回だけの結果なら、たまたま速かったのかもしれないので、何回か走らせて確かめます。
:::

## ⑦ 原典

- Lab I のチェックポイントの数（4）、Full Course と Challenge: Organic のタイムボーナス：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `LevelCollection.cs`
- レースモードの区間タイムといちばんよい時間の記録、Tab キー・Caps Lock キー・Alt キーの働き、ぶつかったときの失敗：同じく `LevelManager.cs`
- タイムボーナスが、走りきったときだけつくこと：同じく `AutograderManager.cs`
- レースモードで、コントローラーの入力がプログラムに届かないこと：同じく `PythonInterface.cs`
- `get_lidar_closest_point()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）

図1・図2・表と `wall_follow_race.py`・`summarize_runs.py` の数字は、この本で作った説明用の簡単なモデル（6-19 の速い車）によるものです。
