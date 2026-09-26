---
title: "7-13 2つを組み合わせる"
free: true
---

7-12 で、壁沿い走行と Gap Follower は、得意と苦手がちょうど反対になっていることがわかりました。この回では、**ふだんは壁沿い走行で走り、前に物があるときだけ Gap Follower に切りかえる**プログラムを作ります。7-1 の「前の帯」と、7-2 のステートマシンを使います。

## ① この回でできるようになること

1. 2つのハンドルの決め方を、クラスや関数にまとめて、1つのプログラムから使える
2. 前の帯の中の物までの距離で、2つを切りかえるステートマシンを作れる
3. 切りかえる距離にあいだをあける理由と、もどるときにやり直す（reset）理由を説明できる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Mode | 走り方の状態 | 今どちらのハンドルの決め方を使っているか（WALL か GAP） |
| Hysteresis | あいだをあけた切りかえ | 行きと帰りで、切りかえる値を変えること（6-17） |
| Reset | やり直し | たまった値（PID の積分など）を消して、はじめからにすること |
| Blend | 混ぜ合わせ | 2つの角度を、割合をつけて足し合わせること |

## ③ 本文

### いつ切りかえるか

7-12 のコース O（横に入り口のある通路）で、Gap Follower が失敗したのは、横の部屋が「いちばん広い空き」に見えたからでした。でも、横の部屋があっても、**車の前**に物があるわけではありません。一方、コース B の箱や、コース C の柱は、車の前に現れます。

そこで、7-1 の安全停止と同じ「前の帯」（車の前の、幅 40 cm の帯）の中の、いちばん近い物までの距離で切りかえます。

| 走り方 | すること | 次の走り方へ |
|---|---|---|
| WALL | 壁沿い走行（6-18 と同じ） | 前の帯の物が `NEAR`（150 cm）より近くなったら GAP |
| GAP | Gap Follower（7-10 と同じ） | 前の帯の物が `FAR`（250 cm）より遠くなったら WALL |

`NEAR` と `FAR` の間をあけているのは、6-17 と同じ理由です。1つの値で切りかえると、ちょうどその距離の近くで、WALL と GAP が1コマごとに入れかわってしまいます。

### 2つのハンドルの決め方を部品にする

1つのプログラムで2つの走り方を使うため、それぞれを部品にまとめます。

壁沿い走行は、6-18 の `wall_follow_course.py` のハンドルを決める部分を、クラス `WallSteer` にまとめます。PID の積分や、6-17 の状態（BOTH・RIGHT・LEFT・NONE）を持っているので、クラスにすると、`reset()` でまとめてやり直せます。

```python:wall_steer.py
"""
wall_steer.py
6-18 の wall_follow_course.py のハンドルを決める部分を、クラスにまとめたもの（7-13）。
walls.py と pid.py を同じフォルダに置いて使う。
"""

from enum import IntEnum

import racecar_utils as rc_utils
from pid import PID
from walls import side_wall, front_distance

HOLD = 10          # 新しい状態がこのコマ数だけ続いたら、切りかえる
FRONT_LIMIT = 200  # 正面の壁がこれより近いと、開いている側へ切りはじめる（cm）
KF = 0.02          # 正面の壁が 1 cm 近づくごとに、切る量


class State(IntEnum):
    BOTH = 0
    RIGHT = 1
    LEFT = 2
    NONE = 3


def seen_state(right, left):
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
        r = 1000.0
    if l == 0.0:
        l = 1000.0
    if r > l:
        return 1
    return -1


class WallSteer:
    """壁を見てハンドルの角度を決める。angle(scan, dt) を毎コマ呼ぶ"""

    def __init__(self):
        self.pid = PID(kp=0.04, ki=0.005, kd=0.04, i_zone=20)
        self.reset()

    def reset(self):
        self.pid.reset()
        self.state = State.BOTH
        self.candidate = State.BOTH
        self.count = 0
        self.target_right = 50.0
        self.target_left = 50.0

    def angle(self, scan, dt):
        right_angle, right = side_wall(scan, "right")
        left_angle, left = side_wall(scan, "left")

        # 1. 状態を決める（6-17）
        seen = seen_state(right, left)
        if seen == self.state:
            self.count = 0
        else:
            if seen == self.candidate:
                self.count += 1
            else:
                self.candidate = seen
                self.count = 1
            if self.count >= HOLD:
                self.state = seen
                self.count = 0
                self.pid.reset()
                if self.state == State.RIGHT:
                    self.target_right = right
                if self.state == State.LEFT:
                    self.target_left = left

        # 2. 状態に合わせて、ずれと向きを決める（6-16、6-17）
        angle = 0.0
        if self.state == State.BOTH and right is not None and left is not None:
            angle = self.pid.update((right - left) / 2, dt, rate=(right_angle - left_angle) / 2)
        elif self.state == State.RIGHT and right is not None:
            angle = self.pid.update(right - self.target_right, dt, rate=right_angle)
        elif self.state == State.LEFT and left is not None:
            angle = self.pid.update(self.target_left - left, dt, rate=-left_angle)

        # 3. 正面に壁が近づいたら、開いている側へ切る（6-18）
        front = front_distance(scan)
        if front < FRONT_LIMIT:
            angle += open_side(scan) * KF * (FRONT_LIMIT - front)
        return rc_utils.clamp(angle, -1.0, 1.0)
```

