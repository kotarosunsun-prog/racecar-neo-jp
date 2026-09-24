---
title: "5-5 IMU で傾きと向きを測る — 相補フィルタ"
free: true
---

IMU（慣性計測装置）は、車がどう動いているかを、車の中だけで測るセンサです。カメラや LIDAR のように外を見るのではなく、自分の体の動きを感じとります。この回では、IMU の値から車の**傾き**と**向き**を求めます。そして、2つの測り方の弱点をたがいに補い合う**相補フィルタ**を作ります。夏のプログラムの課題「BYOA（Build Your Own AHRS）」の中心になる考え方です。

## ① この回でできるようになること

1. IMU が測る2つの量（加速度と角速度）と、軸の向きを説明できる
2. 加速度から、重力の向きを使って傾きを求める考え方を説明できる
3. 角速度を毎コマ足し合わせて、車がどれだけ回ったかを求められる
4. 2つを組み合わせる相補フィルタを作り、そのはたらきを説明できる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| IMU | 慣性計測装置 | 加速度センサとジャイロを組み合わせた部品 |
| Accelerometer | 加速度センサ | 速さの変わり方（と重力）を測る |
| Gyroscope | ジャイロ | 回る速さ（角速度）を測る |
| Magnetometer | 地磁気センサ | 地球の磁石の向きを測る。方位磁針と同じ |
| Roll / Pitch / Yaw | ロール／ピッチ／ヨー | 左右の傾き／前後の傾き／向き（左右どちらを向いているか） |
| Drift | ドリフト | 足し合わせるうちに、ずれがだんだん大きくなること |
| Bias | バイアス | 止まっていても出てしまう、決まったずれ |
| Complementary filter | 相補フィルタ | 2つの測り方を、得意なところだけ使って混ぜる方法 |

## ③ 本文

### IMU が測るもの

RACECAR のライブラリでは、次の2つの関数で IMU の値を読みます。

| 関数 | 測るもの | 単位 |
|---|---|---|
| `rc.physics.get_linear_acceleration()` | 3つの軸の方向の加速度（重力を含む） | m/s² |
| `rc.physics.get_angular_velocity()` | 3つの軸のまわりに回る速さ | rad/s（ラジアン毎秒） |

どちらも、3つの数の組 `(x, y, z)` を返します。**軸の向きは、シミュレータと実機で違う**ので注意が必要です。

| 軸 | シミュレータ | 実機 |
|---|---|---|
| x | 車の右 | 車の前 |
| y | 真上 | 車の右 |
| z | 車の前 | 真上 |

たとえば「車の向きが変わる速さ（ヨーの角速度）」は、シミュレータでは `get_angular_velocity()[1]`（y）、実機では `[2]`（z）です。シミュレータでは、左に曲がるときにプラスになります。

実機には、地磁気センサもあります（`rc.physics.get_magnetic_field()`、単位はテスラ）。シミュレータにはありません。

### まず、値を見てみよう

