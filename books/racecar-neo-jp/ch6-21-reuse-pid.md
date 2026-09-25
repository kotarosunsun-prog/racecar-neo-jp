---
title: "6-21 PID を使い回す"
free: true
---

6-12 で作った `PID` クラスは、壁沿い走行のために作りましたが、中身は「ずれを受けとって、命令を返す」だけです。壁のことは何も知りません。この回では、同じクラスを使って、6-2 の**ライントレース**と、コーンの手前で止まる**コーンへの駐車**を作り直します。

## ① この回でできるようになること

1. いろいろな課題を、「何をずれにして、何を命令にするか」で整理できる
2. 6-2 のライントレースを、PID クラスで作り直し、I の効き目を説明できる
3. カメラと LIDAR を組み合わせて、コーンの手前で止まるプログラムを作れる
4. 1つのプログラムで、PID を2つ同時に使える

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Reuse | 使い回し | 一度作った部品を、ほかの目的にも使うこと |
| Instance | インスタンス | クラスから作った1つ1つのもの。それぞれが自分の値（積分など）を持つ |
| Normalize | 正規化 | 値を −1〜1 のような決まった範囲にそろえること |
| Deadband | 不感帯 | 命令が小さすぎて、車が動かない範囲 |

## ③ 本文

### 「ずれ」と「命令」を決めれば、PID は使える

これまでに作った制御を、「何をずれにして、何を命令にしたか」で並べてみます。

| 課題 | ずれ | 命令 | 回 |
|---|---|---|---|
| 壁沿い走行 | 右の壁までの距離 − 50 cm | angle | 6-7〜6-14 |
| 速さを決める | 正面の壁までの距離 − 60 cm | speed | 6-19 |
| ライントレース | 画面の真ん中からの線の位置（−1〜1） | angle | 6-2、この回 |
| コーンのほうを向く | 画面の真ん中からのコーンの位置（−1〜1） | angle | この回 |
| コーンの手前で止まる | コーンまでの距離 − 30 cm | speed | この回 |

どれも、「ずれを 0 にしたい」「ずれに合わせて命令を決める」という形です。この形になっていれば、6-12 の `PID` クラスが、そのまま使えます。ちがうのは、ずれの**単位**と、それに合わせた**ゲインの大きさ**だけです。

- 壁までの距離のずれは cm なので、KP は 0.02〜0.04 くらいでした（1 cm ずれると angle が 0.02〜0.04）
- 画面の中の位置は −1〜1 に正規化してあるので、KP は 1〜2 くらいになります（画面のはしまでずれると angle が 1〜2）

### ライントレースを PID クラスで作り直す

6-2 の `line_follow.py` では、`angle = KP * error` と書きました。これを `PID` クラスにします。速さは、人がトリガーで決めるかわりに、一定（speed 0.5）にしました。

