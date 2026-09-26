---
title: "7-1 LIDAR で衝突を防ぐ（安全停止）"
free: true
---

第6章の壁沿い走行は、「まわりにあるのは壁だけ」と考えて作りました。でも、実際のコースには、ほかの車や、置き忘れた箱や、人の足があるかもしれません。この回では、どんなプログラムにも足せる**安全停止**を作ります。車の前に物が近づいたら、ほかのプログラムが何を命令していても、前へ進むのをやめさせる「安全装置」です。

## ① この回でできるようになること

1. 車の前の「帯」の中にある物までの距離を、LIDAR で求められる
2. ブレーキテストで、車が止まるまでに進む距離を測れる
3. 速さに合わせて、ブレーキをかけはじめる距離を決められる
4. 安全停止を、ほかのプログラムに組みこめる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Safety stop | 安全停止 | ぶつかりそうなときに、ほかの命令より優先して止めること |
| Stopping distance | 止まるまでの距離（停止距離） | ブレーキをかけてから、車が止まるまでに進む距離 |
| Latency | 遅れ | 物が近づいてから、プログラムがそれに気づくまでの時間 |
| Override | 上書き | ほかの部分が決めた命令を、あとから書きかえること |

## ③ 本文

### 正面の「扇」ではなく、車の前の「帯」を見る

6-15 や 6-18 では、正面 ±10° の中でいちばん近い点を、正面の壁までの距離にしました。壁にはこれで十分ですが、ぶつからないためには、少し足りません。

- 遠くでは、±10° の扇は車の幅より広くなります。車が通らない所の物にも反応します
- 近くでは、扇は車の幅よりせまくなります。車の角（かど）の前にある物を見のがします

そこで、**車の幅と同じくらいの帯**を、車の前にのばして考えます。LIDAR の点ごとに、角度 $\theta$ と距離 $d$ から、「前向きにどれだけ先か」と「横にどれだけずれているか」を計算します（5-3、6-5 の三角比）。

$$
\text{前向き} = d \cos\theta, \qquad \text{横向き} = d \sin\theta
$$

横向きのずれが帯の幅の半分より小さい点だけを集めて、その中でいちばん小さい「前向き」が、車の前にある物までの距離です。

```python
def lidar_angles(scan):
    """LIDAR の各点の角度（ラジアン）。0 が正面、時計回り。
    点の数は len(scan) から求める（シミュレータは 720 点、実機は 1080 点。9-3）"""
    return np.radians(np.arange(len(scan)) * 360 / len(scan))


def distance_ahead(scan):
    """車の前の、幅 2 × HALF_WIDTH の帯の中で、いちばん近い物までの前向きの距離（なければ 10000）"""
    angles = lidar_angles(scan)
    forward = scan * np.cos(angles)          # 前向きの距離
    side = scan * np.sin(angles)             # 横向きの距離（＋：右）
    inside = (scan > 0) & (forward > 0) & (np.abs(side) < HALF_WIDTH)
    if not inside.any():
        return 10000.0
    return float(forward[inside].min())
```

- `lidar_angles()` は、LIDAR の点の数（`len(scan)`）から、各点の角度を求めます。シミュレータは 720 点ですが、実機は 1080 点なので（9-3）、720 と決めつけて書かないようにしています
- NumPy の配列の計算（5-7）で、すべての点をまとめて計算しています。`scan * np.cos(angles)` は、点それぞれの「前向き」の配列です
- `inside` は、条件に合う点が `True` になる配列です。`&` は「かつ」です。0.0（測れなかった点）と、後ろ（前向きが負）の点は、はじめから入れません
- `forward[inside]` で、帯の中の点の「前向き」だけを取り出して、いちばん小さい値を返します

![上から見た図。車が下の真ん中にいて、前に幅 40 cm の帯（オレンジ）がのびている。前方 250〜330 cm にななめの壁があり、帯の中の小さな柱が車の 150 cm 先の少し右にある。左の 110 cm 先にも柱があるが、帯の外にある。LIDAR の点は灰色、帯の中の点はオレンジで、帯の中でいちばん近い点（柱の手前、前向きに 141 cm）に丸がついている](/images/racecar-neo-jp/7-1/fig1-band.png)
*図1　車の前の帯の中だけを見る（説明用の簡単なモデル）*