```python:imu_check.py
"""
imu_check.py
0.5秒ごとに、IMU の加速度と角速度を表示する。トリガーとスティックで車を動かせる。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core

rc = racecar_core.create_racecar()


def start():
    rc.drive.stop()
    rc.set_update_slow_time(0.5)
    print(">> 0.5秒ごとに、加速度（m/s²）と角速度（rad/s）を表示します")


def update():
    # 手動で動かす（3-2 と同じ）
    speed = (rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
             - rc.controller.get_trigger(rc.controller.Trigger.LEFT)) * 0.5
    (x, y) = rc.controller.get_joystick(rc.controller.Joystick.LEFT)
    rc.drive.set_speed_angle(speed, x)


def update_slow():
    ax, ay, az = rc.physics.get_linear_acceleration()
    wx, wy, wz = rc.physics.get_angular_velocity()
    print(f"加速度 x {ax:6.2f}  y {ay:6.2f}  z {az:6.2f}   "
          f"角速度 x {wx:5.2f}  y {wy:5.2f}  z {wz:5.2f}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

シミュレータで止まっているとき、加速度の y はおよそ −9.81 になります。車は動いていないのに値が出るのは、**重力**を測っているからです。前に加速すると z が、左に曲がると角速度の y が変わります。

### 傾きを測る：重力の向きを使う

止まっている車にはたらく加速度は、重力だけです。重力はいつも真下を向いているので、車が傾くと、重力が車の軸のどれにどれだけ分かれて入るかが変わります。

たとえば、車が前を上げて $\theta$ だけ傾くと、重力のうち「車の前向きの軸」に入る分が増え、「車の上下の軸」に入る分が減ります。この2つの比から、傾きを求められます（④）。

ただし、この方法には弱点が2つあります。

- **ばらつきが大きい**：加速度センサの値は、車の振動などで細かくゆれる
- **加速するとだまされる**：車が前に加速すると、その加速度も一緒に測ってしまう。すると、傾いていないのに「傾いた」と計算してしまう

### 回った角度を測る：角速度を足し合わせる

ジャイロは、回る速さを測ります。「回る速さ × 時間 ＝ 回った角度」なので、毎コマ、回った角度を足し合わせていけば、スタートからどれだけ回ったかがわかります。第3章で、経過時間を毎コマ足し合わせたのと同じ考え方です。

次のプログラムは、シミュレータで、車の向きがスタートからどれだけ変わったかを求めます。

```python:heading.py
"""
heading.py
ジャイロ（角速度）を毎コマ足し合わせて、車がスタートからどれだけ回ったか（向き）を求める。
シミュレータ用。左回りをプラスにする。A ボタン（キーボードの 1）で向きを 0 にもどす。
"""

import sys
import math

sys.path.insert(1, "../../library")
import racecar_core

rc = racecar_core.create_racecar()

heading = 0.0   # 向き（度）。スタートしたときを 0 とする


def start():
    global heading
    rc.drive.stop()
    heading = 0.0
    rc.set_update_slow_time(0.5)
    print(">> 車を動かして、向きの変化を見ます（A ボタンで 0 にもどす）")


def update():
    global heading

    # 手動で動かす（3-2 と同じ）
    speed = (rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
             - rc.controller.get_trigger(rc.controller.Trigger.LEFT)) * 0.5
    (x, y) = rc.controller.get_joystick(rc.controller.Joystick.LEFT)
    rc.drive.set_speed_angle(speed, x)

    # シミュレータでは、角速度の 1 番め（y 軸）が、上下の軸のまわりに回る速さ（rad/秒）
    yaw_rate = rc.physics.get_angular_velocity()[1]

    # 回る速さ × 時間 ＝ そのコマで回った角度。これを足し合わせる
    heading += math.degrees(yaw_rate) * rc.get_delta_time()

    if rc.controller.was_pressed(rc.controller.Button.A):
        heading = 0.0
        print("向きを 0 にもどしました")


def update_slow():
    print(f"向き：{heading:.1f}°")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

`math.degrees()` は、ラジアンを度に直す関数です。たとえば、左に 1 rad/s（約 57.3°/s）で2秒回り続けると、向きは約 114.6° になります。ハンドルを切ったまま1周して、向きが 360° に近くなるか確かめてみましょう。

4-2 では、向きのずれが、命令だけで走るときの大きな問題でした。IMU で向きを測れば、「90° 回ったら曲がるのをやめる」のように、**回った角度を見ながら**曲がれます。

ただし、足し合わせる方法にも弱点があります。

- **ドリフト**：実機のジャイロには、止まっていても小さな値が出るくせ（**バイアス**）があります。それを毎コマ足し合わせるので、時間がたつほど、ずれがどんどん大きくなります

### 相補フィルタ：2つのよいところを合わせる

2つの測り方は、得意なところが正反対です。

