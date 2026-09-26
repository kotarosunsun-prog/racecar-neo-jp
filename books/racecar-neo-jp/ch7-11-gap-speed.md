---
title: "7-11 空き具合でスピードを決める"
free: true
---

ここまでの Gap Follower は、ずっと speed 0.5 で走っていました。この回では、**目標の向きが遠くまで空いているほど速く**、近くに物があるほどゆっくり走るようにします。6-19 では、正面の壁までの距離で速さを決めました。Gap Follower では、「これから進む向き」がどれだけ空いているかを使えます。

## ① この回でできるようになること

1. 目標の向きの距離から、speed を決める式を作れる
2. いちばん遅い speed と、いちばん速い speed を決めて、その間におさめられる
3. 一定の速さと、空き具合で決める速さを、時間と安全さでくらべられる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Speed schedule | 速さの決め方 | 何を見て、speed をいくつにするかの決まり |
| Min speed | いちばん遅い speed | 前がせまくても、この速さでは走る |
| Max speed | いちばん速い speed | 前がどんなに空いていても、これより速くしない |
| Lap time | 走りきるまでの時間 | スタートからゴールまでにかかった時間 |

## ③ 本文

### 目標の向きの距離で決める

7-10 までで、Gap Follower は目標の向き（空きの真ん中）を決めました。その向きの距離 $d$（`front_view()` でそろえ、はしをのばし、バブルでふさいだあとの値）は、**これから進む先が、どこまで空いているか**を表しています。

- $d$ がしきい値（150 cm）くらいなら、空きのはしぎりぎりです。ゆっくり走ります（`MIN_SPEED` = 0.4）
- $d$ が `MAX_RANGE`（300 cm）なら、先がずっと空いています。速く走ります（`MAX_SPEED` = 1.0）
- その間は、距離に比例して速くします

$$
\text{speed} = \text{clamp}\bigl(\text{MIN\_SPEED} + K_V\,(d - \text{THRESHOLD}),\ \text{MIN\_SPEED},\ \text{MAX\_SPEED}\bigr)
$$

$K_V = 0.004$ にすると、$d = 150$ で 0.4、$d = 300$ で $0.4 + 0.004 \times 150 = 1.0$ になります。

### プログラム（完成版）

7-7 から少しずつ足してきた `gap_follow.py` の、全体です。はじめの設定は、7-10 までで決めたもの（いちばん広い空きの真ん中、しきい値 150 cm、バブル 20 cm、はしをのばす幅 20 cm）と、この回の速さの決め方です。