図1では、左前の柱は帯の外にあるので、そのまま進んでもぶつかりません。右前の柱は帯の中にあるので、このまま進むとぶつかります。帯の中でいちばん近い点は、その柱の手前の、前向きに 141 cm の所です。

### ブレーキテスト：車はすぐには止まれない

speed を 0 にしても、車はすぐには止まりません。さらに、LIDAR の値は 1 秒に 6 回転しながら少しずつ新しくなるので（6-6、6-8）、壁が近づいたことに気づくのも、少し遅れます。そこで、「ブレーキをかけてから、どれだけ進むか」を測ります。

```python:brake_test.py
"""
brake_test.py
決まった speed で壁に向かってまっすぐ走り、正面の壁が BRAKE_AT より近くなったら speed を 0 にする。
止まるまでに進んだ距離を表示する（7-1）。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

SPEED = 0.5            # 試す速さ
BRAKE_AT = 150.0       # 正面の壁がこれより近くなったら、ブレーキ（cm）

braking = False        # ブレーキをかけたあとか
front_at_brake = 0.0   # ブレーキをかけたときの、正面の壁までの距離
last_front = 0.0       # 0.5 秒前の、正面の壁までの距離（止まったかを調べる）
done = False           # 結果を表示したか


def front_distance(scan):
    """正面 ±5° の平均の距離（ばらつきを小さくするため、いちばん近い点ではなく平均を使う）"""
    return rc_utils.get_lidar_average_distance(scan, 0, 10)


def start():
    global braking, done
    braking = False
    done = False
    rc.drive.stop()
    rc.set_update_slow_time(0.5)
    print(f">> speed {SPEED} で走り、壁まで {BRAKE_AT:.0f} cm でブレーキをかけます")


def update():
    global braking, front_at_brake
    front = front_distance(rc.lidar.get_samples())
    if not braking and 0 < front < BRAKE_AT:
        braking = True
        front_at_brake = front
        print(f"ブレーキ！　正面の壁まで {front:.1f} cm")
    if braking:
        rc.drive.set_speed_angle(0.0, 0.0)
    else:
        rc.drive.set_speed_angle(SPEED, 0.0)


def update_slow():
    global last_front, done
    front = front_distance(rc.lidar.get_samples())
    if braking and not done and abs(front - last_front) < 1.0:
        print(f"止まった：正面の壁まで {front:.1f} cm　ブレーキから {front_at_brake - front:.1f} cm 進んだ")
        done = True
    last_front = front


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

説明用のモデルで、壁から 400 cm の所から speed 0.5 で走らせると、次のように表示されました。

```text
>> speed 0.5 で走り、壁まで 150 cm でブレーキをかけます
ブレーキ！　正面の壁まで 144.4 cm
止まった：正面の壁まで 125.9 cm　ブレーキから 18.6 cm 進んだ
```

速さを変えて、それぞれ 5 回ずつ測りました（図2の左）。

| speed | プログラムの表示（5 回） | 本当に進んだ距離（5 回の最大） |
|---|---|---|
| 0.25 | 8.2〜11.1 cm | 12.5 cm |
| 0.5 | 18.5〜19.5 cm | 25.0 cm |
| 0.75 | 27.9〜30.5 cm | 30.0 cm |
| 1.0 | 38.3〜39.7 cm | 50.0 cm |

「本当に進んだ距離」は、本当の距離が 150 cm になった所から、止まった所までです。プログラムは、LIDAR の遅れのぶん、少しあとで「150 cm より近い」と気づくので、プログラムの表示よりも長くなることがあります。速いほど、止まるまでの距離は長くなります。

:::message
シミュレータや実物の車では、止まるまでの距離は、このモデルとはちがいます。`brake_test.py` で、自分の車の値を測りましょう。シミュレータには本当の距離を表示する機能がないので、何回か測って、いちばん長い値に余裕を足して使います。
:::

### 速さに合わせて、ブレーキをかけはじめる

表から、speed 1.0 では 50 cm 進んでしまいます。止まっていても少し余裕を残したいので、ブレーキをかけはじめる距離を、次のように決めます。

$$
\text{止まるのに必要な距離} = \text{STOP\_BASE} + \text{STOP\_PER\_SPEED} \times \text{speed}
$$

このモデルでは、`STOP_BASE = 15`、`STOP_PER_SPEED = 60` にしました。speed 1.0 なら 75 cm、speed 0.5 なら 45 cm です。帯の中の物がこれより近くなったら、前へ進む命令を 0 に**上書き**します。

```python:safety_stop.py
"""
safety_stop.py
人がコントローラーで運転し、車の前の帯の中に物が近づいたら、プログラムが前へ進むのを止める（7-1）。
右トリガー：前へ　左トリガー：後ろへ　左スティック：ハンドル
"""