Gap Follower は、7-10 までで決めた設定で、ハンドルの角度だけを返す関数 `gap_angle()` にします。

```python:gap_steer.py
"""
gap_steer.py
7-10 までの Gap Follower のハンドルを決める部分を、関数にまとめたもの（7-13）。
gaps.py を同じフォルダに置いて使う。
"""

import racecar_utils as rc_utils
from gaps import front_view, find_gaps, widest_gap, gap_center, add_bubble, extend_disparities

FULL_TURN = 30.0     # 目標の向きがこの角度（度）より横にあったら、ハンドルをいっぱいに切る
THRESHOLD = 150.0    # これより遠くまで見える向きを「空き」とする（cm）
BUBBLE = 20.0        # いちばん近い点のまわりをふさぐ半径（cm）（7-9）
HALF_WIDTH = 20.0    # 物のはしで、近い距離をのばす幅（cm）（7-10）
JUMP = 50.0          # 物のはしとみなす、となりの点との距離の差（cm）（7-10）


def gap_angle(scan):
    """いちばん広い空きの真ん中へ向かう angle を返す。空きがなければ None"""
    angles, dists = front_view(scan)
    dists = extend_disparities(angles, dists, HALF_WIDTH, JUMP)
    dists = add_bubble(angles, dists, BUBBLE)
    gaps = find_gaps(dists, THRESHOLD)
    if len(gaps) == 0:
        return None
    target = gap_center(widest_gap(gaps), angles)
    return rc_utils.clamp(target / FULL_TURN, -1.0, 1.0)
```

### 切りかえるプログラム

```python:combo_follow.py
"""
combo_follow.py
壁沿い走行（WallSteer）と Gap Follower（gap_angle）を、前の帯の中の物までの距離で切りかえる（7-13）。
  WALL：ふだんは壁沿い走行。前の帯に物が NEAR より近づいたら GAP へ
  GAP ：Gap Follower。前の帯の物が FAR より遠くなったら WALL へもどる
wall_steer.py・gap_steer.py・walls.py・pid.py・gaps.py を同じフォルダに置いて使う。
"""

import sys
from enum import IntEnum

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
from wall_steer import WallSteer
from gap_steer import gap_angle

rc = racecar_core.create_racecar()

SPEED = 0.5
HALF_WIDTH = 20.0      # 前の帯の幅の半分（cm）（7-1）
NEAR = 150.0           # 前の帯の物がこれより近くなったら、GAP へ（cm）
FAR = 250.0            # 前の帯の物がこれより遠くなったら、WALL へ（cm）。NEAR とあいだをあける（6-17）
BLEND = False          # True にすると、切りかえずに、2つの角度を混ぜ合わせる


def lidar_angles(scan):
    """LIDAR の各点の角度（ラジアン）。0 が正面、時計回り。
    点の数は len(scan) から求める（シミュレータは 720 点、実機は 1080 点。9-3）"""
    return np.radians(np.arange(len(scan)) * 360 / len(scan))


class Mode(IntEnum):
    WALL = 0
    GAP = 1


wall = WallSteer()
mode = Mode.WALL
ahead = 0.0


def distance_ahead(scan):
    """車の前の、幅 2 × HALF_WIDTH の帯の中で、いちばん近い物までの前向きの距離（7-1）"""
    angles = lidar_angles(scan)
    forward = scan * np.cos(angles)
    side = scan * np.sin(angles)
    inside = (scan > 0) & (forward > 0) & (np.abs(side) < HALF_WIDTH)
    if not inside.any():
        return 10000.0
    return float(forward[inside].min())


def start():
    global mode
    mode = Mode.WALL
    wall.reset()
    rc.drive.stop()
    print(">> 壁沿い走行と Gap Follower を切りかえて走ります")


def update():
    global mode, ahead
    scan = rc.lidar.get_samples()
    dt = rc.get_delta_time()
    ahead = distance_ahead(scan)

    if mode == Mode.WALL and ahead < NEAR:
        mode = Mode.GAP
        print(f"GAP へ（前の物まで {ahead:.0f} cm）")
    elif mode == Mode.GAP and ahead > FAR:
        mode = Mode.WALL
        if not BLEND:
            wall.reset()                     # 壁沿い走行を、はじめからやり直す
        print(f"WALL へ（前の物まで {ahead:.0f} cm）")

    wall_angle = wall.angle(scan, dt)        # 壁沿い走行の角度は、いつも計算しておく
    g = gap_angle(scan)
    angle = wall_angle
    if BLEND:
        if g is not None:
            w = min(1.0, max(0.0, (ahead - NEAR) / (FAR - NEAR)))   # 前が空いているほど 1（壁沿い）に近い
            angle = w * wall_angle + (1 - w) * g
    elif mode == Mode.GAP and g is not None:
        angle = g
    rc.drive.set_speed_angle(SPEED, angle)


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
```

