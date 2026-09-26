---
title: "8-1 統合 — 線・壁・AR マーカーの区間を、ステートマシンで切りかえる"
free: true
---

グランプリの課題は、これまでの課題とちがい、ひな形のコードがほとんどありません。これまでに作ったプログラムを組み合わせて、コースを最初から最後まで、ひとりで走りきるプログラムを作ります。この回では、床の線をたどる・壁に沿って走る・空いている方向へ走る・AR マーカーで曲がる、の4つの部品を、ステートマシンで切りかえます。

## ① この回でできるようになること

1. グランプリの課題の条件を説明できる
2. これまでのプログラムを、状態ごとに呼び出せる「部品」にまとめられる
3. 区間の変わり目を見つける条件を決めて、状態を切りかえるプログラムを作れる
4. 切りかえを調べる順番（どの条件を先に見るか）の大切さを説明できる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Integration | 統合 | いくつかのプログラムを、1つのプログラムにまとめること |
| Section | 区間 | コースの中で、同じ走り方で走れるひとまとまりの部分 |
| Module | 部品 | 1つの仕事だけをするクラスや関数。別のプログラムから呼び出して使う |
| Priority | 優先順位 | いくつかの条件が同時に成り立ったとき、どれを先にするかの順番 |
| Checkpoint | チェックポイント | コースの途中で、通ったかどうかを記録する所 |

## ③ 本文

### グランプリの課題

課題のファイルは、labs フォルダの中の `grand_prix/grand_prix.py` です。中身は、`start()`・`update()`・`update_slow()` の空の関数だけです。原典には、次のように書かれています（要約）。

- ひな形のコードはない。これまでのラボで書いたコードを使って、この課題をやりとげる
- スタートしたら、人が操作できてはいけない。車は自分で前に進み、コースを走りぬけ、**自分で止まる**

シミュレータでは、**Final Challenge** の中に、グランプリのコースが年ごとに並んでいます。たとえば、次のようなコースがあります。

| コース | 自動採点 |
|---|---|
| Grand Prix 2025 | 25 点、制限時間 200 秒 |
| Mini Grand Prix: Fall 2025 | 20 点、制限時間 120 秒。6 通りのコースから、1つが選ばれる |
| Grand Prix 2020 | 25 点、制限時間 360 秒。速くゴールするほどボーナスがある |

コースの形は、年ごとにちがいます。シミュレータのファイルを見ると、Grand Prix 2025 のコースには、床の線の部品（22 個）と AR マーカー（1 個）が置かれています。壁のある通路もあります。どのコースでも使えるように、**区間ごとの走り方を部品にして、切りかえる**作り方をします。

### この本のコース

この回では、図1の左のようなコースを、説明用のモデルで作りました（この本のコースです）。

1. **線**：広い床の上の、青い線をたどる
2. **通路**：幅 150 cm の通路を、壁に沿って走る。直角の曲がり角が2つある
3. **分かれ道**：T 字路の正面の壁に、AR マーカー（番号 1）がある。左は行き止まりで、右が正しい道
4. **箱のある広間**：幅 600 cm の広間に、箱が4つ置いてある。いちばん奥の壁に、ゴールの AR マーカー（番号 3）がある

AR マーカーの番号の意味は、この本で決めたきまりです（0：左へ、1：右へ、3：ゴール）。実際のコースでは、コースに合わせて決め直してください。

### 部品にする

7-13 で、壁沿い走行を `WallSteer` クラスに、Gap Follower を `gap_angle()` 関数にまとめました。線をたどる部分も、6-21 の `line_follow_pid.py` から、`LineSteer` クラスにまとめます。

```python:line_steer.py
"""
line_steer.py
6-21 の line_follow_pid.py のハンドルを決める部分を、クラスにまとめたもの（8-1）。
pid.py を同じフォルダに置いて使う。
"""

import racecar_utils as rc_utils
from pid import PID

BLUE = ((90, 50, 50), (120, 255, 255))   # 線の色（Lab E・Lab F のひな形の青）
MIN_CONTOUR_AREA = 30                      # これより小さいかたまりは無視する
CROP_FLOOR = ((360, 0), (480, 640))        # 画像の下の部分（車のすぐ前の床）


class LineSteer:
    """床の線を見てハンドルの角度を決める。angle(image, dt) を毎コマ呼ぶ"""

    def __init__(self):
        self.pid = PID(kp=2.0, ki=1.0, kd=0.1)
        self.reset()

    def reset(self):
        self.pid.reset()
        self.last_angle = 0.0

    def find_line(self, image):
        """線のいちばん大きいかたまりの (中心の列, 面積) を返す。見えなければ None"""
        if image is None:
            return None
        image = rc_utils.crop(image, CROP_FLOOR[0], CROP_FLOOR[1])
        contours = rc_utils.find_contours(image, BLUE[0], BLUE[1])
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)
        if contour is None:
            return None
        return rc_utils.get_contour_center(contour)[1], rc_utils.get_contour_area(contour)

    def angle(self, image, dt):
        """線が見えれば、PID で決めた angle を返す。見えなければ None"""
        found = self.find_line(image)
        if found is None:
            return None
        error = (found[0] - 320) / 320               # 左はし -1 〜 右はし +1（6-2）
        self.last_angle = self.pid.update(error, dt)
        return self.last_angle
```

