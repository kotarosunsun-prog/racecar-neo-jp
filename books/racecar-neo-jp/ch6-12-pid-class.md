---
title: "6-12 PID をクラスにまとめる"
free: true
---

6-7 から 6-11 で、P・I・D の3つを1つずつ足してきました。プログラムには、`integral` や `errors` のような「覚えておく変数」がふえ、`global` もふえてきました。この先、ハンドルだけでなく速さ（6-19）や、ライントレース（6-21）にも PID を使います。この回では、PID を1つの**クラス**にまとめて、何度でも使える部品にします。あわせて、PID を実際に使うときに大事な3つのこと、**時間・命令の上限・積分の暴走**をあつかいます。

## ① この回でできるようになること

1. クラスを使って、PID を1つの部品にまとめられる
2. 1コマの時間が変わっても正しく動くように、時間を使って計算できる
3. 積分の暴走（ワインドアップ）が起きる理由と、2つの防ぎ方を説明できる
4. 作った PID クラスを、別のファイルから読みこんで使える

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Class | クラス | 値（変数）と、それを使う関数を、ひとまとめにした設計図 |
| Instance / Object | インスタンス（オブジェクト） | クラスから作った、1つ1つの実物 |
| Method | メソッド | クラスの中に書いた関数。`pid.update()` の `update` |
| Integral windup | 積分の暴走（ワインドアップ） | 積分がたまりすぎて、大きく行き過ぎること |

## ③ 本文

### クラスとは

PID には、ゲイン（KP・KI・KD）のような**設定**と、ためた積分やずれの記録のような**覚えておく値**があります。これらを、ばらばらの変数で持つと、PID を2つ使いたいとき（ハンドル用と速さ用など）に、`integral_steer`、`integral_speed` … と、変数がどんどんふえてしまいます。

**クラス**を使うと、設定と覚えておく値と、それを使う計算（関数）を、1つにまとめられます。

```python
steer_pid = PID(kp=0.02, ki=0.005, kd=0.04)     # ハンドル用の PID を1つ作る
speed_pid = PID(kp=0.02, ki=0.01, kd=0.0)       # 速さ用の PID を、もう1つ作る

angle = steer_pid.update(error, dt)              # それぞれが、自分の積分を覚えている
```

`PID(...)` と書くたびに、新しい PID が1つできます（**インスタンス**）。`steer_pid` と `speed_pid` は、それぞれ自分の積分や記録を持っていて、まざりません。クラスの中では、自分の持っている値を `self.integral` のように、`self.` をつけて表します。

### 大事なこと 1：時間

6-9 と 6-11 では、D と I の計算に `rc.get_delta_time()`（1コマの時間）を使いました。3-1 で見たように、1コマの時間は、いつも同じとは限りません。画像の処理が重いと、1秒に 60 コマより少なくなることがあります。

1コマの時間を「いつも 1/60 秒」と決めつけると、コマが少なくなったとき、積分は本当より小さく、速さは本当より大きく計算されてしまいます。このクラスでは、毎回 `dt`（1コマの時間）を受けとって、積分にも速さにも使います。速さは、6-9 の「何コマか前と比べる」方法ですが、記録に**時刻**もいっしょに残しておき、「その間に何秒たったか」でわります。

### 大事なこと 2：命令の上限

angle も speed も、−1〜1 の範囲に入れなければなりません。PID の3つを足した命令は、ずれが大きいと、この範囲をこえます。クラスの最後で、命令を上限・下限の中におさめます（`out_min`・`out_max`）。

### 大事なこと 3：積分の暴走

6-11 の最後で、「遠くから走り出すと、壁にぶつかった」ことを見ました。説明用の簡単なモデルで、壁から 150 cm の所から、6-11 の方法（KI 0.005）で走らせると、車は目標の 50 cm を大きく通りすぎ、壁から **14.6 cm** まで近づきました。

![上のグラフは、壁から 150 cm の所から走り出したときの、時間と壁までの距離。ためすぎを防がないとき（灰色、6-11 のまま）は、目標の 50 cm を通りすぎて、4.5 秒ごろに 15 cm くらいまで壁に近づき、そこからゆっくりもどる。命令がいっぱいのときはためないようにしたとき（青）は、28 cm くらいまで近づく。さらに、ずれが 20 cm より大きいときもためないようにしたとき（オレンジ）は、47 cm くらいまでしか行き過ぎず、すぐに 50 cm に落ち着く。下のグラフは、I の部分。灰色は 2.7 秒ごろに 0.83 まで大きくなる。青は 0.5 まで。オレンジは 0.07 くらいまでしか大きくならない](/images/racecar-neo-jp/6-12/fig1-windup.png)
*図1　積分の暴走と、その防ぎ方（説明用の簡単なモデル）*