| 測り方 | 短い時間では | 長い時間では |
|---|---|---|
| 加速度（重力の向き） | ばらつく・加速にだまされる（苦手） | 平均すると正しい（得意） |
| ジャイロ（足し合わせ） | なめらかで正確（得意） | だんだんずれる（苦手） |

そこで、**短い時間の変化はジャイロ**で、**長い時間の基準は加速度**で決めます。毎コマ、次のように計算します。

1. 前のコマの角度に、ジャイロで測った「このコマで回った角度」を足す（ジャイロで進める）
2. その結果と、加速度から求めた角度を、98：2 のように混ぜる（加速度で少しだけ引き戻す）

$$
\theta_{\text{新}} = \alpha \left( \theta_{\text{前}} + \omega \, \Delta t \right) + (1 - \alpha)\, \theta_{\text{加速度}}
$$

$\omega$ はジャイロの角速度、$\Delta t$ は1コマの時間、$\alpha$ はジャイロをどれだけ信じるかを表す 0〜1 の数です。0.98 のように、1 に近い値にします。

![同じ動きを3つの方法で測った結果。本当の傾きは、2秒から3秒で0度から10度に上がり、7秒から8秒で0度に戻る。加速度だけの線は細かくばらつき、加速中の4秒から5秒では大きく上にずれる。ジャイロだけの線はなめらかだが、時間とともに上にずれていき、12秒後には約9.5度ずれている。相補フィルタの線は、本当の傾きのそばをなめらかに追いかけ、加速中も小さなずれですんでいる](/images/racecar-neo-jp/5-5/fig1-comp-filter.png)
*図1　加速度だけ・ジャイロだけ・相補フィルタで、同じ傾きを測った結果（説明用に作ったデータ）*

図1の相補フィルタの線は、加速度だけの線のようにばらつかず、ジャイロだけの線のようにずれていきません。ジャイロのずれは、毎コマ少しずつ加速度に引き戻されて消え、加速度のばらつきは、2% ずつしか入らないので、ならされて小さくなります。

### 夏のプログラムの課題：comp_filter.py

夏のプログラムでは、実機で動く ROS 2 のノード（2-5）として、相補フィルタを作ります。課題のファイル `comp_filter.py` の流れは次のとおりです。

1. IMU のトピックと、地磁気センサのトピック `/mag` を受けとる
2. IMU の値が届くたびに、前回からの時間 $\Delta t$ を求める
3. 加速度から、ロール（左右の傾き）とピッチ（前後の傾き）を求める
4. ジャイロを足し合わせて、ロール・ピッチ・ヨーを求める
5. 地磁気センサと加速度から、ヨー（向き）を求める
6. 相補フィルタで混ぜて、`/attitude` というトピックに送る（ロール・ピッチ・ヨーを度で）

ヨーには、重力のような「基準」がありません（車がどちらを向いても、重力は真下のままだからです）。そこで、地球の磁石の向きを測る地磁気センサを、方位磁針のように基準として使います。

:::message alert
**訳注：実機のトピック名**
ひな形は `/imu` というトピックを受けとるように書かれていますが、今の実機のドライバでは、IMU の値は `/imu/fused`（2つの IMU を混ぜたもの）や `/imu/lsm9ds1` という名前で送られています。実機で動かすときは、`ros2 topic list` でトピックの名前を確かめて、書きかえましょう。また、このファイルの先頭には「MIT License」と書かれていますが、リポジトリ全体のライセンスは GPL-3.0 です。
:::

## ④ 数式・コード

### 重力から傾きを求める式

車が前を上げて $\theta$ だけ傾いているとき、重力の大きさを $g$（約 9.81 m/s²）とすると、重力は車の軸に次のように分かれて入ります。

$$
\text{前後の軸の成分} = g \sin\theta, \qquad \text{上下の軸の成分} = g \cos\theta
$$

この2つの比が $\tan\theta$ なので、角度は次の式で求められます。

$$
\theta = \operatorname{atan2}(\text{前後の軸の成分},\ \text{上下の軸の成分})
$$