import sys

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core

rc = racecar_core.create_racecar()

MAX_SPEED = 1.0        # トリガーをいっぱいに押したときの speed
HALF_WIDTH = 20.0      # 帯の幅の半分：車の幅の半分 ＋ 余裕（cm）
STOP_BASE = 15.0       # 止まっているときでも、これより近づかない（cm）
STOP_PER_SPEED = 60.0  # speed 1.0 あたり、止まるのに必要な距離（cm）。ブレーキテストで決める


def lidar_angles(scan):
    """LIDAR の各点の角度（ラジアン）。0 が正面、時計回り。
    点の数は len(scan) から求める（シミュレータは 720 点、実機は 1080 点。9-3）"""
    return np.radians(np.arange(len(scan)) * 360 / len(scan))


stopped = False        # 安全停止が働いているか
ahead = 0.0            # 帯の中でいちばん近い物までの、前向きの距離


def distance_ahead(scan):
    """車の前の、幅 2 × HALF_WIDTH の帯の中で、いちばん近い物までの前向きの距離（なければ 10000）"""
    angles = lidar_angles(scan)
    forward = scan * np.cos(angles)          # 前向きの距離
    side = scan * np.sin(angles)             # 横向きの距離（＋：右）
    inside = (scan > 0) & (forward > 0) & (np.abs(side) < HALF_WIDTH)
    if not inside.any():
        return 10000.0
    return float(forward[inside].min())


def start():
    global stopped
    stopped = False
    rc.drive.stop()
    print(">> 右トリガーで前へ。前に物が近づくと、自動で止まります")


