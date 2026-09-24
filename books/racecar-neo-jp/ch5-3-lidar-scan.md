---
title: "5-3 LIDAR スキャンの読み方"
free: true
---

2-3 では、LIDAR が車のまわりをぐるりと測り、720個の距離を返すことを学びました。この回では、その720個の数から、「右の壁までの距離」や「いちばん近い物はどちらにあるか」のような、走るのに役立つ情報を取り出します。第6章の壁沿い走行と、第7章の安全停止・Gap Follower の土台になります。

## ① この回でできるようになること

1. 720個の値の番号と、向き（角度）を行き来できる
2. 決まった向きの距離を、ノイズに強い形で求められる
3. いちばん近い物の向きと距離を、決まった範囲の中から求められる
4. 「データなし」を表す 0.0 を、正しく取りのぞける

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Scan | スキャン | LIDAR が1周測った、720個の距離のまとまり |
| Sample | サンプル（測定点） | スキャンの中の1つの距離 |
| Window | 窓（まど） | 「この角度からこの角度まで」という、調べる範囲 |
| Noise | ノイズ | 測るたびに少しずつばらつく、細かいずれ |
| Polar coordinates | 極座標 | 位置を「向き」と「距離」で表す方法 |
| NumPy | NumPy | 数の並び（配列）をまとめて計算するための Python のライブラリ。`np` という名前で読みこむ |

## ③ 本文

### おさらい：720個の距離

`rc.lidar.get_samples()` が返すのは、次のような数の並び（NumPy の配列）です（2-3）。

- 720個の小数（float）が入っている。シミュレータでも実機でも同じ形
- 0番めは車の**真正面**。そこから**時計回り**に 0.5° ずつ進む
- 単位は **cm**
- **0.0 は「データなし」**。近すぎる・遠すぎる・光が返ってこない、などで測れなかった点

### 番号と角度を行き来する

番号 $i$ の点の角度と、角度 $\theta$ の点の番号は、次の式で行き来できます。`len(scan)` は点の数（720）です。

$$
\theta = i \times \frac{360}{\text{len(scan)}}, \qquad
i = \theta \times \frac{\text{len(scan)}}{360}
$$

| 向き | 角度 | 番号 |
|---|---|---|
| 前 | 0° | 0 |
| 右 | 90° | 180 |
| 後ろ | 180° | 360 |
| 左 | 270° | 540 |

![LIDAR の測定点を上から見た図。車は中央にあり、前が上。左右に廊下の壁、前方 350 センチに正面の壁、右前に右へ曲がる通路の入り口がある。左前の小さな箱が、いちばん近い点（337度の向き、約66センチ）としてオレンジで示されている。前は scan[0]、右は scan[180]、後ろは scan[360]、左は scan[540] で、番号は時計回りに増える。箱の陰になった左の壁は測れていない](/images/racecar-neo-jp/5-3/fig1-scan.png)
*図1　LIDAR の測定点を上から見た図（説明用に作ったデータ）*

`scan[90]` は 90° ではなく、$90 \times \frac{360}{720} = 45°$、つまり**右ななめ前**です。番号と角度を取り違えないようにしましょう。

図1からは、次のこともわかります。

- 車のうしろ（180° あたり）は、測れる範囲に何もないので、0.0 になっている（図には描いていない）
- 左前の箱の**陰**になった壁は、測れない。LIDAR は、光が届く一番手前の物しか測れない

### 決まった向きの距離：まわりの点も使って平均する

`scan[180]` で右の距離はわかりますが、1つの点だけでは、たまたまノイズで大きくずれていたり、0.0 だったりすることがあります。そこで、`racecar_utils` の次の関数を使います。

```python
right = rc_utils.get_lidar_average_distance(scan, 90)
```

これは、90° を中心に、まわり 4°（左右に 2° ずつ）の点の平均を返します。0.0 の点は平均に入れません。3つめの引数で、平均する幅を変えられます（`get_lidar_average_distance(scan, 90, 10)` なら 10°）。幅を広げるほどノイズに強くなりますが、そのぶん、細かい形はぼやけます。