`find_line()` は、線のかたまりの中心の列と面積を返します。面積は、「線の区間に入ったか」を決めるのに使います。

### 状態を設計する

区間ごとの走り方と、区間の変わり目の見つけ方を、表にまとめます（7-2）。

| 状態 | 走り方 | 次の状態へ |
|---|---|---|
| LINE | 線をたどる（6-21） | 線が 0.5 秒続けて見えなければ WALL |
| WALL | 壁沿い走行（6-18） | 前の帯の物が 150 cm より近くなったら GAP、線が大きく見えたら LINE |
| GAP | Gap Follower（7-10） | 前の帯の物が 250 cm より遠くなったら WALL、線が大きく見えたら LINE |
| MARKER | マーカーのほうを向いて近づく（6-3） | 十分近づいたら、番号 1 なら TURN、番号 3 なら FINISH |
| TURN | 決まった時間、右（または左）にハンドルを切る | 時間がたったら WALL |
| FINISH | 止まる | （ずっと FINISH） |

さらに、LINE・WALL・GAP のどれでも、知っている番号のマーカーがある大きさより大きく写ったら、MARKER へ切りかえます。

ここで大切なのは、**条件を調べる順番**です。分かれ道では、正面の壁が近づくので、「前の帯の物が 150 cm より近い」（GAP へ）と、「マーカーが見えた」（MARKER へ）が、同時に成り立ちます。GAP になると、Gap Follower は広い空きを選ぶので、行き止まりのほうへ曲がるかもしれません。そこで、マーカーの条件を**いちばん先に**調べます。

### プログラム