def update():
    global stopped, ahead
    rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    speed = (rt - lt) * MAX_SPEED
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]

    # 安全停止：前へ進もうとしていて、帯の中の物が、止まるのに必要な距離より近いなら、前へは進ませない
    ahead = distance_ahead(rc.lidar.get_samples())
    need = STOP_BASE + STOP_PER_SPEED * max(speed, 0.0)
    if speed > 0 and ahead < need:
        speed = 0.0
        if not stopped:
            print(f"安全停止！　前の物まで {ahead:.1f} cm")
        stopped = True
    else:
        stopped = False

    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    print(f"前の物まで {ahead:7.1f} cm　安全停止 {'中' if stopped else 'なし'}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

- 人がトリガーとスティックで運転します（3-2）。安全停止は、人の命令を、`rc.drive.set_speed_angle()` の直前に書きかえます
- 後ろへ下がる命令（speed が 0 以下）は、止めません。前に物があっても、下がって離れられるようにするためです

右トリガーをいっぱいに押したまま、壁に向かって走らせると、次のように表示されました（speed 1.0）。

```text
>> 右トリガーで前へ。前に物が近づくと、自動で止まります
前の物まで   395.5 cm　安全停止 なし
前の物まで   282.0 cm　安全停止 なし
前の物まで   130.9 cm　安全停止 なし
安全停止！　前の物まで 62.4 cm
前の物まで    30.6 cm　安全停止 中
前の物まで    26.3 cm　安全停止 中
```

![左は、ブレーキテストの結果の棒グラフ。speed 0.25、0.5、0.75、1.0 で、プログラムの表示は 11、20、30、40 cm、本当に進んだ距離は 13、25、30、50 cm。右は、speed 1.0 で壁に向かって走ったときの、車の前のはしから壁までの距離のグラフ。止まる距離をいつも 30 cm にしたとき（灰色）は、そのまま 0 cm まで近づいてぶつかる。止まる距離を速さに合わせたとき（オレンジ）は、2.5 秒ごろからなめらかに速さが落ちて、壁の 16 cm 手前で止まる](/images/racecar-neo-jp/7-1/fig2-stop.png)
*図2　ブレーキテスト（左）と、speed 1.0 で壁に向かって走ったとき（右）*

「いつも 30 cm でブレーキ」では、speed 1.0 のときに止まりきれず、壁にぶつかりました（図2の右の灰色）。速さに合わせると、車の前のはしから壁まで 16 cm の所で止まりました。

帯の幅も確かめました。車のまっすぐ前、横に 15 cm ずれた所に柱を置くと、安全停止が働いて止まりました。横に 30 cm ずれた所に置くと、止まらずに横を通りぬけました。

### ほかのプログラムに組みこむ

安全停止は、「最後に speed を書きかえる」だけなので、どんなプログラムにも足せます。`update()` の最後で、speed と angle が決まってから、次の3行を入れます。

```python
    ahead = distance_ahead(rc.lidar.get_samples())
    if speed > 0 and ahead < STOP_BASE + STOP_PER_SPEED * speed:
        speed = 0.0
```

第6章の壁沿い走行にも、この章の Gap Follower にも使えます。ほかの部分がまちがった命令を出しても、ここで止められるように、**いちばん最後**に置くのがポイントです。

## ④ 数式・コード

### 止まるまでの距離の考え方

自動車の教習所では、止まるまでの距離を、2つに分けて考えます。

$$
\text{止まるまでの距離} = \underbrace{v \times t_{\text{遅れ}}}_{\text{気づくまでに進む}} + \underbrace{\frac{v^2}{2a}}_{\text{ブレーキで進む}}
$$

$v$ は速さ、$t_{\text{遅れ}}$ は気づくまでの時間、$a$ はブレーキで速さが落ちる割合（減速度）です。気づくまでに進む距離は速さに比例し、ブレーキで進む距離は速さの2乗に比例します。この回の式（STOP_BASE ＋ STOP_PER_SPEED × speed）は、速さに比例する部分だけの、かんたんな近似です。もっと速く走るときは、2乗の部分が大きくなるので、ブレーキテストの結果に合わせて、式を見直しましょう。

### 帯は、車の軌跡の近似

ハンドルを切っているときは、車はまっすぐ前ではなく、弧をえがいて進みます。この回の帯は「まっすぐ進む」と考えたものなので、急に曲がっている間は、曲がる先の物を見のがすことがあります。ハンドルの角度から、曲がる先に帯を曲げる方法もありますが、まずは速さを上げすぎないことが大切です。

## ⑤ つまずきポイント

### とても近い物は、0.0 になる

シミュレータの LIDAR は、12 cm より近い物を 0.0（測れなかった）にします（6-4）。`distance_ahead()` は 0.0 の点を使わないので、物が車にほとんどくっついていると、「何もない」と判断してしまいます。安全停止が働いて止まったあと、さらに近づくことがないように、止まる距離を 12 cm より十分大きくしておきましょう。

### せまい通路で、いつも止まってしまう

`HALF_WIDTH` を大きくしすぎると、せまい通路では、横の壁が帯の中に入って、ずっと安全停止が働きます。帯の幅は、車の幅に少しの余裕を足したくらいにします。

### 後ろに下がるときにぶつかる

この回の安全停止は、前にしか働きません。後ろに下がるプログラムでは、`scan` の後ろ側（前向きが負の点）で、同じように帯を作って調べます（7-2 の `patrol.py`）。

## ⑥ 確認問題

**問1**　LIDAR の点が、右 30° の向きに 100 cm の所にありました。前向きと横向きの距離はいくつですか。帯の幅の半分が 20 cm なら、帯の中に入りますか。

:::details 答え
前向きは $100 \cos 30° \approx 86.6$ cm、横向きは $100 \sin 30° = 50$ cm です。横に 50 cm ずれているので、20 cm の帯には入りません。
:::

**問2**　`STOP_BASE = 15`、`STOP_PER_SPEED = 60` のとき、speed 0.75 で走っていたら、帯の中の物が何 cm より近くなるとブレーキをかけますか。

:::details 答え
$15 + 60 \times 0.75 = 60$ cm です。
:::

**問3**　安全停止のコードを、`update()` の最初に置くと、どんな問題が起きますか。

:::details 答え
あとから、ほかの部分が speed を決め直すと、安全停止で 0 にした speed が上書きされてしまいます。いちばん最後に置けば、何があっても安全停止が優先されます。
:::

## ⑦ 原典

- シミュレータの LIDAR（12 cm より近い点と 10 m より遠い点は 0.0、1 秒に 6 回転、約 2% のばらつき）：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `Lidar.cs`（6-4、6-6）

`brake_test.py`・`safety_stop.py`・図1・図2と表の数字は、この本で作ったものです（説明用の簡単なモデル）。
