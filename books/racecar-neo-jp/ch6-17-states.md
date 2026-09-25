---
title: "6-17 状態で切り替える"
free: true
---

6-16 の「真ん中を走る」は、両側に壁があるときにしか使えません。ところが、Lab I のコースには、入り口や曲がり角のように、片側の壁がとぎれる所があります。Lab I の Expected Outcome にも、「右の壁だけ見える、左の壁だけ見える、両側に見える、で、違う状態をもってよい」とありました（6-4）。この回では、見えている壁に合わせて、走り方を**切りかえる**プログラムを作ります。

## ① この回でできるようになること

1. 見えている壁から、今の「状態」を決められる
2. 状態ごとに、ずれと向きの求め方を切りかえられる
3. 状態がせわしなく切りかわる（チャタリング）のを、「しばらく続いたら切りかえる」ことで防げる
4. 切りかえるときに、PID の積分と目標の距離をどうするかを説明できる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| State | 状態 | 今、どの走り方をしているか。この回では4つ |
| Transition | 遷移（切りかえ） | ある状態から、別の状態にうつること |
| Chattering | チャタリング | 2つの状態の間を、せわしなく行ったり来たりすること |
| Hysteresis | ヒステリシス | すぐには切りかえず、少し余裕をもたせて、行ったり来たりを防ぐしくみ |

## ③ 本文

### 片側の壁がとぎれると、何が起きるか

説明用の簡単なモデルで、幅 150 cm の通路の途中に、左の壁がない所（奥に部屋がある）、右の壁がない所、両側の壁がない所（広い部屋）をつくり、6-16 の「真ん中を走る」プログラムで走らせました。すると、左の壁がとぎれた所で、車は左へ曲がりこみ、部屋の奥の壁にぶつかりました（図1の灰色）。

壁がとぎれる少し手前では、左ななめ前の光線だけが、とぎれた先の遠くまで届きます。そのため、左の壁がとても遠くへ離れていくように見え、「真ん中」が左にずれたと思ってしまうのです。6-16 で `walls.py` に入れた `MAX_ANGLE` のしかけで、壁がとぎれたことはわかるようになっています。問題は、**わかったあと、どう走るか**です。

### 4つの状態

見えている壁によって、次の4つの**状態**に分け、状態ごとに走り方を変えます。

| 状態 | 見えている壁 | 走り方 | ずれ | 向き |
|---|---|---|---|---|
| BOTH | 両側 | 真ん中を走る（6-16） | $(d_R - d_L)/2$ | $(\alpha_R - \alpha_L)/2$ |
| RIGHT | 右だけ | 右の壁から一定の距離 | $d_R - \text{target\_right}$ | $\alpha_R$ |
| LEFT | 左だけ | 左の壁から一定の距離 | $\text{target\_left} - d_L$ | $-\alpha_L$ |
| NONE | どちらもない | まっすぐ | ― | ― |

LEFT のずれと向きに－がついているのは、6-7 の「左の壁のときは符号が逆」と同じ理由です。こうしておくと、どの状態でも「ずれが＋なら右へ切る」ので、1つの PID をそのまま使えます。

### 切りかえるときに気をつけること

**1. すぐには切りかえない**

壁の見え方は、ばらつきや、壁のとぎれ目で、1コマごとに変わることがあります。見えたとたんに切りかえると、BOTH と RIGHT の間を、せわしなく行ったり来たりします。これを**チャタリング**といいます。モデルで、見え方が変わったらすぐに切りかえるようにすると、左の壁のとぎれ目で 20 回も切りかわり、車は部屋に曲がりこんで、ぶつかりました（図1の青）。

そこで、**新しい見え方が `HOLD` コマ続いたら、切りかえる**ことにします。このように、すぐには切りかえない余裕をもたせるしくみを、**ヒステリシス**といいます。

**2. 切りかえたら、PID の積分を消す**

BOTH でためた積分は、「真ん中からのずれ」をためたものです。RIGHT では、ずれの意味が「右の壁からの距離のずれ」に変わるので、ためた積分はそのまま使えません。切りかえたら、`reset()` で消します。

**3. 片側だけになったら、そのときの距離を保つ**

