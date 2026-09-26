---
title: "7-4 コーンスラローム"
free: true
---

この回の課題は、オンライン事前コースの **Lab H**「コーンスラローム（Cone Slalom）」です。青いコーンは左側を、赤いコーンは右側を通りぬけながら、コーンの列を走りきります。7-2 のステートマシンと、7-3 のカメラと LIDAR でコーンを見る方法を組み合わせます。

## ① この回でできるようになること

1. Lab H の課題と、自動採点のコースを説明できる
2. コーンの色で「どちら側を通るか」を決め、コーンの横をねらって走れる
3. コーンが見えなくなったあと、次のコーンを見つけるための動きを作れる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Slalom | スラローム | 並べた物の間を、右・左と交互にぬけていく走り方 |
| Pass side | 通る側 | コーンの左と右の、どちらを通るか |
| Offset | ずらし | コーンの中心から、横にどれだけ離れた所をねらうか |
| Gate | 門 | 2つのコーンの間を通りぬける所 |

## ③ 本文

### Lab H の課題

シミュレータのレベルは、**Neo Labs** の **Lab H: Cone Slalom** です。ヘルプには「青いコーンの左側と、赤いコーンの右側を走りなさい」と書かれています。自動採点モードでは、次の6つのコースを順番に走ります。

| コース | 内容 | 点数 | 制限時間 |
|---|---|---|---|
| Blue Cone | 青いコーンの左側を通る | 1 | なし |
| Red Cone | 赤いコーンの右側を通る | 1 | なし |
| Straight Course | まっすぐなスラロームのコースを走りきる | 3 | 20 秒 |
| Curved Course | 曲がったスラロームのコースを走りきる | 3 | 25 秒 |
| Gates | コーンの門を1つずつ通りぬける | 2 | 15 秒 |
| Full Course | スラロームのコースを走りきる | 10 | 90 秒 |

Full Course には、時間によるボーナスがあります。20 秒以内なら ＋1 点、30 秒以内なら ＋0.5 点、45 秒以内なら 0 点、60 秒以内なら −1 点、それより遅いと −2 点です。

Lab G とちがい、racecar-neo-prereq-labs には `lab_h` のフォルダ（課題のひな形）がありません。labs フォルダの `template.py` をコピーして、自分で作りましょう。

:::message
Lab H も自動採点つきの課題なので、この本では、赤いコーンの色の範囲などの答えの数値は載せません。5-1 の `hsv_probe.py` で、シミュレータのコーンの色を測って決めましょう。説明用のモデルでは、青いコーンには Lab E・Lab F のひな形の青の範囲を使い、赤のかわりに**紫**のコーンを使っています。
:::

### どこをねらって走るか

コーンの真ん中へ向かって走ると、コーンにぶつかります。そこで、**コーンの中心から横へ `PASS`（50 cm）ずれた所**をねらいます。

- カメラの画像で、コーンの向き $\theta_c$ がわかります（7-3 と同じく、列の位置 × カメラの横の視野の半分）
- LIDAR で、その向きの距離 $d$ がわかります（7-3 の `cone_distance()` と同じ考え方）
- 距離 $d$ 先で、横へ `PASS` だけずれた所は、コーンの向きから $\arctan(\text{PASS}/d)$ だけ横に見えます

青いコーンなら左へ（−）、もう1色のコーンなら右へ（＋）ずらします。

$$
\theta_{\text{aim}} = \theta_c + s \cdot \arctan\frac{\text{PASS}}{d}
$$

$s$ は、青なら $-1$、もう1色なら $+1$ です。

近づくほど $d$ が小さくなり、ずらす角度は大きくなります。遠くではほぼコーンの方へ、近くでは大きく横へハンドルを切ることになります。

### 2つの状態

スラロームは、2つの状態で作れます。

| 状態 | すること | 次の状態へ |
|---|---|---|
| APPROACH（近づく） | いちばん近いコーンの、通る側へ `PASS` ずらした所をねらう | コーンが見えなくなったら RETURN |
| RETURN（もどる） | 通った側と反対へハンドルを `RETURN_TURN` だけ切って進む | コーンが見えたら APPROACH |

コーンの横をぬけるころには、たいてい次のコーンが見えています。すると「いちばん近いコーン」が次のコーンに変わるだけで、APPROACH のまま、次のコーンの反対側へ向かいます。コーンが1本も見えなくなるのは、次のコーンが横に大きくずれているときや、最後のコーンをぬけたあとです。そのとき車は、コーンの列から横にはみ出しているので、今通った側と反対へハンドルを切って、列へもどりながら次のコーンを探します（RETURN）。

「いちばん近いコーン」は、画像の中でいちばん大きく写っているコーンにします。2つの色それぞれで、いちばん大きい輪郭を探し、大きいほうを選びます。