```python:grand_prix.py
"""
grand_prix.py
グランプリ（8-1）。線・壁・障害物・AR マーカーの区間を、ステートマシンで切りかえて走り、ゴールで止まる。
  LINE  ：床の線を PID でたどる（6-21）。線が LOST_TIME 秒続けて見えなければ WALL へ
  WALL  ：壁沿い走行（6-18）。前の帯の物が NEAR より近くなったら GAP へ（7-13）
  GAP   ：Gap Follower（7-10）。前の帯の物が FAR より遠くなったら WALL へ（7-13）
  MARKER：AR マーカーのほうを向いて近づく（6-3）。十分近づいたら、番号で TURN か FINISH へ
  TURN  ：決まった時間、決まった向きにハンドルを切る。終わったら WALL へ
  FINISH：止まる（もう動かない）
LINE・WALL・GAP のときに、知っている番号のマーカーが SEEN_HEIGHT より大きく写ったら MARKER へ。
WALL・GAP のときに、線が LINE_AREA より大きく見えたら LINE へ。
line_steer.py・wall_steer.py・gap_steer.py・walls.py・pid.py・gaps.py を同じフォルダに置いて使う。
"""

import sys
from enum import IntEnum

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from line_steer import LineSteer
from wall_steer import WallSteer
from gap_steer import gap_angle

rc = racecar_core.create_racecar()

# 状態ごとの速さ（8-2 で調整する）
LINE_SPEED = 0.5
WALL_SPEED = 0.5
GAP_SPEED = 0.5
MARKER_SPEED = 0.4
TURN_SPEED = 0.4

LOST_TIME = 0.5        # 線がこの時間（秒）続けて見えなければ、線の区間は終わり
LINE_AREA = 300        # WALL・GAP のとき、線のかたまりがこの面積（画素）より大きければ LINE へ
HALF_WIDTH = 20.0      # 前の帯の幅の半分（cm）（7-1）
NEAR = 150.0           # 前の帯の物がこれより近くなったら GAP へ（cm）（7-13）
FAR = 250.0            # 前の帯の物がこれより遠くなったら WALL へ（cm）（7-13）

# AR マーカーの番号の意味（この本のコースのきまり。実際のコースに合わせて変える）
TURN_ANGLE = {0: -1.0, 1: 1.0}   # 0：左へ曲がる、1：右へ曲がる（6-3）
FINISH_ID = 3                     # 3：ゴール。近づいたら止まる
SEEN_HEIGHT = 25       # マーカーがこの高さ（画素）より大きく写ったら、MARKER へ
NEAR_HEIGHT = 60       # マーカーがこの高さ（画素）より大きく写ったら、曲がる（または止まる）
KP_MARKER = 0.8        # マーカーのほうを向くための比例ゲイン（6-3）
TURN_TIME = 1.6        # 曲がり続ける時間（秒）


def lidar_angles(scan):
    """LIDAR の各点の角度（ラジアン）。0 が正面、時計回り。
    点の数は len(scan) から求める（720 点なら 0.5° ずつ）"""
    return np.radians(np.arange(len(scan)) * 360 / len(scan))


class State(IntEnum):
    LINE = 0
    WALL = 1
    GAP = 2
    MARKER = 3
    TURN = 4
    FINISH = 5


line = LineSteer()
wall = WallSteer()
state = State.LINE
lost = 0.0             # 線が見えなくなってからの時間（秒）
turn_left = 0.0        # TURN の残り時間（秒）
turn = 0.0             # TURN で切るハンドルの向き
ahead = 0.0
elapsed = 0.0          # スタートからの時間（秒）。区間ごとの時間を測るのに使う（8-2）


def distance_ahead(scan):
    """車の前の、幅 2 × HALF_WIDTH の帯の中で、いちばん近い物までの前向きの距離（7-1）"""
    angles = lidar_angles(scan)
    forward = scan * np.cos(angles)
    side = scan * np.sin(angles)
    inside = (scan > 0) & (forward > 0) & (np.abs(side) < HALF_WIDTH)
    if not inside.any():
        return 10000.0
    return float(forward[inside].min())


def find_marker(image):
    """知っている番号のマーカーのうち、いちばん大きく写っているものの (番号, 中心の列, 高さ) を返す（6-3）"""
    if image is None:
        return None
    best = None
    for marker in rc_utils.get_ar_markers(image):
        if marker.get_id() not in TURN_ANGLE and marker.get_id() != FINISH_ID:
            continue
        corners = marker.get_corners()
        height = corners[:, 0].max() - corners[:, 0].min()
        if best is None or height > best[2]:
            best = (marker.get_id(), corners[:, 1].mean(), height)
    return best


def change(new_state, why):
    """状態を切りかえて、入るときの処理をする（7-2）"""
    global state, lost
    state = new_state
    if new_state == State.LINE:
        line.reset()
        lost = 0.0
    if new_state == State.WALL:
        wall.reset()
    print(f"{new_state.name} へ（{why}）　{elapsed:.1f} 秒")


def start():
    global state, elapsed
    state = State.LINE
    elapsed = 0.0
    line.reset()
    wall.reset()
    rc.drive.stop()
    print(">> グランプリ：スタート")


def update():
    global lost, turn_left, turn, ahead, elapsed
    dt = rc.get_delta_time()
    elapsed += dt
    image = rc.camera.get_color_image()
    scan = rc.lidar.get_samples()
    ahead = distance_ahead(scan)
    marker = find_marker(image)

    # ---- 1. 状態を切りかえる ----
    if state in (State.LINE, State.WALL, State.GAP) and marker is not None and marker[2] > SEEN_HEIGHT:
        change(State.MARKER, f"マーカー {marker[0]} が見えた")
    elif state == State.LINE:
        if line.find_line(image) is None:
            lost += dt
            if lost > LOST_TIME:
                change(State.WALL, "線が見えなくなった")
        else:
            lost = 0.0
    elif state in (State.WALL, State.GAP):
        found = line.find_line(image)
        if found is not None and found[1] > LINE_AREA:
            change(State.LINE, "線が見えた")
        elif state == State.WALL and ahead < NEAR:
            change(State.GAP, f"前の物まで {ahead:.0f} cm")
        elif state == State.GAP and ahead > FAR:
            change(State.WALL, "前の帯に物がない" if ahead >= 10000 else f"前の物まで {ahead:.0f} cm")
    elif state == State.MARKER:
        if marker is None:
            change(State.WALL, "マーカーを見失った")
        elif marker[2] > NEAR_HEIGHT:
            if marker[0] == FINISH_ID:
                change(State.FINISH, "ゴールのマーカー")
            else:
                turn = TURN_ANGLE[marker[0]]
                turn_left = TURN_TIME
                change(State.TURN, f"マーカー {marker[0]} → {'右' if turn > 0 else '左'}へ曲がる")
    elif state == State.TURN:
        turn_left -= dt
        if turn_left <= 0:
            change(State.WALL, "曲がり終えた")

    # ---- 2. 今の状態で、速さとハンドルを決める ----
    wall_angle = wall.angle(scan, dt)          # 壁沿い走行の角度は、いつも計算しておく（7-13）
    speed, angle = 0.0, 0.0
    if state == State.LINE:
        a = line.angle(image, dt)
        speed, angle = LINE_SPEED, (line.last_angle if a is None else a)
    elif state == State.WALL:
        speed, angle = WALL_SPEED, wall_angle
    elif state == State.GAP:
        g = gap_angle(scan)
        speed, angle = GAP_SPEED, (wall_angle if g is None else g)
    elif state == State.MARKER:
        error = (marker[1] - 320) / 320
        speed, angle = MARKER_SPEED, rc_utils.clamp(KP_MARKER * error, -1.0, 1.0)
    elif state == State.TURN:
        speed, angle = TURN_SPEED, turn
    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    print(f"  {state.name}　前の物まで {min(ahead, 9999):.0f} cm")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

- `update()` は、「1. 状態を切りかえる」と「2. 今の状態で、速さとハンドルを決める」の2つに分けています。切りかえの条件を1か所にまとめると、順番が見やすくなります
- `change()` は、状態に入るときの処理（7-2）をまとめた関数です。LINE に入るときは線の PID を、WALL に入るときは壁沿い走行を、やり直します（7-13）。切りかえた理由と、スタートからの時間 `elapsed` も表示します（8-2 で使います）
- FINISH からは、どの状態にも切りかわりません。これが「自分で止まる」です
- コントローラーの値は、どこでも読んでいません。これが「人が操作できない」です

走らせると、状態が変わるたびに、次のように表示されました。

```text
>> グランプリ：スタート
WALL へ（線が見えなくなった）　15.6 秒
GAP へ（前の物まで 143 cm）　21.7 秒
WALL へ（前の物まで 313 cm）　23.2 秒
GAP へ（前の物まで 139 cm）　29.2 秒
WALL へ（前の物まで 325 cm）　30.7 秒
MARKER へ（マーカー 1 が見えた）　35.7 秒
TURN へ（マーカー 1 → 右へ曲がる）　39.1 秒
WALL へ（曲がり終えた）　40.7 秒
GAP へ（前の物まで 123 cm）　40.7 秒
WALL へ（前の物まで 279 cm）　41.2 秒
GAP へ（前の物まで 146 cm）　47.2 秒
WALL へ（前の帯に物がない）　48.7 秒
GAP へ（前の物まで 148 cm）　55.5 秒
WALL へ（前の物まで 298 cm）　56.8 秒
GAP へ（前の物まで 140 cm）　79.8 秒
MARKER へ（マーカー 3 が見えた）　80.1 秒
FINISH へ（ゴールのマーカー）　81.6 秒
```

（右の数字は、スタートからの時間です。`update_slow()` の1秒ごとの表示は、はぶいています。）

![左は、この本のグランプリのコースを上から見た図。下の広い床に、うすい青の線がS字にかかれている。そこから幅 150 cm の通路が上へのび、左へ曲がり、また上へ曲がって、T 字路に出る。T 字路の正面の壁には「マーカー 1」がある。左は行き止まりで、右へ進むと、また上へ曲がって、箱が4つある広い広間に入る。広間のいちばん上の壁に「マーカー 3」がある。車の道すじは、状態で色分けされている。線の区間は青（LINE）、通路は灰色（WALL）、曲がり角の手前はオレンジ（GAP）、T 字路の手前は緑（MARKER）、T 字路で右へ曲がる所は紫（TURN）。広間では、入り口でオレンジ（GAP）になったあと、左の壁に沿って灰色（WALL）のまま箱の左を通りぬけ、最後に緑でマーカー 3 に近づいて、赤い四角の所で止まっている。右上は、線の区間でカメラに写った画像で、下のほうに青い線が写り、線を探す範囲が四角で囲まれている。右下は、T 字路の手前で写った画像で、正面にマーカー 1 が写っている](/images/racecar-neo-jp/8-1/fig1-course.png)
*図1　線・壁・障害物・AR マーカーの区間を、状態を切りかえて走る（説明用の簡単なモデル）*

LIDAR とカメラのばらつきを変えて、5 回走らせました。

| 回 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 止まった時間 | 81.6 秒 | 79.0 秒 | 79.0 秒 | 79.4 秒 | 79.2 秒 |
| ぶつかったか | なし | なし | なし | なし | なし |
| 壁や箱にいちばん近づいた距離 | 49.3 cm | 21.3 cm | 20.6 cm | 22.8 cm | 22.5 cm |

（距離は、車の中心から、いちばん近い壁や箱までです。車の中心から車のはしまでは、約 12 cm です。）

5 回とも、ぶつからずに走りきり、ゴールのマーカーの手前で止まりました。止まった時間は、ほとんど同じです。次の 8-2 では、この時間を縮めていきます。

## ④ 数式・コード

### 切りかえの順番をコードで表す

`update()` の「1. 状態を切りかえる」は、`if`・`elif` の順番が、そのまま優先順位になっています。

```python
if state in (State.LINE, State.WALL, State.GAP) and マーカーが大きく見えた:   # 1番め
    ...