`atan2(a, b)` は、$\tan\theta = \frac{a}{b}$ となる角度を、$a$ と $b$ の符号まで考えて求める関数で、Python では `math.atan2(a, b)` です（結果はラジアン）。どの軸の値をプラス・マイナスどちら向きで入れるかは、センサの軸の決まりで変わります。実機では、車を手でゆっくり傾けて、求めた角度の符号が正しいかを確かめましょう。

### 相補フィルタを、作ったデータで試す

次のプログラムは、実機もシミュレータも使わずに、作ったデータで相補フィルタを試します。図1は、このデータで描いたものです。本当の傾きは 0° → 10° → 0° と変わります。加速度から求めた傾きには ±2° ほどのばらつきと、加速中のうそのずれを、ジャイロには 0.8°/秒のバイアスを入れてあります。

```python:comp_demo.py
"""
comp_demo.py
作ったデータで、相補フィルタのはたらきを確かめる（実機・シミュレータは使わない）。
本当の傾きは 0° → 10° → 0° と変わる。加速度から求めた傾きはばらつきが大きく、
車が加速している間はうそのずれが出る。ジャイロには、少しずつずれていくくせ（バイアス）がある。
"""

import numpy as np

DT = 1 / 60          # 1コマの時間（秒）
ALPHA = 0.98         # ジャイロをどれだけ信じるか（0〜1）

rng = np.random.default_rng(0)
t = np.arange(0, 12, DT)                                   # 0〜12秒
true = np.interp(t, [0, 2, 3, 7, 8, 12], [0, 0, 10, 10, 0, 0])   # 本当の傾き（度）
rate = np.gradient(true, DT)                               # 本当の、傾きが変わる速さ（度/秒）

gyro = rate + 0.8 + rng.normal(0, 0.5, len(t))             # ジャイロ：バイアス 0.8 度/秒 ＋ ばらつき
acc = true + rng.normal(0, 2.0, len(t))                    # 加速度から求めた傾き：ばらつき 2 度
acc[(t > 4) & (t < 5)] += 6                                # 4〜5秒は加速中で、うそのずれが出る


def complementary(angle, gyro_rate, acc_angle, dt, alpha):
    """1コマ分の相補フィルタ：ジャイロで進めて、加速度で少しだけ引き戻す"""
    return alpha * (angle + gyro_rate * dt) + (1 - alpha) * acc_angle


gyro_only = np.zeros(len(t))
fused = np.zeros(len(t))
for k in range(1, len(t)):
    gyro_only[k] = gyro_only[k - 1] + gyro[k] * DT                         # ジャイロだけ（足し合わせる）
    fused[k] = complementary(fused[k - 1], gyro[k], acc[k], DT, ALPHA)     # 相補フィルタ


def rms(x):
    return np.sqrt(np.mean((x - true) ** 2))   # 本当の傾きとのずれの大きさ（二乗平均の平方根）


print(f"加速度だけ　のずれ：{rms(acc):.2f} 度")
print(f"ジャイロだけのずれ：{rms(gyro_only):.2f} 度（12秒後には {gyro_only[-1] - true[-1]:.1f} 度ずれている）")
print(f"相補フィルタのずれ：{rms(fused):.2f} 度")
```

```text
加速度だけ　のずれ：2.54 度
ジャイロだけのずれ：5.46 度（12秒後には 9.5 度ずれている）
相補フィルタのずれ：1.39 度
```

`ALPHA` を 0.9 や 0.995 に変えて、ずれがどう変わるか試してみましょう。

### α の決め方の目安

相補フィルタで、加速度の値がどれくらいの時間をかけて効いてくるかは、次の時間 $\tau$ でおおよそ表せます。

$$
\tau \approx \frac{\alpha \, \Delta t}{1 - \alpha}
$$

1コマが $\frac{1}{60}$ 秒で $\alpha = 0.98$ なら、$\tau \approx 0.82$ 秒です。0.8 秒くらいより短い変化はジャイロで、それより長い変化は加速度で見る、という意味になります。$\alpha$ を 1 に近づけるほど、加速にだまされにくくなりますが、ジャイロのずれを直すのが遅くなります。