### いちばん近い点を見つける

```python
angle, distance = rc_utils.get_lidar_closest_point(scan)
```

いちばん近い点の**角度**と**距離**を、組にして返します。こちらも 0.0 の点は無視します。

調べる範囲（窓）を、2つめの引数で指定できます。

```python
_, front = rc_utils.get_lidar_closest_point(scan, (315, 45))    # 前の 90° の範囲
_, back = rc_utils.get_lidar_closest_point(scan, (135, 225))    # 後ろの 90° の範囲
```

`(315, 45)` のように、0° をまたぐ窓も書けます。「315° から時計回りに 45° まで」、つまり正面を中心に左右 45° ずつの範囲です。角度だけいらないときは、`_`（使わない変数）で受けます。

### やってみよう：まわりの距離を表示する

次のプログラムは、1秒ごとに、前・右・後ろ・左の距離と、いちばん近い点を表示します。トリガーとスティックで車を動かしながら、数がどう変わるかを確かめましょう。

```python:lidar_check.py
"""
lidar_check.py
1秒ごとに、前・右・後ろ・左の距離と、いちばん近い物の向きと距離を表示する。
トリガーとスティックで車を動かせる。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()


def start():
    rc.drive.stop()
    print(">> 1秒ごとに、LIDAR で測った距離を表示します")


def update():
    # 手動で動かす（3-2 と同じ）
    speed = (rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
             - rc.controller.get_trigger(rc.controller.Trigger.LEFT)) * 0.5
    (x, y) = rc.controller.get_joystick(rc.controller.Joystick.LEFT)
    rc.drive.set_speed_angle(speed, x)

    # LIDAR の点を画面に表示し、いちばん近い点を水色で目立たせる
    scan = rc.lidar.get_samples()
    closest = rc_utils.get_lidar_closest_point(scan)
    rc.display.show_lidar(scan, highlighted_samples=[closest])


def update_slow():
    scan = rc.lidar.get_samples()

    # 決まった向きの距離（まわり 4° の平均）
    front = rc_utils.get_lidar_average_distance(scan, 0)
    right = rc_utils.get_lidar_average_distance(scan, 90)
    back = rc_utils.get_lidar_average_distance(scan, 180)
    left = rc_utils.get_lidar_average_distance(scan, 270)

    # いちばん近い点の向きと距離
    angle, distance = rc_utils.get_lidar_closest_point(scan)

    print(f"前 {front:.0f}  右 {right:.0f}  後ろ {back:.0f}  左 {left:.0f} cm")
    print(f"  いちばん近い点：{angle:.1f}° の向き、{distance:.0f} cm")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

シミュレータのレベルは、**Sandbox Environments** の **LIDAR Sandbox** がおすすめです（スペースキーで、車を外から見るカメラに切りかえられます）。図1のデータを渡すと、次のように表示されました。後ろの 0 は、「測れる範囲に何もない」ことを表しています。

```text
前 350  右 71  後ろ 0  左 80 cm
  いちばん近い点：338.0° の向き、65 cm
```

`rc.display.show_lidar()` は、測った点を、車を真ん中にした上から見た図として、別のウィンドウに表示します。

## ④ 数式・コード

### 向きと距離から、上から見た位置へ

LIDAR の点は、「向き $\theta$」と「距離 $d$」で表されています（**極座標**）。これを、車から見て右を $x$、前を $y$ とした位置に直すには、次の式を使います。角度は正面から時計回りなので、ふつうの数学の座標とは $\sin$ と $\cos$ が入れかわっています。

$$
x = d \sin\theta, \qquad y = d \cos\theta
$$

NumPy を使うと、720個の点をまとめて変換できます。0.0 の点は、先に取りのぞきます。図1は、この計算で描いています。

```python
import numpy as np