図1の下の灰色の線を見てください。壁に近づいていく間、ずれは＋（遠すぎる）のままなので、積分はどんどんたまり、I の部分は 0.83 にもなります。目標に着いたときには、ためた積分が大きすぎて、ハンドルを壁のほうへ切り続けてしまいます。ためた積分は、反対のずれでしか減らないので、壁に近づきすぎてから、ようやく減っていきます。これが**積分の暴走**（ワインドアップ）です。

防ぎ方は、いろいろあります。このクラスでは、次の2つを使います。

1. **命令がいっぱいのときは、ためない**：命令が上限（または下限）をこえていて、さらに同じ向きにためようとしているときは、ためても意味がありません。そういうときは、積分を足さないことにします（図1の青）
2. **ずれが大きいときは、ためない**：I の役目は、「目標の近くで残る、小さなずれ」を消すことです。ずれが大きい間は、P と D にまかせて、ためないことにします（`i_zone`、図1のオレンジ）

2つを合わせると、行き過ぎは 47 cm くらいまでになりました。

ただし、`i_zone` を小さくしすぎると、今度は I がはたらかなくなります。6-11 の丸い部屋では、P だけだと 15 cm ずれるので、`i_zone = 5` や `10` にすると、ずれが `i_zone` の外にあるままになり、I がはたらかず、ずれが残りました（35.2 cm、36.6 cm）。`i_zone = 20` なら、50.1 cm にもどりました。

### PID クラス

これまでのことを、1つのクラスにまとめたものです。`pid.py` という名前で保存します。

```python:pid.py
"""
pid.py
PID 制御をまとめたクラス（6-12）。
使い方：
    from pid import PID
    pid = PID(kp=0.02, ki=0.005, kd=0.03)
    angle = pid.update(error, rc.get_delta_time())
"""


class PID:
    def __init__(self, kp, ki, kd, out_min=-1.0, out_max=1.0,
                 i_limit=None, i_zone=None, rate_frames=10):
        self.kp = kp                      # P のゲイン
        self.ki = ki                      # I のゲイン
        self.kd = kd                      # D のゲイン
        self.out_min = out_min            # 命令の下限
        self.out_max = out_max            # 命令の上限
        self.i_limit = i_limit            # 積分の大きさの上限（None なら上限なし）
        self.i_zone = i_zone              # ずれがこれより小さいときだけ、ためる（None ならいつでも）
        self.rate_frames = rate_frames    # 何コマ前のずれと比べて、速さを求めるか（6-9）
        self.reset()

    def reset(self):
        """ためた積分と、ずれの記録を消す（走り出すときや、切りかえるときに呼ぶ）"""
        self.integral = 0.0
        self.history = []                 # 最近の (時刻, ずれ)
        self.time = 0.0

    def update(self, error, dt, rate=None):
        """ずれ error と、1コマの時間 dt（秒）から、命令を返す。
        rate を渡すと、D の部分には、ずれの変わる速さのかわりに、それを使う"""
        self.time += dt

        # D：ずれの変わる速さ（記録の、いちばん古いものと新しいものを比べる）
        self.history.append((self.time, error))
        if len(self.history) > self.rate_frames + 1:
            self.history.pop(0)
        if rate is None:
            rate = 0.0
            if len(self.history) >= 2:
                t0, e0 = self.history[0]
                t1, e1 = self.history[-1]
                rate = (e1 - e0) / (t1 - t0)

        # I：ずれをためる。ただし、次のときはためない（積分の暴走をふせぐ）
        #  ・ずれが i_zone より大きいとき
        #  ・命令がもう上限（下限）をこえていて、さらに同じ向きにためようとするとき
        in_zone = self.i_zone is None or abs(error) < self.i_zone
        trial = self.kp * error + self.ki * (self.integral + error * dt) + self.kd * rate
        too_high = trial > self.out_max and self.ki * error > 0
        too_low = trial < self.out_min and self.ki * error < 0
        if in_zone and not (too_high or too_low):
            self.integral += error * dt
        if self.i_limit is not None:
            self.integral = max(-self.i_limit, min(self.i_limit, self.integral))

        # 3つを足して、上限・下限の中におさめる
        out = self.kp * error + self.ki * self.integral + self.kd * rate
        return max(self.out_min, min(self.out_max, out))
```

