---
title: "9-5 実機の物体検出 — 止まれの標識で止まる"
free: true
---

5-11 では、Edge TPU が見つけた物を `rc.vision.get_detections()` で受けとり、コーンのほうへハンドルを切りました。5-14 では、自分のモデルを学習させて、車に入れました。この回では、物体検出の答えで、車の走り方（状態）を切りかえます。止まれの標識を見つけたら 3 秒止まり、また走りだすプログラムを作ります。

物体検出の答えは、ときどきまちがえます。見のがしたり、ない物を「ある」と答えたりします。その答えで車を止めたり走らせたりするときは、答えを 1 回だけ信じるのではなく、「続けて見えたか」を確かめることが大切です。

## ① この回でできるようになること

1. 実機の物体検出の答えが、1 秒に何回新しくなるか、どんなまちがいをするかを説明できる
2. 答えが「続けて」見えた時間を数えて、まちがった答えで止まらないプログラムを作れる
3. 物体検出の答えで、ステートマシンの状態を切りかえられる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| False positive | まちがった「ある」 | 本当はないのに、「ある」と答えること（空振り） |
| False negative | 見のがし | 本当はあるのに、答えに出てこないこと |
| Confirmation | 確かめ | 何回か続けて見えたときだけ、本当にあると考えること |
| Inference rate | 答えの速さ | 物体検出の答えが、1 秒に何回新しくなるか |
| COCO | COCO | 人・車・止まれの標識など 80 種類の物の写真を集めたデータ。はじめから入っているモデルは、これで学習している |

## ③ 本文

### 実機の物体検出の答え

実機の Edge TPU のプログラムは、はじめから、COCO で学習したモデル（EfficientDet-Lite0）を使います。このモデルは、`"person"`（人）・`"traffic light"`（信号）・`"stop sign"`（止まれの標識）などを見つけられます。自分で学習させたモデルに入れかえる方法は、5-14 で学びました。

5-11 で見たとおり、答えは `Detection` のリストで、名前（`class_id`）・自信（`score`）・枠（`bbox`）が入っています。ここでは、走らせるときに気をつけたい、次の3つを確かめておきます。

- **答えは 1 秒に最大 15 回しか新しくならない**：`update()` は 1 秒に約 60 回呼ばれますが、物体検出の答えが新しくなるのは、そのうち 4 回に 1 回くらいです。その間は、同じ答えが返ります
- **見のがす**：遠くて小さく写った物や、ななめから見た物は、答えに出てこないことがあります
- **まちがった「ある」を答える**：標識に似た赤い丸い物などを、`"stop sign"` と答えることがあります。自信が 0.4 より低い答えは、はじめから入っていません（5-11）が、0.5 や 0.6 のまちがいは出てきます

### 1 回見えたら止まる、ではうまくいかない

いちばん簡単なのは、「近くの標識が 1 回でも答えに出たら止まる」プログラムです。この本では、説明用の簡単なモデルで、これを確かめました。

- まっすぐな廊下（幅 150 cm）の、9 m と 18 m のところに、止まれの標識（高さ 20 cm）を置く
- カメラに写る標識の大きさを計算し、4 コマに 1 回（1 秒に 15 回）答えを作る。遠くの小さい標識は、ときどき見のがす
- 平均して 1 秒に 0.15 回、標識がないのに「`stop sign`、自信 0.5〜0.62、枠の高さ 60〜110 画素」という、まちがった答えを出す

![上：標識が1回見えたら止まるプログラムは、60秒で7回止まり、標識の前で止まったのは1回、ほかの6回はまちがった答えで止まった。2つめの標識は、止まったあとの気にしない時間に通りすぎた。下：0.2秒続けて見えたら止まるプログラムは、2つの標識の前でだけ止まった](/images/racecar-neo-jp/9-5/fig1-detect-stop.png)
*図1　説明用の簡単なモデル（標識の見え方と、まちがった答えは、この本で作ったもの）。横は時間、たては廊下を進んだ位置。赤い帯は止まっている 3 秒*