```python:line_follow_pid.py
"""
line_follow_pid.py
6-2 の line_follow.py のハンドルを、6-12 の PID クラスで決めるようにしたもの（6-21）。
速さは一定（SPEED）。pid.py を同じフォルダに置いて使う。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from pid import PID

rc = racecar_core.create_racecar()

BLUE = ((90, 50, 50), (120, 255, 255))   # 線の色（Lab E・Lab F のひな形の青）
MIN_CONTOUR_AREA = 30                      # これより小さいかたまりは無視する
CROP_FLOOR = ((360, 0), (rc.camera.get_height(), rc.camera.get_width()))   # 画像の下の部分（車のすぐ前の床）
SPEED = 0.5                                # 走る速さ（一定）

# ハンドルの PID：ずれは、画面の真ん中からの線の位置（左はし -1 〜 右はし +1）
steer_pid = PID(kp=2.0, ki=1.0, kd=0.1)

angle = 0.0   # 今のハンドルの角度（線が見えないときは、前の角度を使い続ける）
error = 0.0


def get_line_error():
    """線の中心が、画面の真ん中から左右にどれだけずれているか（左はし -1 〜 右はし +1）。見えなければ None"""
    image = rc.camera.get_color_image()
    if image is None:
        return None
    image = rc_utils.crop(image, CROP_FLOOR[0], CROP_FLOOR[1])
    contours = rc_utils.find_contours(image, BLUE[0], BLUE[1])
    contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)
    if contour is None:
        return None
    center = rc_utils.get_contour_center(contour)      # (行, 列)
    half = rc.camera.get_width() / 2
    return (center[1] - half) / half


def start():
    global angle
    angle = 0.0
    steer_pid.reset()
    rc.drive.stop()
    print(">> 線を見て、PID でハンドルを切ります")


def update():
    global angle, error
    e = get_line_error()
    if e is not None:
        error = e
        angle = steer_pid.update(error, rc.get_delta_time())
    rc.drive.set_speed_angle(SPEED, angle)


def update_slow():
    print(f"ずれ {error:+.2f}　angle {angle:+.2f}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

- `steer_pid.update(error, rc.get_delta_time())` では、3つめの引数（`rate`）を省いています。D の「ずれの変わる速さ」は、`PID` クラスが、過去 10 コマのずれから計算します（6-12）
- 線が見えないときは、6-2 と同じように、前の角度を使い続けます。このとき、`update()` を呼ばないので、積分もたまりません

右・左・右と曲がる S 字の線で、6-2 と同じ P だけ（KP 1.0）と、PID をくらべました（説明用の簡単なモデル、speed 0.5）。

| ゲイン | ずれの大きさの平均 | 線からはなれた距離の平均 | いちばんはなれた距離 |
|---|---|---|---|
| P だけ（KP 1.0、6-2 と同じ） | 0.421 | 6.5 cm | 15.1 cm |
| P（KP 2.0） | 0.212 | 2.6 cm | 5.6 cm |
| PI（KP 1.0、KI 1.0） | 0.245 | 3.9 cm | 12.0 cm |
| PID（KP 2.0、KI 1.0、KD 0.1） | 0.140 | 1.7 cm | 7.0 cm |

![左は、S 字の青い線と、車の道すじを上から見た図。線は、まっすぐ 150 cm 進んでから、右へ 90°、左へ 180°、まっすぐ、右へ 180° と曲がる。P だけ（灰色）は、カーブの外側へずれて走る。PID（オレンジ）は、線にほぼ重なる。右は、カメラで見たずれの時間変化。P だけは、右へ曲がる所で +0.4〜+0.8、左へ曲がる所で −0.3〜−0.9 と、カーブの間ずっとずれが残る。PID は、カーブに入るときに ±0.3〜0.5 までずれるが、そのあと 0 に近づく](/images/racecar-neo-jp/6-21/fig1-line.png)
*図1　PID クラスでライントレース（説明用の簡単なモデル）*

図1の右を見ると、P だけでは、**カーブを曲がっている間、ずっとずれが残っています**。曲がり続けるには、ハンドルを切り続ける必要があります。P だけだと、ハンドルを切るには、ずれが必要です。だから、ずれが 0 にもどりません。これは、6-11 で、丸い部屋で壁から 50 cm を保てなかったのと、まったく同じ理由です。

I を足すと、カーブの間にずれがたまって、そのぶんハンドルを切り足すので、ずれが 0 に近づきます（図1のオレンジ）。ただし、I は「過去にためたもの」なので、S 字で曲がる向きが変わる所では、前のカーブの分が残っていて、少し遅れます。PI（KP 1.0、KI 1.0）のいちばんはなれた距離が 12.0 cm と大きいのは、そのためと考えられます。KP も大きくした PID では、7.0 cm になりました。

説明用のモデルで `line_follow_pid.py` を走らせると、次のように表示されました（1秒ごと）。

```text
>> 線を見て、PID でハンドルを切ります
ずれ +0.00　angle +0.00
ずれ +0.00　angle +0.00
ずれ +0.01　angle +0.02
ずれ +0.28　angle +0.75
ずれ +0.08　angle +0.50
ずれ +0.07　angle +0.57
ずれ -0.52　angle -0.84
ずれ -0.19　angle -0.50
ずれ -0.12　angle -0.52
ずれ -0.09　angle -0.58
ずれ -0.04　angle -0.55
ずれ -0.04　angle -0.58
ずれ +0.17　angle -0.10
ずれ +0.19　angle +0.11
ずれ +0.23　angle +0.39
ずれ +0.25　angle +0.66
```

### コーンの手前で止まる：PID を2つ使う

次は、コーンを見つけて近づき、コーンの **30 cm 手前で止まる**プログラムです。Lab G（7-3）の中心になる部分です。

- **ハンドル**：カメラの画像で、コーンの色のかたまりの中心を探し、画面の真ん中からの位置（−1〜1）をずれにします。ライントレースと同じ形です
- **速さ**：LIDAR で、正面 ±20° のいちばん近い物までの距離を測り、「距離 − 30 cm」をずれにします。6-1 の「壁の手前で止まる」と同じ形です

`PID` クラスから、ハンドル用と速さ用の2つのインスタンスを作ります。2つは、それぞれ自分の積分と、過去のずれの記録を持っているので、混ざりません。

```python:cone_park_pid.py
"""
cone_park_pid.py
コーンの色のかたまりを見てコーンのほうへハンドルを切り、コーンの 30 cm 手前で止まる（6-21）。
ハンドルと速さに、6-12 の PID クラスを1つずつ使う。pid.py を同じフォルダに置いて使う。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from pid import PID

rc = racecar_core.create_racecar()

CONE = ((90, 50, 50), (120, 255, 255))   # コーンの色（説明用のモデルでは青。Lab G のオレンジは自分で測る）
MIN_CONTOUR_AREA = 30                    # これより小さいかたまりは無視する
TARGET = 30.0                            # コーンの手前で止まりたい距離（cm）

# ハンドルの PID：ずれは、画面の真ん中からのコーンの位置（左はし -1 〜 右はし +1）
steer_pid = PID(kp=1.0, ki=0.0, kd=0.0)
# 速さの PID：ずれは「コーンまでの距離 - TARGET」。I は、目標まで 10 cm 以内に来てからためる（6-12）。
# 近すぎたら後ろへ下がれるように、下限はマイナス
speed_pid = PID(kp=0.01, ki=0.01, kd=0.0, i_zone=10, out_min=-0.3, out_max=0.5)

distance = 0.0


def find_cone():
    """コーンの中心の列を、-1〜1 で返す。見えなければ None"""
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


def start():
    rc.drive.stop()
    steer_pid.reset()
    speed_pid.reset()
    print(">> コーンに近づいて、30 cm 手前で止まります")


def update():
    global distance
    dt = rc.get_delta_time()
    x = find_cone()
    scan = rc.lidar.get_samples()
    _, distance = rc_utils.get_lidar_closest_point(scan, (340, 20))   # 前 ±20° で、いちばん近い物

    if x is None:                  # コーンが見えないときは止まる（探し方は 7-3 で作る）
        steer_pid.reset()
        speed_pid.reset()
        rc.drive.stop()
        return

    angle = steer_pid.update(x, dt)
    speed = speed_pid.update(distance - TARGET, dt)
    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    print(f"コーンまで {distance:5.1f} cm")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

- 速さの PID の `out_min=-0.3` は、コーンに近づきすぎたときに、後ろへ下がれるようにするためです
- コーンが見えないときは止まって、2つの PID を `reset()` します。コーンを探して回る動きは、7-3 でステートマシンを使って作ります

:::message
Lab G のシミュレータのコーンはオレンジ色です。オレンジの色の範囲は、Lab G の課題の答えなので、この本には載せません。5-1 の `hsv_probe.py` で測って決めましょう。説明用のモデルでは、6-2 と同じ青のコーンを使っています。また、Lab G のひな形には、「実物の RACECAR Neo に合わせるため、深度カメラは使わない」とあります。この回のように、距離は LIDAR で測ります。
:::

### 止まる所で、また I が必要になる

説明用のモデルでは、6-11 と同じように、speed の命令が 0.15 より小さいと、摩擦で車が動かないようにしています。コーンの 200 cm 以上手前から走らせて、速さの PID を3通りにしてくらべました（図2の右）。

![左は、説明用のモデルのカメラ画像。灰色の壁と床の境目の近くに、青い台形のコーンが、画面の右寄り（列 505）に写っている。画面の真ん中（列 320）からの矢印に、ずれ = (505 − 320) ÷ 320 = +0.58 と書かれている。右は、コーンまでのすき間の時間変化。3本とも、はじめはまっすぐ近づく。P だけ（灰色）は、約 34 cm で止まったまま動かない。PI（青）は、18 cm くらいまで行き過ぎてから、30 cm まで下がるが、12 秒ごろにまた 34 cm くらいまで下がる。PI ＋ i_zone 10（オレンジ）は、いったん 34 cm で止まり、7 秒ごろから少しずつ前に出て、30.4 cm で止まる](/images/racecar-neo-jp/6-21/fig2-cone.png)
*図2　カメラで見たコーン（左）と、コーンの手前で止まるようす（右）*

- **P だけ**：34.3 cm で止まって、30 cm まで行きません。ずれが 15 cm より小さくなると、命令 $0.01 \times$ ずれ が 0.15 より小さくなり、車を動かす力が足りなくなるからです（6-11 の摩擦と同じ）
- **PI**：I がたまって、30 cm まで届くようになりましたが、近づく間にもたまった I のせいで、17.7 cm まで行き過ぎました。さらに、止まっている間も、LIDAR のばらつきで I が少しずつ変わり続けて、12 秒ごろにまた動き出し、33.9 cm で止まりました
- **PI ＋ `i_zone=10`**：目標まで 10 cm 以内に入ってからだけ、I をためます（6-12）。遠くから近づく間は P だけで走り、34 cm くらいで止まったあと、I が少しずつたまって、30.4 cm まで寄せました

壁沿い走行で学んだ I の効き目と、ワインドアップの対策が、そのまま使えました。**同じ部品を使うと、同じ問題が起き、同じ対策が効きます。**

説明用のモデルで `cone_park_pid.py` を走らせると、次のように表示されました（1秒ごと）。表示の距離は LIDAR で測った値なので、6-6 で見たように、本当のすき間（30.4 cm）より少し短めに出ています。

```text
>> コーンに近づいて、30 cm 手前で止まります
コーンまで 284.8 cm
コーンまで 230.3 cm
コーンまで 159.1 cm
コーンまで  88.7 cm
コーンまで  36.1 cm
コーンまで  33.8 cm
コーンまで  33.8 cm
コーンまで  30.9 cm
コーンまで  29.7 cm
コーンまで  29.9 cm
コーンまで  29.0 cm
コーンまで  28.9 cm
```

## ④ 数式・コード

### ずれの単位と、ゲインの大きさ

同じ「ハンドルを切る」でも、ずれの単位がちがうと、ゲインの大きさがまったく変わります。

$$
\text{angle} = K_P \times \text{ずれ}
$$

の右と左で単位をそろえると、$K_P$ の単位は「angle ÷ ずれの単位」です。壁までの距離（cm）なら「1 cm あたり」、正規化した画面の位置なら「画面の半分あたり」です（6-1 の「KP の単位」）。ほかの課題のゲインを、そのまま写しても動きません。ずれの大きさを考えて、決め直しましょう。

### インスタンスごとに、値を持つ

`PID` クラスの `self.integral` や `self.history` は、インスタンスごとに別々です。

```python
steer_pid = PID(kp=1.0, ki=0.0, kd=0.0)
speed_pid = PID(kp=0.01, ki=0.01, kd=0.0, i_zone=10, out_min=-0.3, out_max=0.5)
```

`steer_pid.update()` を呼んでも、`speed_pid.integral` は変わりません。もしクラスを使わずに、グローバル変数 `integral` を1つだけ使っていたら、ハンドルのずれと、距離のずれが、同じ変数にまざってしまいます。これが、6-12 で PID をクラスにまとめた理由の1つです。

## ⑤ つまずきポイント

### ずれの符号が逆

線やコーンが画面の右にあるとき、ずれは＋で、angle も＋（右）になるはずです。符号が逆だと、線やコーンから遠ざかります。コーンを画面の右に置いて、表示される angle が＋になるか確かめましょう。

### 見失ったあとで、急にハンドルを切る

見失っている間に `update()` を呼び続けると、古いずれで積分がたまることがあります。見失ったら `update()` を呼ばないか、`reset()` しましょう。見つけ直したときに、D の「ずれの変わる速さ」が、見失う前のずれとの差で大きくなることもあります。`reset()` すると、過去のずれの記録も消えます。

### 速さの PID が、止まったあとで動き出す

図2の PI のように、I は、止まっている間も、ばらつきで少しずつ変わります。`i_zone` のほかに、「ずれが 1 cm 以内なら、I をためない」のような条件を足すのも1つの方法です。

## ⑥ 確認問題

**問1**　画面の幅が 640 で、コーンの中心が列 160 にありました。ずれ（−1〜1）はいくつですか。KP が 1.0 なら、angle はいくつですか。

:::details 答え
$(160 - 320) \div 320 = -0.5$ です。angle は $1.0 \times (-0.5) = -0.5$（左）です。
:::

**問2**　速さの PID の KP が 0.01 で、車は speed の命令が 0.15 より小さいと動きません。I を使わないと、コーンまでの距離が何 cm より近くなったとき、車を前に進める力が足りなくなりますか（目標は 30 cm）。

:::details 答え
$0.01 \times (\text{距離} - 30) < 0.15$ となるのは、距離が 45 cm より小さいときです。45 cm より近づくと、前に進める命令が足りなくなります。実際には、それまでの勢いで少し進むので、図2では 34.3 cm で止まりました。
:::

**問3**　1つのプログラムで、ハンドル用と速さ用の2つの PID を使うとき、なぜ `PID` クラスのインスタンスを2つ作るのでしょうか。

:::details 答え
PID は、積分や過去のずれの記録を持っています。インスタンスを分けると、それぞれが自分の値を持つので、ハンドルのずれと距離のずれが混ざりません。
:::

## ⑦ 原典

- Lab G の課題（コーンの 30 cm 手前に駐車する、深度カメラは使わない）：[racecar-neo-outreach-labs](https://github.com/MITRacecarNeo/racecar-neo-outreach-labs) の `labs/lab_g/lab_g.py`
- Lab F と、青の色の範囲 `((90, 50, 50), (120, 255, 255))`：同じく `labs/lab_f/lab_f.py`（6-2）
- `find_contours()`・`get_largest_contour()`・`get_contour_center()`・`crop()`・`get_lidar_closest_point()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）

図1・図2、表と表示の数字は、この本で作った説明用の簡単なモデル（上から見た2次元の車、床の線とコーンを写すカメラ、LIDAR の計算）によるものです。
