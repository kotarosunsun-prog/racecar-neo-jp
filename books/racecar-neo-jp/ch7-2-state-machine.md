---
title: "7-2 ステートマシンの設計"
free: true
---

6-17 では、壁の見え方で「右だけ」「左だけ」「両側」「壁なし」の4つの**状態**を切りかえました。このように、「どんな状態があって、何が起きたら、どの状態にうつるか」をはっきり決めたものを、**ステートマシン**（状態機械）といいます。この回では、ステートマシンを、まず紙の上で設計し、それからプログラムに書く手順を学びます。例として、部屋の中を、ぶつからないように走り回るプログラムを作ります。

## ① この回でできるようになること

1. やりたいことを、状態・切りかわる条件・入るときの処理に分けて設計できる
2. 状態の図（状態遷移図）と表をかける
3. `IntEnum` と `change()` 関数を使って、ステートマシンをプログラムに書ける
4. 状態ごとの時間（タイマー）を使って、「1 秒たったら次へ」のような切りかえを書ける

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| State machine | ステートマシン（状態機械） | 状態と、状態の切りかわり方を決めたしくみ |
| State | 状態 | 今どんな走り方をしているか。一度に1つだけ |
| Transition | 遷移（切りかわり） | ある状態から、別の状態にうつること |
| Condition | 条件 | 切りかわるきっかけ。「前の物が 50 cm より近い」など |
| Entry action | 入るときの処理 | ある状態に切りかわったときに、1回だけすること |
| State diagram | 状態遷移図 | 状態を箱、切りかわりを矢印でかいた図 |

## ③ 本文

### まず、紙の上で設計する

「部屋の中を、ぶつからないように走り回る」を、次の3つの状態に分けます。

| 状態 | すること | 切りかわる条件 → 次の状態 |
|---|---|---|
| FORWARD | まっすぐ進む（speed 0.5） | 前の物が 50 cm より近い → BACK |
| BACK | まっすぐ下がる（speed −0.4） | 1 秒たった、または後ろの物が 30 cm より近い → TURN |
| TURN | 空いているほうへハンドルをいっぱいに切って進む（speed 0.4） | 前の物が 50 cm より近い → BACK<br>1.5 秒たった → FORWARD |

さらに、TURN に入るときには、「右ななめ前と左ななめ前をくらべて、空いているほうを、曲がる向きに決める」を1回だけします。これが**入るときの処理**です。

表を図にすると、図1のようになります。箱が状態、矢印が切りかわりで、矢印の横に条件を書きます。

![patrol.py の状態遷移図。FORWARD（まっすぐ進む、speed 0.5）、BACK（下がる、speed −0.4）、TURN（空いているほうへ曲がる、speed 0.4）の3つの箱がある。start() から FORWARD へ矢印。FORWARD から BACK へ「前の物が 50 cm より近い」、BACK から TURN へ「1 秒たった または 後ろの物が 30 cm より近い」、TURN から FORWARD へ「1.5 秒たった」、TURN から BACK へ「前の物が 50 cm より近い」の矢印がある](/images/racecar-neo-jp/7-2/fig1-diagram.png)
*図1　patrol.py のステートマシン*

設計のときに、次のことを確かめます。

- **どの状態からも、出口があるか**：出口のない状態に入ると、ずっとそのままになります。BACK と TURN には、時間で出る出口があります
- **同じ条件で、2つの状態に行こうとしていないか**：TURN の出口は2つあるので、「前の物が近い」を先に調べる、と決めておきます
- **はじめの状態は何か**：`start()` で FORWARD にします

### プログラムに書く

設計ができたら、プログラムにします。書き方の決まった形は、次の4つです。

1. **状態の名前**：`IntEnum` で名前をつけます（6-17）
2. **今の状態とタイマー**：グローバル変数 `state` と、今の状態になってからの時間 `timer`
3. **`change()` 関数**：状態を切りかえるときは、必ずこの関数を通します。タイマーを 0 にもどし、入るときの処理をして、切りかえたことを表示します
4. **`update()` の中**：`if state == ...` で状態ごとに分け、それぞれ「すること」と「出口の条件」を書きます