図1の上が、1 回見えたら止まるプログラムです。まちがった答え（オレンジの ×）が出るたびに止まり、60 秒で 7 回止まりました。標識の前で止まったのは 1 回だけです。しかも、2 つめの標識は、まちがった答えで止まったあとの「標識を気にしない時間」に通りすぎてしまいました。

### 0.2 秒続けて見えたら止まる

まちがった答えは、たいてい 1 回（1/15 秒）だけ出て、次の答えでは消えます。本当の標識は、近づくにつれて、何回も続けて答えに出ます。そこで、近くの標識が見えている時間を数えて、0.2 秒（答え 3 回分くらい）続いたときだけ止まることにします。

ただし、本当の標識でも、ときどき見のがします。1 回見のがしただけで数え直すと、なかなか 0.2 秒になりません。そこで、見えない時間が 0.3 秒続いたときだけ、数え直します。

```python:detect_stop.py
"""
detect_stop.py（実機用）
壁に沿って走り（WallSteer、7-13）、Edge TPU が「stop sign」（止まれの標識）を見つけたら、3 秒止まってから、また走る（9-5）。
  DRIVE：壁に沿って走る。近くの標識を CONFIRM_TIME 秒続けて見たら STOP へ
  STOP ：止まる。STOP_TIME 秒たったら PASS へ
  PASS ：標識を気にせずに走る。PASS_TIME 秒たったら DRIVE へ（同じ標識で、もう一度止まらないように）
wall_steer.py・walls.py・pid.py を同じフォルダに置いて使う。RB を押している間だけ、プログラムの命令が車に届く。
"""

import sys
from enum import IntEnum

sys.path.insert(1, "../../library")
import racecar_core
from wall_steer import WallSteer

rc = racecar_core.create_racecar()

TARGET = "stop sign"   # はじめから入っているモデル（COCO）の名前
MIN_SCORE = 0.5        # これより自信が低い答えは使わない
NEAR_HEIGHT = 60       # 枠の高さがこれより大きい（近い）標識だけを相手にする（画素）
CONFIRM_TIME = 0.2     # この時間（秒）続けて見えたら、本当にあると考える
LOST_TIME = 0.3        # この時間（秒）続けて見えなかったら、見えていた時間を 0 にもどす
STOP_TIME = 3.0        # 止まる時間（秒）
PASS_TIME = 3.0        # 止まったあと、標識を気にしない時間（秒）
SPEED = 0.4


class State(IntEnum):
    DRIVE = 0
    STOP = 1
    PASS = 2


state = State.DRIVE
timer = 0.0            # 今の状態になってからの時間（秒）
seen_time = 0.0        # 標識が続けて見えている時間（秒）
lost_time = 0.0        # 標識が続けて見えていない時間（秒）
wall = WallSteer()


def near_sign():
    """近くの TARGET のうち、いちばん自信の高い検出結果を返す。なければ None"""
    best = None
    for det in rc.vision.get_detections():
        if det.class_id == TARGET and det.score >= MIN_SCORE and det.bbox[3] >= NEAR_HEIGHT:
            if best is None or det.score > best.score:
                best = det
    return best


def set_state(new_state):
    global state, timer
    print(f"{new_state.name} へ")
    state = new_state
    timer = 0.0


def start():
    rc.drive.set_max_speed(0.25)      # はじめは上限を小さくしておく（9-1）
    rc.drive.stop()
    set_state(State.DRIVE)
    print(">> 壁に沿って走り、止まれの標識で 3 秒止まります（RB を押している間）")


def update():
    global timer, seen_time, lost_time
    dt = rc.get_delta_time()
    timer += dt
    scan = rc.lidar.get_samples()
    angle = wall.angle(scan, dt)

    # 標識が「続けて」見えている時間を数える（見えたり見えなかったりしても、LOST_TIME までは数え続ける）
    if near_sign() is not None:
        seen_time += dt
        lost_time = 0.0
    else:
        lost_time += dt
        if lost_time > LOST_TIME:
            seen_time = 0.0

    speed = SPEED
    if state == State.DRIVE:
        if seen_time >= CONFIRM_TIME:
            set_state(State.STOP)
    elif state == State.STOP:
        speed = 0.0
        if timer >= STOP_TIME:
            set_state(State.PASS)
    elif state == State.PASS:
        if timer >= PASS_TIME:
            set_state(State.DRIVE)

    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    sign = near_sign()
    print(f"  {state.name}　見えている時間 {seen_time:.2f} 秒　" + ("標識なし" if sign is None else str(sign)))


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

- `near_sign()` は、5-11 の `find_target()` に、枠の高さの条件（`NEAR_HEIGHT`）を足したものです。遠くの標識では止まりません
- `seen_time` が「続けて見えている時間」、`lost_time` が「続けて見えていない時間」です。`lost_time` が `LOST_TIME` をこえたら、`seen_time` を 0 にもどします
- 状態は 3 つです。STOP で 3 秒止まったあと、PASS で 3 秒は標識を気にせずに走ります。PASS がないと、止まった場所にはまだ標識が見えているので、DRIVE にもどったとたん、また止まってしまいます
- ハンドルは、7-13 の `WallSteer` で決めます。止まっている間も `wall.angle()` を呼んで、状態を続けて覚えておきます

図1の下が、`detect_stop.py` です。まちがった答えは 60 秒で 11 回出ましたが、一度も止まらず、2 つの標識の前でだけ止まりました。はじめの標識の前では、次のように表示されました（モデルの値です）。

```text
  DRIVE　見えている時間 0.00 秒　標識なし