elif state == State.LINE:                                                  # 2番め
    ...
elif state in (State.WALL, State.GAP):                                     # 3番め：その中でも「線」が先
    ...
```

`elif` は、「前の条件が成り立たなかったときだけ調べる」ので、上にある条件ほど優先されます。1コマで切りかわるのは、多くても1回だけです。

### 1コマの流れ

```text
画像と LIDAR を読む
  → マーカーを探す・前の帯の距離を測る
  → 1. 状態を切りかえる（多くても1回）
  → 2. 今の状態の部品で、speed と angle を決める
  → set_speed_angle()
```

`wall.angle()` だけは、どの状態でも毎コマ呼んでいます。6-17 の「右だけ・左だけ・両側」の状態の数え方を、止めないためです（7-13）。

## ⑤ つまずきポイント

### 部品ごとに、同じ画像を何回も読む

`rc.camera.get_color_image()` を、線を探すとき・マーカーを探すときに、別々に呼ぶと、1コマの計算に時間がかかります。このプログラムでは、`update()` のはじめに1回だけ読んで、それを部品に渡しています。

### 行き止まりに入ってから、マーカーに気づく

マーカーに近づく条件（`SEEN_HEIGHT`）が大きすぎると、分かれ道にかなり近づくまで MARKER になりません。その前に GAP に切りかわると、行き止まりへ曲がってしまうことがあります。このモデルでは、マーカーまで約 3.7 m の所で MARKER になるように、25 画素にしました。写った高さから距離の目安を求める方法は、6-3 の④にあります。実際のカメラで、距離と写る大きさを確かめて決めましょう。

### このモデルの AR マーカー

説明用のモデルでは、AR マーカーはいつも車のほうを向いて写り、壁のうしろにあっても写ります。実際のシミュレータでは、ななめから見たマーカーはゆがみ、壁にかくれたマーカーは写りません。

## ⑥ 確認問題

**問1**　分かれ道で、「マーカーが見えた」より先に「前の帯の物が近い」を調べると、どんなことが起きるおそれがありますか。

:::details 答え
正面の壁が近づいた時点で GAP に切りかわり、Gap Follower が広い空きを選んで、行き止まりのほうへ曲がるおそれがあります。マーカーの条件を先に調べれば、MARKER になって、マーカーの番号どおりに曲がれます。
:::

**問2**　grand_prix.py が「自分で止まる」「人が操作できない」という課題の条件をみたしているのは、それぞれどこですか。

:::details 答え
「自分で止まる」は、FINISH の状態です。ゴールのマーカーに近づくと FINISH になり、そこから別の状態には切りかわらず、speed を 0 にし続けます。「人が操作できない」は、コントローラーの値をどこでも読んでいないことです。
:::

## ⑦ 原典

- グランプリの課題（ひな形のコードがない、人が操作できない、自分で止まる）：[racecar-neo-prereq-labs](https://github.com/MITRacecarNeo/racecar-neo-prereq-labs) の `labs/grand_prix/grand_prix.py`（MIT License）
- Final Challenge のコースと自動採点の点数・制限時間・ボーナス：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `LevelCollection.cs`
- Grand Prix 2025 のコースの部品（線と AR マーカー）：同じく `Assets/Scenes/GrandPrixFiles/GrandPrix2025.unity`
- `crop()`・`find_contours()`・`get_largest_contour()`・`get_contour_center()`・`get_contour_area()`・`get_ar_markers()`・`clamp()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）

`line_steer.py`・`grand_prix.py`・この本のコース・図1と表の数字は、この本で作った説明用の簡単なモデル（上から見た2次元の車、床の線と AR マーカーを写すカメラ、LIDAR の計算）によるものです。