BOTH から RIGHT に切りかえたとき、目標を「右の壁から 50 cm」にすると、幅 150 cm の通路の真ん中（右から 75 cm）を走っていた車は、急に右へ 25 cm 寄ろうとします。壁がまた両側に見えるようになると、今度は真ん中にもどろうとして、道すじがくねくねします。そこで、**切りかえたときの距離を、そのまま目標にします**。

### やってみよう：状態を切りかえて走る

`walls.py`（6-16）と `pid.py`（6-12）を同じフォルダに置いて、次のプログラムを作ります。

```python:wall_follow_states.py
"""
wall_follow_states.py
見えている壁に合わせて、走り方を切りかえる（6-17）。
両側が見える：真ん中を走る　右だけ：右の壁から一定の距離　左だけ：左の壁から一定の距離　どちらも見えない：まっすぐ
walls.py と pid.py を同じフォルダに置いて使う。
"""

import sys
from enum import IntEnum

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from pid import PID
from walls import side_wall

rc = racecar_core.create_racecar()

SPEED = 0.5       # 走る速さ（一定）
HOLD = 10         # 新しい状態がこのコマ数だけ続いたら、切りかえる


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


def seen_state(right, left):
    """見えている壁から、今の状態を決める"""
    if right is not None and left is not None:
        return State.BOTH
    if right is not None:
        return State.RIGHT
    if left is not None:
        return State.LEFT
    return State.NONE


def start():
    global state, candidate, count
    rc.drive.stop()
    steer_pid.reset()
    state = State.BOTH
    candidate = State.BOTH
    count = 0
    print(">> 見えている壁に合わせて、走り方を切りかえます")


def update():
    global state, candidate, count, target_right, target_left

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

    rc.drive.set_speed_angle(SPEED, angle)


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
```

- `class State(IntEnum)`：4つの状態に、名前をつけています。`State.RIGHT` のように名前で書けるので、`state == 1` と書くより、読みやすく、まちがえにくくなります。`state.name` で、名前（`"RIGHT"`）を文字として取り出せます。ライブラリの `rc.controller.Button`（2-1）も、この書き方で作られています
- `candidate` と `count`：今とちがう見え方（`candidate`）が、何コマ続いているかを数えます。とちゅうで別の見え方になったら、数え直します
- 切りかえを待っている間に、今の状態に必要な壁が見えないときは、まっすぐ走ります

説明用の簡単なモデルで、図1の通路を走らせると、次のように表示されました。

```text
>> 見えている壁に合わせて、走り方を切りかえます
状態を RIGHT にした
状態を BOTH にした
状態を RIGHT にした
状態を BOTH にした
状態を LEFT にした
状態を BOTH にした
状態を NONE にした
状態を BOTH にした
状態を NONE にした
```

はじめの RIGHT → BOTH → RIGHT は、左の壁がとぎれる所で、見え方が一度ゆれたためです（`HOLD` の 10 コマより長くゆれたので、切りかわりました）。そのあとは、左の壁がない所で RIGHT、右の壁がない所で LEFT、広い部屋で NONE と、通路に合わせて切りかわっています。最後の NONE は、通路の終わりです。

![左は、入り口や広い部屋のある通路を上から見た図。幅 150 cm の通路の途中に、左の壁がない所（奥 450 cm に壁のある部屋）、右の壁がない所、両側の壁がない広い部屋がある。両側の真ん中だけを走る 6-16 のプログラム（灰色）は、左の壁がない所で左へ曲がりこみ、部屋の奥の壁にぶつかる。状態をすぐ切りかえるプログラム（青、HOLD 1）も、同じ所で左へ曲がりこんで、ぶつかる。HOLD 10 で状態を切りかえるプログラム（オレンジ）は、最後までまっすぐ、通路の真ん中を走る。右は、HOLD 10 のときの状態を、通路にそって色で表したもの。下から、BOTH、RIGHT（左の壁がない所）、BOTH、LEFT（右の壁がない所）、BOTH、NONE（広い部屋）、BOTH、NONE（通路の終わり）](/images/racecar-neo-jp/6-17/fig1-states.png)
*図1　入り口や広い部屋のある通路を走る（speed 0.5、説明用の簡単なモデル）*