## ⑤ つまずきポイント

### 止まっているのに、加速度が 0 にならない

重力を測っているからです。シミュレータでは、止まっていると y がおよそ −9.81 になります。車が加速していないことを確かめるには、3つの値の大きさ（$\sqrt{x^2 + y^2 + z^2}$）が約 9.81 かどうかを見ます。

### 向きが、少しずつ勝手に変わっていく

ジャイロのバイアスを足し合わせているからです（ドリフト）。実機では、プログラムを始めたときに、車を止めたまま数秒間ジャイロの値を平均し、その平均（バイアス）を毎回引いてから足し合わせると、ずれを小さくできます。

### 実機で、左に曲がったのに向きが増えない

シミュレータと実機では、軸の向きが違います。シミュレータでヨーは `[1]`（y）、実機では `[2]`（z）です。符号も、実際に回して確かめましょう。

### 角度の単位を取り違える

ジャイロの値はラジアン毎秒です。度で考えたいときは、`math.degrees()` で直します。逆に、`math.sin()` や `math.cos()` に入れる角度はラジアンです。

## ⑥ 確認問題

**問1**　IMU の加速度センサとジャイロで、「短い時間なら得意」なのはどちらですか。「長い時間でもずれない」のはどちらですか。

:::details 答え
短い時間なら得意なのは、ジャイロです。長い時間でもずれないのは、加速度センサ（重力の向き）です。相補フィルタは、この2つを合わせて使います。
:::

**問2**　ジャイロに 0.5°/秒 のバイアスがあるとします。そのまま1分間足し合わせると、向きは何度ずれますか。

:::details 答え
$0.5 \times 60 = 30$ 度ずれます。
:::

**問3**　相補フィルタの $\alpha$ を 1 にすると、どうなりますか。0 にすると、どうなりますか。

:::details 答え
$\alpha = 1$ だと、加速度をまったく使わず、ジャイロを足し合わせるだけになります。なめらかですが、ずれはたまり続けます。
$\alpha = 0$ だと、ジャイロをまったく使わず、加速度から求めた角度そのものになります。ずれはたまりませんが、ばらつきが大きく、加速にもだまされます。
:::

**問4**　シミュレータで、左に 0.5 rad/s で4秒間回りました。`heading.py` の向きは、およそ何度になりますか。

:::details 答え
回った角度は $0.5 \times 4 = 2$ rad です。度に直すと $2 \times \frac{180}{\pi} \approx 114.6°$ です。
:::

## ⑦ 原典

- **BYOA（Build Your Own AHRS）**（`comp_filter.py`）：[racecar-neo-summer-labs](https://github.com/MITRacecarNeo/racecar-neo-summer-labs)（GPL-3.0。ファイルの先頭には MIT License と書かれています）。課題の流れと、トピック `/mag`・`/attitude` はこのファイルより
- `get_linear_acceleration()`・`get_angular_velocity()`・`get_magnetic_field()` と、シミュレータ・実機の軸の向き：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `physics.py`（GPL-3.0）
- 実機の IMU のトピック（`/imu/fused`・`/imu/lsm9ds1`）：[racecar_neo_ros2_driver](https://github.com/MITRacecarNeo/racecar_neo_ros2_driver) の `imu_fusion_node.py`・`config/pit.yaml`（GPL-3.0）
- シミュレータの加速度に重力が入ること：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `PhysicsModule.cs`
- 相補フィルタの式：[AHRS のドキュメント「Complementary Filter」](https://ahrs.readthedocs.io/en/latest/filters/complementary.html)（`comp_filter.py` の中で紹介されている資料）

図1と `comp_demo.py` は、作ったデータによる説明用のものです。`imu_check.py` と `heading.py` は、作った IMU の値を1コマずつ渡すプログラムで確かめました。