- `__init__()`：`PID(...)` と書いたときに、1回だけ動く関数です。受けとった設定を、`self.kp` などに覚えておきます
- `reset()`：ためた積分と記録を消します。`start()` の中で呼ぶと、走らせ直すたびに、まっさらな状態から始められます
- `update()`：毎コマ呼びます。ずれと 1コマの時間を渡すと、命令を返します
- `rate`：6-10 の「壁の向き」のように、ずれの変わる速さのかわりになる値があるときは、`rate=` で渡します。渡さなければ、6-9 の方法で、記録から速さを求めます

### やってみよう：PID クラスで壁にそって走る

`pid.py` と同じフォルダに、次のプログラムを作ります。D の部分には、6-10 の「壁の向き」を渡すので、`kd` は 6-10 の `KA` と同じ意味になります。

```python:wall_follow_pid.py
"""
wall_follow_pid.py
右の壁から TARGET cm の距離を保って走る。PID クラス（pid.py）を使う。
D の部分には、6-10 の「壁の向き」を入れる。
"""

import sys
import math

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from pid import PID              # 同じフォルダの pid.py から読みこむ

rc = racecar_core.create_racecar()

TARGET = 50.0     # 右の壁から保ちたい距離（cm）
SPEED = 0.5       # 走る速さ（一定）
THETA = 30        # 2本の光線の間の角度（度）

# ハンドルの PID：D には「壁の向き（度）」を入れるので、kd は 6-10 の KA と同じ意味
steer_pid = PID(kp=0.02, ki=0.005, kd=0.04, i_zone=20)

distance = None   # 右の壁までの距離（update_slow で表示する）
angle = 0.0


def right_wall(scan):
    """右の壁の向き（度）と、壁までの距離（cm）を返す。測れなければ (None, None)（6-10）"""
    a = rc_utils.get_lidar_average_distance(scan, 90 - THETA)
    b = rc_utils.get_lidar_average_distance(scan, 90)
    if a == 0.0 or b == 0.0:
        return None, None
    t = math.radians(THETA)
    alpha = math.atan2(a * math.cos(t) - b, a * math.sin(t))
    return math.degrees(alpha), b * math.cos(alpha)


def start():
    rc.drive.stop()
    steer_pid.reset()
    print(f">> 右の壁から {TARGET:.0f} cm を保って走ります（PID クラス）")


def update():
    global distance, angle

    scan = rc.lidar.get_samples()
    wall_angle, distance = right_wall(scan)

    if distance is None:
        angle = 0.0
    else:
        angle = steer_pid.update(distance - TARGET, rc.get_delta_time(), rate=wall_angle)

    rc.drive.set_speed_angle(SPEED, angle)


def update_slow():
    if distance is None:
        print("壁が見えない")
    else:
        print(f"右の壁まで {distance:5.1f} cm　I の部分 {steer_pid.ki * steer_pid.integral:+.3f}　angle {angle:+.2f}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

`global` が `distance` と `angle` だけになり、`update()` の中の PID の計算は1行になりました。説明用の簡単なモデルで、壁から 150 cm の所から走らせると、次のように表示されました（はじめの 10 秒）。

```text
>> 右の壁から 50 cm を保って走ります（PID クラス）
右の壁まで 150.7 cm　I の部分 +0.000　angle +1.00
右の壁まで 137.2 cm　I の部分 +0.000　angle +0.46
右の壁まで  93.8 cm　I の部分 +0.000　angle -0.43
右の壁まで  65.3 cm　I の部分 +0.027　angle -0.14
右の壁まで  52.8 cm　I の部分 +0.063　angle -0.09
右の壁まで  47.9 cm　I の部分 +0.062　angle +0.03
右の壁まで  46.7 cm　I の部分 +0.049　angle +0.02
右の壁まで  47.4 cm　I の部分 +0.033　angle -0.07
右の壁まで  47.7 cm　I の部分 +0.018　angle -0.01
右の壁まで  48.8 cm　I の部分 +0.012　angle +0.07
右の壁まで  48.5 cm　I の部分 +0.005　angle -0.03
```

ずれが 20 cm より大きい間（はじめの3秒近く）は、I の部分が 0 のままです。目標の近くに来てから、少しずつためはじめています。

同じクラスは、6-11 の「壁の手前で止まる」にも、そのまま使えます。`speed = speed_pid.update(front - TARGET, rc.get_delta_time())` と書くだけです。モデルで、摩擦を入れて 300 cm の所から走らせると、6-11 のプログラムでは壁にぶつかりましたが、`PID(0.02, 0.01, 0.0)` のクラスでは、いちばん近づいても 35.4 cm で、51.0 cm で止まりました。走り出しは命令がいっぱい（speed 1）なので、「命令がいっぱいのときは、ためない」がはたらいたのです。

## ④ 数式・コード

### PID の式

このクラスが計算しているのは、次の式です。$e$ はずれ、$\dot{e}$ はずれの変わる速さです。

$$
u = K_P \, e + K_I \int e \, dt + K_D \, \dot{e}
$$

そのうえで、$u$ を上限・下限の中におさめます。3つの部分の役目をまとめると、次のようになります。

| 部分 | 見ているもの | 役目 |
|---|---|---|
| P | 今のずれ | ずれを減らす向きに、ずれに比例して動かす |
| I | これまでのずれの積み重ね | 残ったずれを、時間をかけて消す |
| D | ずれの変わる速さ | 勢いよく近づいているときに、早めにブレーキをかける |

### 1コマの時間を決めつけると、どうなるか

1コマの時間を 1/60 秒と決めつけていて、実際には 1/30 秒だったとします。すると、積分に足す量は本当の半分になり、I は本当の半分しか効きません。速さは、ずれの差を実際の2倍の短い時間でわるので、本当の2倍になり、D が2倍効きます。`dt` を毎回受けとって使えば、このずれは起きません。

### 積分の上限（i_limit）

このクラスには、もう1つの防ぎ方として、積分の大きさに上限をつける `i_limit` も入れてあります。たとえば「I の部分は、最大でも ±0.3 まで」にしたいなら、`i_limit = 0.3 / ki` とします。上限が小さすぎると、丸い部屋のように大きな I の部分が必要なとき、ずれが消しきれません。

## ⑤ つまずきポイント

### `ModuleNotFoundError: No module named 'pid'`

`pid.py` が、動かすプログラムと同じフォルダにありません。`racecar sim wall_follow_pid.py` で動かすときは、`wall_follow_pid.py` と同じフォルダに `pid.py` を置きます。

### PID を `update()` の中で作ってしまう

`steer_pid = PID(...)` を `update()` の中に書くと、毎コマ新しい PID ができて、積分や記録が毎回 0 にもどります。PID は、プログラムのはじめ（`start()` の外）で1回だけ作り、`start()` では `reset()` だけを呼びます。

### `self.` を書き忘れる

クラスの中で、自分の値を使うときは、`self.integral` のように `self.` をつけます。`integral` とだけ書くと、「そんな変数はない」というエラーになるか、別の変数を使ってしまいます。

### D に何を渡しているのか、わからなくなる

`rate=wall_angle` を渡すと、`kd` は「壁の向き 1° あたり」のゲインになります。`rate` を渡さないと、`kd` は「ずれの変わる速さ 1 cm/秒 あたり」のゲインです。同じ `kd` の数でも、意味がまったくちがうので、コメントに書いておきましょう。

## ⑥ 確認問題

**問1**　`PID(kp=0.02, ki=0.005, kd=0.0)` で、`update(10, 0.5)` を1回だけ呼びました（はじめての呼び出し）。返ってくる値はいくつですか。

:::details 答え
積分は $10 \times 0.5 = 5$、D は記録が1つしかないので 0 です。$0.02 \times 10 + 0.005 \times 5 = 0.2 + 0.025 = 0.225$ です。
:::

**問2**　問1 の PID を `i_zone=5` にして、同じように呼ぶと、返ってくる値はいくつですか。

:::details 答え
ずれ 10 は `i_zone` の 5 より大きいので、積分はためません。$0.02 \times 10 = 0.2$ です。
:::

**問3**　積分の暴走は、どんなときに起きやすいですか。

:::details 答え
走り出しなど、ずれの大きい状態が長く続くときです。その間に積分がたまりすぎて、目標に着いたあとも、同じ向きに命令を出し続けてしまいます。
:::

## ⑦ 原典

この回は、この本で加えた解説です。

- `get_delta_time()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_core.py`（GPL-3.0）
- `get_lidar_average_distance()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）

図1と、`wall_follow_pid.py` の表示、丸い部屋・壁の手前で止まる場合の数値は、この本で作った説明用の簡単なモデル（上から見た2次元の車と壁、LIDAR の計算）によるものです。