```python:gap_follow.py
"""
gap_follow.py
LIDAR で正面 ±90° の「空き」を探し、選んだ空きの向きへ走る（Gap Follower、7-7〜7-11）。
gaps.py を同じフォルダに置いて使う。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from gaps import (front_view, find_gaps, widest_gap, deepest_gap, gap_center, gap_farthest,
                  add_bubble, extend_disparities)

rc = racecar_core.create_racecar()

FULL_TURN = 30.0     # 目標の向きがこの角度（度）より横にあったら、ハンドルをいっぱいに切る
THRESHOLD = 150.0    # これより遠くまで見える向きを「空き」とする（cm）
PICK = "widest"      # どの空きを選ぶか："widest"（いちばん広い）/ "deepest"（いちばん遠くまで見える）（7-8）
AIM = "center"       # 空きのどこを狙うか："center"（真ん中）/ "farthest"（いちばん遠い点）（7-8）
BUBBLE = 20.0        # 0 でなければ、いちばん近い点のまわりを、この半径（cm）でふさぐ（7-9）
HALF_WIDTH = 20.0    # 0 でなければ、物のはしで、近い距離を、この幅（cm）が入る角度だけのばす（7-10）
JUMP = 50.0          # となりの点との距離の差がこれより大きい所を、物のはしとみなす（7-10）
MIN_SPEED = 0.4      # いちばん遅いときの speed（7-11）
MAX_SPEED = 1.0      # いちばん速いときの speed（7-11。MIN_SPEED と同じなら、一定の速さ）
KV = 0.004           # 目標の向きの距離が 1 cm 遠いごとに、speed をどれだけ上げるか（7-11）

target = 0.0         # 目標の向き（度。右が＋）
speed = 0.0
n_gaps = 0


def start():
    rc.drive.stop()
    print(">> 空きを探して走ります")


def update():
    global target, speed, n_gaps
    angles, dists = front_view(rc.lidar.get_samples())
    if HALF_WIDTH > 0:
        dists = extend_disparities(angles, dists, HALF_WIDTH, JUMP)
    if BUBBLE > 0:
        dists = add_bubble(angles, dists, BUBBLE)

    gaps = find_gaps(dists, THRESHOLD)
    n_gaps = len(gaps)
    if n_gaps == 0:                       # 空きがない：止まる
        speed = 0.0
        rc.drive.stop()
        return

    if PICK == "widest":
        gap = widest_gap(gaps)
    else:
        gap = deepest_gap(gaps, dists)
    if AIM == "center":
        target = gap_center(gap, angles)
    else:
        target = gap_farthest(gap, angles, dists)

    # 目標の向きが遠くまで空いているほど速く（7-11）
    i = int(round((target - angles[0]) / (angles[1] - angles[0])))   # 目標の向きの点の番号
    speed = rc_utils.clamp(MIN_SPEED + KV * (dists[i] - THRESHOLD), MIN_SPEED, MAX_SPEED)
    angle = rc_utils.clamp(target / FULL_TURN, -1.0, 1.0)
    rc.drive.set_speed_angle(speed, angle)


def update_slow():
    print(f"空き {n_gaps} 個　目標の向き {target:+6.1f}°　speed {speed:.2f}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

目標の向きの点の番号 `i` は、角度から逆算しています。`front_view()` の角度は、左はし `angles[0]`（−90°）から 0.5° ずつ並んでいるので、$(\text{target} - (-90)) \div 0.5$ 番めです。

コース A（曲がり角）で走らせると、次のように表示されました。

```text
  0.0 秒 >> 空きを探して走ります
  0.0 秒 空き 1 個　目標の向き   +0.2°　speed 1.00
  1.0 秒 空き 1 個　目標の向き   +0.2°　speed 1.00
  2.0 秒 空き 3 個　目標の向き   +0.2°　speed 1.00
  3.0 秒 空き 2 個　目標の向き   +5.0°　speed 0.64
  4.0 秒 空き 2 個　目標の向き   +5.0°　speed 1.00
  5.0 秒 空き 2 個　目標の向き   +0.5°　speed 1.00
  6.0 秒 空き 2 個　目標の向き  -15.5°　speed 0.92
  7.0 秒 空き 1 個　目標の向き   -2.0°　speed 1.00
  8.0 秒 空き 1 個　目標の向き   -9.8°　speed 0.56
  9.0 秒 空き 1 個　目標の向き  -28.2°　speed 1.00
 10.0 秒 空き 2 個　目標の向き   +0.2°　speed 1.00