```python:slalom.py
"""
slalom.py
コーンスラローム（7-4）。青いコーンは左側を、もう1色のコーンは右側を通りぬける。
  APPROACH：いちばん近いコーンの、通りたい側へ PASS cm ずらした所をめざす
  RETURN  ：コーンが見えなくなったら、コーンの列のほうへ曲がりながら、次のコーンを探す
"""

import math
import sys
from enum import IntEnum

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

# 説明用のモデルの色。Lab H の赤いコーンの色の範囲は、5-1 の方法で自分で測る
BLUE = ((90, 50, 50), (120, 255, 255))      # 左側を通るコーン（Lab E・Lab F のひな形の青）
OTHER = ((140, 80, 80), (170, 255, 255))    # 右側を通るコーン（このモデルでは紫。Lab H では赤）
MIN_CONTOUR_AREA = 30
HALF_FOV = 34.7        # カメラの横の視野の半分（度）
PASS = 50.0            # コーンの中心から、どれだけ横を通るか（cm）
FULL_TURN = 30.0       # 目標の向きがこの角度（度）より横にあったら、ハンドルをいっぱいに切る
SPEED = 0.4
RETURN_TURN = 0.8      # RETURN で切るハンドルの大きさ


class State(IntEnum):
    APPROACH = 0
    RETURN = 1


state = State.RETURN
last_side = -1.0       # 最後に通ったコーンで、車がどちら側を通ったか（-1：左、+1：右）
aim = 0.0              # 目標の向き（度）


def nearest_cone():
    """見えているコーンのうち、いちばん大きく写っている（近い）ものを (色, 列 -1〜1) で返す。なければ None"""
    image = rc.camera.get_color_image()
    if image is None:
        return None
    best = None
    for color, (low, high) in (("blue", BLUE), ("other", OTHER)):
        contour = rc_utils.get_largest_contour(rc_utils.find_contours(image, low, high), MIN_CONTOUR_AREA)
        if contour is not None:
            area = rc_utils.get_contour_area(contour)
            if best is None or area > best[0]:
                col = rc_utils.get_contour_center(contour)[1]
                best = (area, color, (col - 320) / 320)
    if best is None:
        return None
    return best[1], best[2]


def cone_distance(scan, x):
    """カメラで見たコーンの向きの、±5° の中でいちばん近い物までの距離（7-3）"""
    a = round(x * HALF_FOV)
    _, d = rc_utils.get_lidar_closest_point(scan, ((a - 5) % 360, (a + 5) % 360))
    return d


def start():
    global state, last_side
    state = State.RETURN
    last_side = -1.0
    rc.drive.stop()
    print(">> スラロームをはじめます")


def update():
    global state, last_side, aim
    cone = nearest_cone()

    if state == State.APPROACH:
        if cone is None:                           # コーンの横をぬけた
            state = State.RETURN
            print("RETURN へ（コーンが見えなくなった）")
    elif state == State.RETURN:
        if cone is not None:
            state = State.APPROACH
            print(f"APPROACH へ（{'青' if cone[0] == 'blue' else 'もう1色'}のコーンが見えた）")

    if state == State.APPROACH:
        color, x = cone
        d = cone_distance(rc.lidar.get_samples(), x)
        side = -1.0 if color == "blue" else 1.0     # 青は左側（-1）、もう1色は右側（+1）を通る
        last_side = side
        aim = x * HALF_FOV + side * math.degrees(math.atan2(PASS, d))
        angle = rc_utils.clamp(aim / FULL_TURN, -1.0, 1.0)
    else:
        angle = -last_side * RETURN_TURN             # 通った側と反対へ切って、コーンの列にもどる
    rc.drive.set_speed_angle(SPEED, angle)


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
```

まっすぐな列で走らせると、状態が変わるたびに、次のように表示されました。

```text
  0.0 秒 >> スラロームをはじめます
  0.0 秒 APPROACH へ（青のコーンが見えた）
 16.7 秒 RETURN へ（コーンが見えなくなった）
 22.5 秒 APPROACH へ（青のコーンが見えた）
```

（左の数字は、スタートからの秒数です。この本で書き足しました。）

まっすぐな列では、6 本めのコーンをぬける（17.9 秒）まで、ずっと APPROACH のままでした。16.7 秒に RETURN になったのは、最後のコーンが視野から外れたときです。そのあと車は左へ曲がり続け、22.5 秒に、ぬけてきたコーンがまた見えて、APPROACH にもどりました。コースの終わりで止まる仕組みは入れていないので、必要なら、時間やコーンの数で止まる状態を足しましょう。

### 走らせてみる

説明用のモデルで、6本のコーンを 150 cm おきに、まっすぐ並べた列と、曲がって並べた列を作りました。青と紫が交互に並んでいます。

| 列 | RETURN_TURN 0.8 | RETURN_TURN 0.6 |
|---|---|---|
| まっすぐ | 4 回とも、6 本すべてを正しい側でぬけた | 4 回とも、6 本すべてを正しい側でぬけた |
| 曲がった | 4 回とも、6 本すべてを正しい側でぬけた | 2 回は 6 本すべてをぬけた。2 回は 3 本めの青いコーンにぶつかった |

（LIDAR とカメラのばらつきを変えて、4 回ずつ走らせました。）