- WALL から GAP へ切りかわっている間も、`wall.angle()` は毎コマ呼んでいます。6-17 の状態の数え方などを、止めないためです
- GAP から WALL にもどるときは、`wall.reset()` で壁沿い走行をやり直します。GAP の間、壁沿い走行の PID には「使われなかった角度」の積分がたまり、6-17 の状態もずれているからです
- `BLEND = True` にすると、切りかえずに、2つの角度を混ぜ合わせます（あとでくらべます）

`wall_steer.py` は 6-16 の `walls.py` と 6-12 の `pid.py` を、`gap_steer.py` は 7-10 までの `gaps.py` を使います。5つのファイルを、同じフォルダに置いてください。

### 2つの苦手がつながったコース

コース D は、7-12 のコース O（横に入り口のある通路）の先に、コース C のような柱の並ぶ広間をつなげたものです。どちらか1つの走り方では、どちらかの苦手な所で失敗します。

| 走り方 | 結果（5 回） |
|---|---|
| 壁沿い走行だけ | 5 回とも、柱の広間でぶつかった |
| Gap Follower だけ（speed 0.5） | ゴールできなかった（横の部屋に入り、3 回ぶつかり、2 回はスタートのほうへもどった） |
| 切りかえ（`combo_follow.py`） | 4 回ゴール（64.1〜105.2 秒）、1 回ぶつかった |
| 切りかえ、もどるときに `reset()` しない | 2 回ゴール（63.3・64.4 秒）、3 回ぶつかった |
| 混ぜ合わせ（`BLEND = True`） | ゴールできなかった（4 回ぶつかり、1 回は時間内に着かなかった） |

（どれも speed 0.5 の一定、110 秒までです。）

![コース D を上から見た図が2つ並んでいる。下半分が横に入り口のある通路、上半分が柱の並ぶ広間で、いちばん上にゴールの線がある。左の図は1つの走り方だけの道すじ。青（壁沿い走行だけ）は、通路をまっすぐぬけて広間に入り、柱の間をくねって進むが、ゴールの手前の柱にぶつかっている（ばつ）。オレンジ（Gap Follower だけ）は、はじめの左の部屋に入って輪をえがき、スタートのほうへもどっている。右の図は切りかえて走る道すじで、64.6 秒でゴールしている。通路の部分はすべて青（WALL）で、広間では、柱に近づくたびに、短いオレンジ（GAP）がはさまっている](/images/racecar-neo-jp/7-13/fig1-combine.png)
*図1　前に物があるときだけ Gap Follower に切りかえる（説明用の簡単なモデル）*

図1の右のように、切りかえて走ると、横に入り口のある通路は、ずっと WALL（壁沿い走行）のままで通りぬけました。前の帯に物がないので、GAP に切りかわらないからです。柱の広間に入ると、柱が前に来るたびに GAP に切りかわって柱をよけ、よけ終わると WALL にもどりました。はじめの 1 回は、次のように表示されました。

```text
  0.0 秒 >> 壁沿い走行と Gap Follower を切りかえて走ります
 37.8 秒 GAP へ（前の物まで 63 cm）
 38.0 秒 WALL へ（前の物まで 10000 cm）
 43.7 秒 GAP へ（前の物まで 148 cm）
 44.2 秒 WALL へ（前の物まで 326 cm）
 44.7 秒 GAP へ（前の物まで 79 cm）
 45.7 秒 WALL へ（前の物まで 726 cm）
 46.7 秒 GAP へ（前の物まで 148 cm）
 47.4 秒 WALL へ（前の物まで 362 cm）
 48.0 秒 GAP へ（前の物まで 52 cm）
 48.2 秒 WALL へ（前の物まで 302 cm）
 50.4 秒 GAP へ（前の物まで 150 cm）
 50.5 秒 WALL へ（前の物まで 10000 cm）
 57.4 秒 GAP へ（前の物まで 136 cm）
```