scan = rc.lidar.get_samples()
angles = np.arange(len(scan)) * 360 / len(scan)   # 0, 0.5, 1.0, ... の720個の角度
valid = scan > 0                                   # データがある点だけ True
x = scan[valid] * np.sin(np.radians(angles[valid]))   # 右方向の位置（cm）
y = scan[valid] * np.cos(np.radians(angles[valid]))   # 前方向の位置（cm）
```

`scan > 0` は、720個それぞれが 0 より大きいかを True / False で並べたものです。これを `scan[ ]` の中に入れると、True の点だけを取り出せます。

### 0.0 をのぞいて、いちばん小さい値を求める

```python
nearest = np.min(scan[scan > 0])
```

`min(scan)` と書くと、0.0（データなし）がいちばん小さい値として選ばれてしまいます（⑤）。

## ⑤ つまずきポイント

### いちばん近い距離が、いつも 0.0 になる

`min(scan)` や `np.min(scan)` を使うと、「データなし」の 0.0 が選ばれます。図1のデータでも `min(scan)` は 0.0 で、0.0 をのぞくと約 65.7 cm でした。`scan[scan > 0]` で 0.0 をのぞくか、`get_lidar_closest_point()` を使いましょう。

### `scan[90]` が、右の距離にならない

番号 90 は 45°（右ななめ前）です。右（90°）は番号 180 です。角度から番号を求めるときは、$\theta \times \frac{\text{len(scan)}}{360}$ を計算します。

### 左の距離を −90° で求めてもよい？

`get_lidar_average_distance()` と `get_lidar_closest_point()` は、中で角度を 0〜360 に直すので、−90° と 270° は同じ結果になります。`(−45, 45)` と `(315, 45)` も同じです。ただし、配列の番号として `scan[-180]` と書くと、「後ろから180番め」（番号 540 ＝ 左）という意味になり、角度とは関係なく動きます。

### `print(closest)` で `np.float64(...)` のように表示される

NumPy の新しいバージョンでは、組をそのまま表示すると、数の種類まで表示されます。値はふつうの数と同じように使えます。見やすくしたいときは、`f"{angle:.1f}"` のように書式を指定して表示します。

### ガラスや鏡のまわりで、おかしな値になる

LIDAR は光の反射で測るので、光を通すガラスや、光をはね返す鏡、黒くて光を吸う物は、うまく測れないことがあります。ライブラリの説明にも、ガラス・鏡・広い空間では誤差が大きくなりやすいと書かれています。

## ⑥ 確認問題

**問1**　30° の向きの点は、何番めですか。また、600番めの点は、何度の向きですか。

:::details 答え
$30 \times \frac{720}{360} = 60$ 番めです。
$600 \times \frac{360}{720} = 300°$ で、左ななめ前（正面から反時計回りに 60°）です。
:::

**問2**　車の後ろの 60° の範囲（後ろを中心に左右 30° ずつ）で、いちばん近い物までの距離を求める1行を書きましょう。

:::details 答えの例
```python
_, back_distance = rc_utils.get_lidar_closest_point(scan, (150, 210))
```
:::

**問3**　決まった向きの距離を、1つの点ではなく、まわりの点の平均で求めるのはなぜですか。

:::details 答え
1つの点だけだと、ノイズで大きくずれていたり、0.0（データなし）だったりすることがあるからです。まわりの点の平均をとると、ばらつきが小さくなり、0.0 の点も取りのぞけます。
:::

**問4**　ある点の向きが 30°、距離が 200 cm でした。車から見て、右に何 cm、前に何 cm のところにありますか。

:::details 答え
右に $200 \times \sin 30° = 100$ cm、前に $200 \times \cos 30° \approx 173$ cm です。
:::

## ⑦ 原典

- `get_lidar_closest_point()`・`get_lidar_average_distance()`（0.0 の扱い、0° をまたぐ窓、ガラス・鏡についての注意）：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）
- `show_lidar()`：同じく `display.py`
- シミュレータの LIDAR（720点、時計回り、cm）と LIDAR Sandbox：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `Lidar.cs`・`LevelCollection.cs`

図1は、説明のために作った LIDAR のデータです。`lidar_check.py` と⑤の値は、このデータを1コマずつ渡すプログラムで確かめたものです。