![左は、スタートで車のカメラに写った画像。灰色の床の上に、青と紫のコーンが、遠くへ向かって小さく並んでいる。右の2つは、まっすぐな列と曲がった列を上から見た道すじ。青い丸と紫の丸が、たてに交互に並んでいる。オレンジの線（RETURN_TURN 0.8）は、どちらの列でも、青いコーンの左、紫のコーンの右を、交互にぬけている。灰色の点線（RETURN_TURN 0.6）は、まっすぐな列ではオレンジとほぼ重なるが、曲がった列では、2 本めのコーンのあたりで右へ大きくふくらみ、3 本めの青いコーンの前でぶつかっている](/images/racecar-neo-jp/7-4/fig1-slalom.png)
*図1　コーンスラローム：青は左側、紫（Lab H では赤）は右側を通る（説明用の簡単なモデル）*

`RETURN_TURN` が 0.6 だと、曲がった列でぶつかることがありました。図1の灰色の点線の回では、次のようなことが起きていました。

1. 6.9 秒、2 本めの紫のコーンの手前で、コーンが1本も見えなくなり、RETURN になった（3 本めの青いコーンは、左へ大きくずれた所にある）
2. RETURN で左へ切ったが、0.6 では曲がり方が小さく、車は右へふくらんで、3 本めの青いコーンより右に出てしまった
3. 8.8 秒、青いコーンを見つけて APPROACH にもどった。でも、青いコーンの左側へ回りこむには、もう近すぎた。コーンの前を横切ろうとして、11.1 秒にぶつかった

0.8 では、列へもどる曲がり方が大きいので、ふくらみすぎません。4 回とも、6 本すべてを正しい側でぬけました。

## ④ 数式・コード

### ずらす角度

コーンまでの距離が $d$、ずらす幅が PASS のとき、ずらした所の見える角度は、直角三角形から

$$
\alpha = \arctan\frac{\text{PASS}}{d}
$$

です。プログラムでは `math.degrees(math.atan2(PASS, d))` です。

| $d$ | PASS = 50 cm のときの $\alpha$ |
|---|---|
| 300 cm | 9.5° |
| 150 cm | 18.4° |
| 80 cm | 32.0° |
| 50 cm | 45.0° |

### 画像の列から向きへ

7-3 と同じく、画像の横の中心（列 320）からのずれを −1〜1 にして、カメラの横の視野の半分（34.7°）をかけます。

$$
\theta_c = \frac{\text{列} - 320}{320} \times 34.7°
$$

## ⑤ つまずきポイント

### 色の範囲が、別の色のコーンにも当たる

青の範囲が広すぎると、紫（Lab H では赤）のコーンの一部も青と見なされ、通る側をまちがえます。5-1 の方法で、2つの色のコーンを両方写し、それぞれの範囲が、もう一方の色に当たらないことを確かめましょう。

### RETURN で、コーンが見えないまま近づく

RETURN の間は、カメラにコーンが写っていないので、コーンをよけられません。ハンドルの切り方（`RETURN_TURN`）が小さいと、車がふくらんで、次のコーンの反対側へ出てしまい、見つけたときには回りこめなくなります（図1の灰色）。コーンの並び方が変わるコースでは、何通りかの `RETURN_TURN` を試しましょう。

### Gates のコース

Gates のコースは、「コーンの門を通りぬける」コースで、コーンの並び方がスラロームとはちがいます。この回の `slalom.py` は、1本ずつ交互に並んだコーンの列だけを、説明用のモデルで確かめたものです。門のコースでは、2つのコーンが同時に写るので、「いちばん近いコーン」だけを見るこの作り方で足りるかどうかを、シミュレータで確かめてください。

## ⑥ 確認問題

**問1**　青いコーンが、画像の列 400 に写っていて、LIDAR でその向きの距離は 150 cm でした。`PASS = 50` のとき、目標の向きは何度ですか。

:::details 答え
コーンの向きは $(400 - 320) \div 320 \times 34.7 \approx 8.7°$ です。ずらす角度は $\arctan(50/150) \approx 18.4°$ で、青なので左（−）へずらします。$8.7 - 18.4 = -9.7°$（左）です。
:::

**問2**　RETURN で、通った側と反対へハンドルを切るのはなぜですか。

:::details 答え
コーンの横をぬけたとき、車はコーンの列から横にはみ出しています。次のコーンは列の上にあるので、今通った側と反対へ曲がると、列へもどりながら次のコーンを見つけられるからです。
:::

## ⑦ 原典

- Lab H のレベル名、ヘルプ（青いコーンの左側、赤いコーンの右側）、自動採点のコース・点数・制限時間・時間のボーナス：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `LevelCollection.cs`
- カメラの視野（横 69.4°）：同じく `CameraModule.cs`
- labs フォルダの中身（`lab_h` がなく、`template.py` がある）：[racecar-neo-prereq-labs](https://github.com/MITRacecarNeo/racecar-neo-prereq-labs)
- `find_contours()`・`get_largest_contour()`・`get_contour_center()`・`get_contour_area()`・`get_lidar_closest_point()`・`clamp()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）

`slalom.py`・図1と表の数字は、この本で作った説明用の簡単なモデル（上から見た2次元の車、コーンを写すカメラ、LIDAR の計算）によるものです。