（左の数字は、スタートからの秒数です。この本で書き足しました。）

37.8 秒から 50.5 秒の間に、GAP と WALL が何度も入れかわっています。柱をよけると、前の帯から柱が外れて、すぐに `FAR` より遠くなるからです。

### うまくいかなかったこと

- **5 回のうち 1 回は、失敗しました**。とちゅうで向きが逆になり、スタートの所の壁にぶつかりました。ゴールまでの時間も、64〜105 秒と、回によって大きくちがいました。柱の広間は、切りかえても、まだむずかしいコースです
- **もどるときに `reset()` しない**と、ゴールは 2 回に減りました。GAP の間にたまった積分や、ずれた状態が、WALL にもどったときに、ハンドルを変な向きに切らせるためだと考えられます
- **`NEAR` と `FAR` を 120 cm と 200 cm にする**と、ゴールは 3 回でした（この本の設定 150 cm と 250 cm では 4 回）
- **混ぜ合わせ**（`BLEND = True`）は、1 回もゴールできませんでした。前が空いているほど壁沿い走行の角度を多く、物が近いほど Gap Follower の角度を多くして足し合わせましたが、2 つの角度の「間の向き」は、どちらの走り方も選ばなかった向きです。柱をよける向きと、壁に沿う向きの間は、柱にぶつかる向きになることがあります

## ④ 数式・コード

### 混ぜ合わせの割合

`BLEND = True` のときは、前の帯の物までの距離 $a$ から、壁沿い走行の割合 $w$ を

$$
w = \text{clamp}\left(\frac{a - \text{NEAR}}{\text{FAR} - \text{NEAR}},\ 0,\ 1\right)
$$

とし、$\text{angle} = w \cdot \text{angle}_{\text{wall}} + (1 - w) \cdot \text{angle}_{\text{gap}}$ にしています。$a \le 150$ で Gap Follower だけ、$a \ge 250$ で壁沿い走行だけ、その間は両方を混ぜます。

### クラスにまとめる理由

| | 関数（`gap_angle()`） | クラス（`WallSteer`） |
|---|---|---|
| 前のコマの値を覚えるか | 覚えない（毎コマ、LIDAR だけから決まる） | 覚える（PID の積分、6-17 の状態と数） |
| やり直し | 必要ない | `reset()` でまとめてやり直す |

Gap Follower は、その場の LIDAR だけから角度を決めるので、関数で十分です。壁沿い走行は、前のコマからの続きの値を持っているので、クラスにまとめておくと、切りかえのときに扱いやすくなります。

## ⑤ つまずきポイント

### 切りかえを print で確かめない

切りかえるプログラムでは、「今どちらで走っているか」が見た目ではわかりません。この回のプログラムのように、切りかわるたびに `print()` で表示すると、うまくいかないときに、どこで何が起きたかを調べやすくなります（7-2）。

### 2つを混ぜれば、両方のよいところが出る、とは限らない

混ぜ合わせは、なめらかで、よさそうに見えます。でも、この回の実験では、はっきり切りかえるほうがうまくいきました。思いつきは、実験で確かめましょう。

## ⑥ 確認問題

**問1**　コース D の横に入り口のある通路で、`combo_follow.py` が横の部屋に入らないのはなぜですか。

:::details 答え
横の部屋があっても、車の前の帯の中には物がないので、WALL（壁沿い走行）のまま走るからです。壁沿い走行は、壁がとぎれても、見えている側の壁をたどります（6-17）。
:::

**問2**　GAP から WALL にもどるときに `wall.reset()` を呼ぶのはなぜですか。

:::details 答え
GAP の間も `wall.angle()` を呼んでいるので、壁沿い走行の PID には、実際には使われなかった角度の積分がたまり、状態もずれています。そのまま使うと、もどったときにハンドルを変な向きに切ってしまうので、やり直します。
:::

## ⑦ 原典

`wall_steer.py`・`gap_steer.py`・`combo_follow.py`・図1と表の数字は、この本で作ったものです（説明用の簡単なモデル）。`wall_steer.py` は 6-18 の `wall_follow_course.py`、`gap_steer.py` は 7-10 までの `gap_follow.py` のハンドルの決め方を、そのまま部品にしたものです。

- `get_lidar_average_distance()`・`clamp()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）