```

（左の数字は、スタートからの秒数です。この本で書き足しました。）

### 一定の速さとくらべる

一定の速さ（0.5、0.75、1.0）と、空き具合で決める速さ（0.4〜1.0）を、2つのコースで 5 回ずつ走らせました。

| speed | コース A（曲がり角） | コース B（箱のある通路） |
|---|---|---|
| 一定 0.5 | 5 回ともゴール（45.7〜46.0 秒、42.4 cm 以上） | 5 回ともゴール（37.9〜38.1 秒、57.2 cm 以上） |
| 一定 0.75 | 5 回ともゴール（30.7〜31.1 秒、24.7 cm まで近づいた回がある） | 5 回ともゴール（25.6 秒、59.0 cm 以上） |
| 一定 1.0 | ゴールは 2 回だけ（23.3 秒）。1 回ぶつかり、2 回は 60 秒の間にゴールまで行けなかった | 5 回ともゴール（19.3〜19.5 秒、58.1 cm 以上） |
| 0.4〜1.0（空き具合） | 5 回ともゴール（25.0〜25.1 秒、43.4 cm 以上） | 5 回ともゴール（20.2〜20.4 秒、57.8 cm 以上） |

（距離は、車の中心から、いちばん近い壁や箱までです。）

- **一定 1.0** は、コース B（ゆるやかな曲がりだけ）ではいちばん速いのですが、コース A（直角の曲がり角がある）では、ぶつかったり、ゴールまで行けなかったりしました
- **空き具合で決める速さ**は、コース A でも 5 回ともゴールし、一定 0.5 のときの約 55 %（45.9 秒 → 25.1 秒）の時間で走りきりました。壁からの距離も、一定 0.5 のときとほとんど変わりません

図1の左は、コース A の道すじを、speed で色分けしたものです。まっすぐな所は黄色（1.0）、曲がり角の手前は紫（0.5 前後）になっています。右は、speed の変化です。曲がり角に近づくと、目標の向きの距離が短くなり、speed が 0.5 くらいまで下がって、曲がり終えるとまた 1.0 にもどります。

![左は、コース A を上から見た道すじで、色が speed を表す（0.4 が紺、1.0 が黄色）。まっすぐな所はほとんど黄色で、45° の曲がり角の手前と、直角の曲がり角の手前が、紫やピンクになっている。右は、横軸が時間（0〜50 秒）、縦軸が speed のグラフ。灰色の点線（一定 0.5）は 45.9 秒まで 0.5 のまま。オレンジの線（0.4〜1.0）は、ほとんど 1.0 で、ところどころ 0.46〜0.7 くらいまで下がり、25.1 秒でゴールしている](/images/racecar-neo-jp/7-11/fig1-speed.png)
*図1　前が空いているほど速く走る（説明用の簡単なモデル）*

## ④ 数式・コード

### $K_V$ の決め方

いちばん遅い speed を $v_{\min}$、いちばん速い speed を $v_{\max}$ とし、距離が THRESHOLD のとき $v_{\min}$、MAX_RANGE のとき $v_{\max}$ にしたいなら

$$
K_V = \frac{v_{\max} - v_{\min}}{\text{MAX\_RANGE} - \text{THRESHOLD}} = \frac{1.0 - 0.4}{300 - 150} = 0.004
$$

です。`MIN_SPEED` と `MAX_SPEED` を同じ値にすると、`clamp()` で、いつもその値になるので、一定の速さで走ります（7-7〜7-10 は、どちらも 0.5 にして走らせていました）。

### 6-19 とのちがい

| | 6-19（壁沿い走行） | 7-11（Gap Follower） |
|---|---|---|
| 見る距離 | 正面の壁までの距離 | 目標の向き（これから進む向き）の距離 |
| 決め方 | PID（ねらいの距離との差） | 距離に比例（上と下をおさえる） |
| 曲がるときのハンドル | 速さに合わせてゲインを変える | 変えない |

## ⑤ つまずきポイント

### このモデルの車は、横にすべらない

この回の説明用のモデルの車は、speed 1.0 で 1.5 m/秒 まで出ますが、タイヤが横にすべりません（6-19 の「速い車」のモデルではありません）。実物の車やシミュレーターでは、速く曲がると、横にすべって曲がりきれないことがあります。まずは `MAX_SPEED` を 0.6 くらいにして、少しずつ上げましょう。

### 目標の向きの距離だけを見ている

速さは、目標の向きの1点の距離だけで決めています。目標の向きは空いていても、車の真横に物がある、ということもあります。Nathan Otterness の Disparity Extender（7-10 の原典）では、曲がる側の真横に物があるときは曲がるのをやめる、という工夫もしています。

## ⑥ 確認問題

**問1**　`MIN_SPEED = 0.4`、`MAX_SPEED = 1.0`、`KV = 0.004`、`THRESHOLD = 150` のとき、目標の向きの距離が 200 cm なら、speed はいくつですか。

:::details 答え
$0.4 + 0.004 \times (200 - 150) = 0.4 + 0.2 = 0.6$ です。0.4〜1.0 の間なので、そのまま 0.6 です。
:::

**問2**　いちばん遅い speed を 0.3、いちばん速い speed を 0.8 にしたいとき、`KV` はいくつにすればよいですか（しきい値 150 cm、`MAX_RANGE` 300 cm）。

:::details 答え
$(0.8 - 0.3) \div (300 - 150) = 0.5 \div 150 \approx 0.0033$ です。
:::

## ⑦ 原典

`gap_follow.py`・図1と表の数字は、この本で作ったものです（説明用の簡単なモデル）。

- 正面の空き具合で速さを決め、曲がる側の真横に物があるときは曲がるのをやめる工夫：Nathan Otterness, [The "Disparity Extender" Algorithm, and F1/Tenth](https://www.nathanotterness.com/2019/04/the-disparity-extender-algorithm-and.html)（2019 年）
- `clamp()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）