```python:patrol.py
"""
patrol.py
部屋の中を、ぶつからないように走り回る（7-2）。3つの状態を、ステートマシンで切りかえる。
  FORWARD：まっすぐ進む。前に物が近づいたら BACK へ
  BACK   ：少し下がる。1 秒たつか、後ろに物が近づいたら TURN へ
  TURN   ：空いているほうへ曲がりながら進む。1.5 秒たったら FORWARD へ（前に物が近づいたら BACK へ）
"""

import sys
from enum import IntEnum

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

HALF_WIDTH = 20.0      # 前と後ろの帯の幅の半分（cm）
NEAR = 50.0            # 前の物がこれより近くなったら、止まって下がる（cm）
BACK_TIME = 1.0        # 下がる時間（秒）
TURN_TIME = 1.5        # 曲がる時間（秒）


def lidar_angles(scan):
    """LIDAR の各点の角度（ラジアン）。0 が正面、時計回り。
    点の数は len(scan) から求める（720 点なら 0.5° ずつ）"""
    return np.radians(np.arange(len(scan)) * 360 / len(scan))


class State(IntEnum):
    FORWARD = 0
    BACK = 1
    TURN = 2


state = State.FORWARD
timer = 0.0            # 今の状態になってからの時間（秒）
turn_dir = 1.0         # TURN で切るハンドルの向き（+1：右、-1：左）


def distance_in_band(scan, direction):
    """車の前（direction = +1）か後ろ（-1）の帯の中で、いちばん近い物までの距離（なければ 10000）"""
    angles = lidar_angles(scan)
    along = scan * np.cos(angles) * direction
    side = scan * np.sin(angles)
    inside = (scan > 0) & (along > 0) & (np.abs(side) < HALF_WIDTH)
    if not inside.any():
        return 10000.0
    return float(along[inside].min())


def change(new_state, scan):
    """状態を切りかえる。切りかえたときに1回だけすること（入るときの処理）も、ここに書く"""
    global state, timer, turn_dir
    state = new_state
    timer = 0.0
    if state == State.TURN:
        # 右ななめ前と左ななめ前をくらべて、空いているほうへ曲がる
        right = rc_utils.get_lidar_average_distance(scan, 45, 20)
        left = rc_utils.get_lidar_average_distance(scan, 315, 20)
        right = 1000.0 if right == 0.0 else right
        left = 1000.0 if left == 0.0 else left
        turn_dir = 1.0 if right > left else -1.0
    print(f"{state.name} へ")


def start():
    global state, timer
    state = State.FORWARD
    timer = 0.0
    rc.drive.stop()
    print(">> 部屋の中を走り回ります")


def update():
    global timer
    timer += rc.get_delta_time()
    scan = rc.lidar.get_samples()
    front = distance_in_band(scan, 1)
    back = distance_in_band(scan, -1)

    if state == State.FORWARD:
        speed, angle = 0.5, 0.0
        if front < NEAR:
            change(State.BACK, scan)
    elif state == State.BACK:
        speed, angle = -0.4, 0.0
        if timer > BACK_TIME or back < 30:
            change(State.TURN, scan)
    elif state == State.TURN:
        speed, angle = 0.4, turn_dir
        if front < NEAR:
            change(State.BACK, scan)
        elif timer > TURN_TIME:
            change(State.FORWARD, scan)

    rc.drive.set_speed_angle(speed, angle)


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
```

- `distance_in_band()` は、7-1 の `distance_ahead()` を、前（`direction = 1`）と後ろ（`direction = -1`）の両方に使えるようにしたものです
- `timer += rc.get_delta_time()` で、今の状態になってからの時間を数えます（3-1）。`change()` で 0 にもどるので、「BACK に入ってから 1 秒」が数えられます
- TURN の曲がる向き `turn_dir` は、`change()` の中で、TURN に入るときに1回だけ決めます。TURN の間、毎コマ決め直すと、向きがふらつくからです

### 走らせてみる

説明用のモデルで、箱が2つある 5 m × 6 m の部屋で 60 秒走らせました。

```text
  0.00 秒 >> 部屋の中を走り回ります
  5.67 秒 BACK へ
  6.67 秒 TURN へ
  7.50 秒 BACK へ
  8.50 秒 TURN へ
  9.68 秒 BACK へ
 10.68 秒 TURN へ
 12.18 秒 FORWARD へ
 14.33 秒 BACK へ
```

（左の数字は、スタートからの秒数です。この本で書き足しました。）