`HOLD = 10` のプログラムは、最後まで、通路の真ん中から 3 cm 以内を走りました。

### HOLD の決め方

`HOLD` を大きくすると、チャタリングは起きにくくなりますが、本当に壁がとぎれたときに、切りかわるのが遅れます。speed 0.5（モデルでは 1 秒に約 75 cm）なら、10 コマ（約 0.17 秒）の間に、約 12 cm 進みます。壁がとぎれてから 12 cm くらい進むまでは、前の状態のままです。速く走るときや、短いとぎれ目が多いコースでは、この距離を考えて決めましょう。

## ④ 数式・コード

### 状態をまとめて表す

この回のプログラムは、状態と、状態の切りかわり方を、次のように決めています。

- 状態は4つ：BOTH、RIGHT、LEFT、NONE
- 切りかわる条件は、どの状態からでも同じ：「見え方が、HOLD コマ続けて、今とちがう状態を示した」
- 切りかわるときにすること：積分を消す、片側になるなら、そのときの距離を目標にする

このように、「どんな状態があって、何が起きたら、どの状態にうつるか」をはっきり決めたものを**ステートマシン**（状態機械）といいます。第7章で、くわしく学びます。

### ずれの符号をそろえる

LEFT の状態で、ずれを `target_left - left`、向きを `-left_angle` にしたのは、「左の壁から遠すぎる（ずれ＋）なら左へ」ではなく、「ずれが＋なら右へ」にそろえるためです。

$$
\text{ずれ}_{\text{LEFT}} = \text{target\_left} - d_L
$$

左の壁に近すぎる（$d_L$ が小さい）と、ずれは＋になり、右へ（左の壁から離れる向きに）切ります。符号をそろえておくと、1つの PID を、どの状態でも同じように使えます。

## ⑤ つまずきポイント

### 切りかえるたびに、ハンドルがぴくっと動く

`reset()` で積分と記録を消すと、D の部分が使う記録もなくなります。このプログラムでは、D に壁の向き（`rate=`）を渡しているので問題ありませんが、6-9 のように記録から速さを求めている場合は、切りかえの直後の数コマは D がはたらきません。

### 広い部屋で、まっすぐ走れずに曲がっていく

NONE の状態では、ハンドルを 0 にしています。6-11 のハンドルのくせがある車では、少しずつ曲がっていきます。長い NONE の区間があるコースでは、LIDAR で見える遠くの壁や、IMU（5-5）の向きを使って、まっすぐを保つ工夫が必要です。

### 片側だけのとき、壁に近すぎる距離を保ってしまう

RIGHT や LEFT に切りかえたとき、たまたま壁に近い所を走っていると、その近い距離を保ってしまいます。目標の距離に、最小と最大の値をつけておくと安心です（たとえば `target_right = rc_utils.clamp(right, 40, 100)`）。

## ⑥ 確認問題

**問1**　右の壁まで 70 cm、左の壁は見えません（`None`）。状態は何ですか。

:::details 答え
RIGHT です（HOLD コマ続けば、切りかわります）。
:::

**問2**　LEFT の状態で、`target_left = 60`、左の壁までが 45 cm でした。ずれはいくつで、どちらに切りますか。

:::details 答え
$60 - 45 = +15$ です。＋なので右へ（左の壁から離れる向きに）切ります。
:::

**問3**　HOLD を 1 にすると、どんなことが起きますか。

:::details 答え
見え方がゆれるたびに、状態がせわしなく切りかわります（チャタリング）。そのたびに積分が消え、目標の距離も変わるので、走りが乱れます。
:::

## ⑦ 原典

- Lab I の課題（右だけ・左だけ・両側で、状態を分けてよい）：**Lab I - Wall Follower**（`labs/lab_i/lab_i.py`）：[racecar-neo-prereq-labs](https://github.com/MITRacecarNeo/racecar-neo-prereq-labs)（MIT License）
- `IntEnum`：Python の標準ライブラリ [enum](https://docs.python.org/ja/3/library/enum.html)。`Button` の定義：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `controller.py`（GPL-3.0）

図1と `wall_follow_states.py` の表示は、この本で作った説明用の簡単なモデル（上から見た2次元の車と壁、LIDAR の計算）によるものです。