STOP へ
  STOP　見えている時間 0.30 秒　Detection(class_id='stop sign', score=0.83, bbox=(521, 200, 68, 68))
  STOP　見えている時間 1.03 秒　Detection(class_id='stop sign', score=0.87, bbox=(534, 200, 72, 72))
  STOP　見えている時間 1.90 秒　Detection(class_id='stop sign', score=0.72, bbox=(535, 200, 72, 72))
PASS へ
  PASS　見えている時間 2.63 秒　Detection(class_id='stop sign', score=0.89, bbox=(538, 200, 73, 73))
```

5 回ずつ（まちがった答えの出方を変えて）走らせた結果は、次のとおりです。

| | 標識の前で止まった | 標識のない所で止まった | 止まらずに通りすぎた標識 |
|---|---|---|---|
| 1 回見えたら止まる | 10 回のうち 9 回 | 22 回 | 1 回 |
| `detect_stop.py`（0.2 秒続けて） | 10 回のうち 10 回 | 0 回 | 0 回 |

### 実機で動かすときは

1. はじめは車を持ち上げて（車輪を浮かせて）、カメラの前に標識の写真を持っていき、STOP・PASS・DRIVE と切りかわるか確かめる
2. 標識の写真を、印刷して壁に貼る。紙の大きさ（写る大きさ）で `NEAR_HEIGHT` がどの距離にあたるか、`update_slow()` の表示の `bbox` の高さで確かめる
3. コースに、赤くて丸い物（まちがえやすい物）を置いて、止まらないか確かめる
4. 物体検出だけに頼らない。LIDAR で前の物に近づいたら止まるしくみ（7-1）も残しておき、いつでも RB をはなせるようにする

## ④ 数式・コード

### 写る大きさと距離

カメラの焦点距離（画素）を $f$、標識の高さを $H$、標識までの前向きの距離を $d$ とすると、写る高さ $h$（画素）は次のとおりです（6-3）。

$$
h = \frac{f H}{d}
\qquad\Longleftrightarrow\qquad
d = \frac{f H}{h}
$$

このモデルでは $f = 466$ 画素、$H = 20$ cm なので、`NEAR_HEIGHT` = 60 画素は $d = 466 \times 20 \div 60 \approx 155$ cm です。実際に、はじめの標識の約 143 cm 手前で止まりました（止まれと決めてから、車が止まるまでに少し進みます）。

### まちがった答えで止まる確率

まちがった答えが、答え 1 回あたり確率 $p$ で出て、次の答えとは関係なく出るとします。1 回のまちがいは 4 コマ（約 0.067 秒）続くので、`seen_time` が 0.2 秒になるには、まちがいが 3 回ほど、あまり間をあけずに出る必要があります。簡単のために、3 回続けて出る確率で考えると $p^3$ です。このモデルの $p = 0.01$ なら、$0.01^3 = 0.000001$ で、1 秒に 15 回答えるとしても、おおよそ $1 \div (15 \times 0.000001) \approx 67000$ 秒（約 18 時間）に 1 回です。1 回見えたら止まるプログラムは、$1 \div (15 \times 0.01) \approx 6.7$ 秒に 1 回のまちがいで、そのたびに止まろうとします。

ただし、実際のまちがいは「関係なく」出るとはかぎりません。標識に似た物が置いてあれば、その前を通るたびに、続けて「ある」と答えます。コースで確かめることが大切です（③の「実機で動かすときは」の3）。

## ⑤ つまずきポイント

### 名前が合わない

`TARGET` は、ラベルのファイルに書かれた名前と、1 文字もちがわないようにします。COCO の名前は `"stop sign"`（小文字、間に空白）です。`"stop_sign"` や `"Stop Sign"` では見つかりません。自分で学習させたモデルなら、5-13 で付けた名前にします。

### 止まったあと、動かなくなる

PASS がないか、`PASS_TIME` が短すぎると、止まった場所で見えている同じ標識で、また止まります。PASS の間に、標識がカメラの外に出る（または `NEAR_HEIGHT` より小さくなる）ように、`PASS_TIME` と速さを決めましょう。

### 近づいても、止まらない

標識に近づきすぎると、カメラの横の外に出て、答えに出なくなります。`NEAR_HEIGHT` を大きくしすぎると、その前に止まる条件がそろいません。表示の `bbox` を見て、写る高さを確かめましょう。

### シミュレータで `AttributeError` が出る

シミュレータの `rc` には `vision` がありません（5-11）。このプログラムは実機で動かします。

## ⑥ 確認問題

**問1**　`update()` が 1 秒に 60 回呼ばれ、物体検出の答えが 1 秒に 15 回新しくなるとき、同じ答えは何回続けて返りますか。

:::details 答え
$60 \div 15 = 4$ 回です。そのため、まちがった答えが 1 回出ると、4 コマ（約 0.067 秒）の間、同じまちがいが返ります。`CONFIRM_TIME` を 0.2 秒にしたのは、これより十分長くするためです。
:::

**問2**　`LOST_TIME` を 0 にすると、何が起きやすくなりますか。

:::details 答え
本当の標識を 1 回見のがしただけで、`seen_time` が 0 にもどります。見のがしが多いと、なかなか 0.2 秒続けて見えず、止まるのがおそくなったり、標識がカメラの外に出て、止まらずに通りすぎたりします。
:::

**問3**　写る高さが 40 画素の標識までの距離を、このモデルの値（$f = 466$、$H = 20$ cm）で求めましょう。この標識で止まりますか。

:::details 答え
$466 \times 20 \div 40 = 233$ cm です。`NEAR_HEIGHT`（60 画素）より小さいので、まだ止まりません。
:::

## ⑦ 原典

- `rc.vision.get_detections()`・`Detection`（名前・自信・枠、最新の答えを返す）：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `vision.py`・`real/vision_real.py`（GPL-3.0）
- Edge TPU のプログラム（1 秒に最大 15 回、自信のしきい値 0.4、はじめから入っている COCO のモデルとラベル）：[racecar_neo_ros2_driver](https://github.com/MITRacecarNeo/racecar_neo_ros2_driver) の Edge TPU の設定（GPL-3.0）

`detect_stop.py` は、この本で作ったものです。図1・表・表示の例は、この本で作った説明用の簡単なモデル（上から見た2次元の車と壁、標識の写る大きさの計算、見のがしとまちがった答えの出方）によるもので、実際の Edge TPU の値ではありません。