![左は、部屋を上から見た図に、60 秒間の道すじを状態ごとの色でかいたもの。FORWARD（青）でまっすぐ進み、壁や箱の手前で BACK（オレンジ）で少し下がり、TURN（緑）で曲がって向きを変えることをくり返しながら、部屋じゅうを走り回っている。右は、はじめの 20 秒の状態を時間にそって並べたもの。0〜5.7 秒は FORWARD、そのあと BACK と TURN を何回かくり返してから FORWARD にもどる](/images/racecar-neo-jp/7-2/fig2-run.png)
*図2　部屋の中を走り回る（説明用の簡単なモデル）*

60 秒の間に、状態は 44 回切りかわり、一度もぶつかりませんでした。壁や箱にいちばん近づいたのは、車の中心から 29.5 cm でした。はじめの角では、BACK と TURN を3回くり返してから、やっと FORWARD にもどっています。1回の TURN で向きを変えきれないときも、「前が近い → BACK」の出口があるので、ぶつからずにやり直せます。

## ④ 数式・コード

### 「どの状態でも」の切りかわり

安全停止（7-1）や「コーンを見失ったら探しなおす」（7-3）のように、今どの状態でも同じように切りかえたいものがあります。このときは、状態ごとの `if` の**前**に書きます。

```python
    # どの状態でも：〜なら、STOP へ
    if 条件 and state != State.STOP:
        change(State.STOP)

    if state == State.FORWARD:
        ...
```

`state != State.STOP` をつけないと、STOP の間も毎コマ `change()` が呼ばれて、タイマーがいつまでも 0 のままになります。

### 表のまま書く方法

状態が増えてきたら、「状態ごとの speed と angle」を辞書（dict）にまとめる書き方もあります。`SPEEDS = {State.FORWARD: 0.5, State.BACK: -0.4, State.TURN: 0.4}` のようにしておくと、`speed = SPEEDS[state]` の1行で決まります。設計の表と、プログラムの形が近くなるので、見くらべやすくなります。

## ⑤ つまずきポイント

### 状態が、毎コマ切りかわる

2つの状態の条件が、同じ所でぶつかっていると、毎コマ行ったり来たりします（チャタリング、6-17）。条件のしきい値にあいだをあける（ヒステリシス）か、「その状態に入って○秒は出ない」ようにします。

### 状態から出られなくなる

出口の条件が、ずっと成り立たないことがあります。たとえば、「後ろの物が 30 cm より近い」だけを BACK の出口にすると、後ろに何もない所では、いつまでも下がり続けます。時間の出口（タイムアウト）を1つ足しておくと安全です。

### `change()` を通さずに `state` を書きかえた

`state = State.TURN` と直接書くと、タイマーがもどらず、入るときの処理も行われません。状態を変えるときは、必ず `change()` を呼びましょう。

## ⑥ 確認問題

**問1**　`patrol.py` で、BACK に入ってから 0.7 秒後に、後ろの物が 25 cm になりました。次はどの状態になりますか。

:::details 答え
TURN です。BACK の出口の条件は「1 秒たった、または後ろの物が 30 cm より近い」なので、0.7 秒でも、後ろの物が 25 cm なら TURN に切りかわります。
:::

**問2**　TURN の曲がる向きを、`change()` の中ではなく、TURN の間の毎コマ決めるようにすると、何が困りますか。

:::details 答え
右と左の空き具合は、曲がっている間に変わります。毎コマ決め直すと、途中で曲がる向きが反対になり、どちらにも曲がりきれずにふらつくことがあります。
:::

**問3**　「信号の色を見て、赤なら止まり、青なら進む。止まってから 10 秒たっても青にならなければ、ゆっくり進む」を、状態と切りかわる条件の表にしてみましょう。

:::details 答え
たとえば、次のようになります。

| 状態 | すること | 切りかわる条件 → 次の状態 |
|---|---|---|
| GO | 進む | 赤が見えた → STOP |
| STOP | 止まる | 青が見えた → GO<br>10 秒たった → CREEP |
| CREEP | ゆっくり進む | 青が見えた → GO<br>赤が見えた → STOP |
:::

## ⑦ 原典

`patrol.py`・図1・図2と表示の数字は、この本で作ったものです（説明用の簡単なモデル）。ステートマシンの考え方は、6-17（壁の見え方で状態を切りかえる）と、2-2（フラグで状態を覚える）の続きです。
