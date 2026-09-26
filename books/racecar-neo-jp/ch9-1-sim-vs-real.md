---
title: "9-1 シミュレータから実機へ"
free: true
---

第1章〜第8章では、シミュレータの中の車を動かしてきました。同じ `racecar_core` の命令は、実機でもそのまま使えます。ただ、実機は、ぶつかれば壊れ、人がけがをすることもあります。速さの上限や、使えるセンサなど、シミュレータとちがうところもあります。この回では、実機でプログラムを動かす手順と、シミュレータとのちがいをまとめ、センサの値を確かめるプログラムを作ります。

## ① この回でできるようになること

1. 実機でプログラムを動かし、止め、終える手順を言える
2. シミュレータと実機のちがいを、表で確かめられる
3. 実機を走らせる前に、センサの値と `update()` の回数を確かめられる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Physical car | 実機 | 本物の RACECAR |
| Default drive mode | ふつうの運転モード | ライブラリに入っている、ゆっくり走る手動運転 |
| User program mode | プログラムのモード | 自分が書いた `start()`・`update()` が動くモード |
| Autonomy gate | 関所 | RB を押している間だけ、プログラムの命令が車に届くしくみ（2-4） |
| Max speed | 速さの上限 | `speed` にかけられる倍率。`set_max_speed()` で決める |

## ③ 本文

### 実機でプログラムを動かす

シミュレータでは、パソコンで `racecar sim ファイル名.py` を実行し、シミュレータで Enter を押しました。実機では、車のコンピュータ（Raspberry Pi 5、2-4）の上で、`-s` をつけずに実行します（5-12）。

```bash
python3 real_check.py
```

ゲームパッドのボタンで、次のように操作します。

| ボタン | すること |
|---|---|
| START | プログラムのモードに入る（`start()` が 1 回、そのあと `update()` がくり返し呼ばれる） |
| BACK | ふつうの運転モードにもどる（右トリガーで前へ、左トリガーで後ろへ、左スティックでハンドル） |
| BACK と START を同時に | プログラムを終える |
| RB を押し続ける | プログラムの命令が車に届く（2-4）。はなすと、車は止まる |

プログラムのモードに入っても、RB を押していないと、車は動きません。危ないと思ったら、すぐに RB をはなします。

### シミュレータと実機のちがい

| | シミュレータ | 実機 | くわしくは |
|---|---|---|---|
| 動かし方 | `racecar sim ファイル名.py`、Enter | `python3 ファイル名.py`、START | この回 |
| 車が動く条件 | プログラムのモードなら、いつでも | RB を押している間だけ | 2-4 |
| `set_max_speed()` のはじめの値 | 0.25 | 0.50 | この回 |
| `update()` の回数 | 1 秒に約 60 回 | 1 秒に約 60 回（おくれることがある） | この回 |
| LIDAR の点の数 | 720 点（0.5° ごと） | 同じ | 2-3 |
| LIDAR で測れない物 | ほとんどない | ガラス・鏡・黒い物 | 9-3 |
| IMU の軸の向き | シミュレータ独自 | 実機のセンサの向き | 5-5 |
| バッテリーの電圧・電流、車輪の速さ | 0.0 | 使える | 9-2・9-4 |
| 物体検出 `rc.vision` | ない | 使える | 9-5 |
| `rc.telemetry` のグラフ | プログラムを終えると自動で保存 | 自分で `visualize()` を呼ぶ | 9-4 |
| ぶつかったとき | やり直せばよい | 車が壊れる。人がけがをする | この回 |

### 速さの上限：同じ `speed` でも、実機は 2 倍

`rc.drive.set_speed_angle(speed, angle)` の `speed` は、そのまま車に送られるのではなく、`set_max_speed()` で決めた上限がかけられます。

$$
\text{車に送られる速さ} = \texttt{speed} \times \text{上限}
$$

上限のはじめの値は、シミュレータが 0.25、実機が 0.50 です。何もしないと、同じ `speed = 0.5` でも、実機はシミュレータの 2 倍の速さの命令になります。実機で、シミュレータのときと同じ命令にしたいときは、`start()` で上限を 0.25 にしておきます。

```python
def start():
    rc.drive.set_max_speed(0.25)     # シミュレータと同じ上限にする
```

この章の、車を動かすプログラムは、すべて、はじめにこうしています。上限を同じにしても、実機とシミュレータでは、床のすべりやすさやバッテリーの残りで、実際の速さは変わります（4-2）。実際の速さを測る方法は、9-4 で学びます。

### `update()` の回数

実機でも、`update()` は 1 秒に約 60 回呼ばれます。ただ、カメラの画像の処理などで 1 回の `update()` に時間がかかると、次の呼び出しがおくれます。`rc.get_delta_time()` は、前のコマからの本当の時間を返すので、PID（第6章）のように時間を使う計算は、いつも `rc.get_delta_time()` を使いましょう。

### センサの値を確かめるプログラム

実機を走らせる前に、センサの値と、`update()` の回数を確かめます。次のプログラムは、車を動かさずに、1 秒に 1 回、値を表示します。シミュレータでも実機でも動きます。

```python:real_check.py
"""
real_check.py
実機とシミュレータのちがいを、センサの値を表示して確かめる（9-1）。車は動かさない。
シミュレータ：racecar sim real_check.py　　実機：python3 real_check.py
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

frames = 0          # 1 秒の間に update() が呼ばれた回数
dt_max = 0.0        # 1 秒の間で、いちばん長かった 1 コマの時間（秒）


def start():
    rc.drive.set_max_speed(0.25)     # 実機では、はじめは上限を小さくしておく（9-1）
    rc.drive.stop()
    print(">> センサの値を 1 秒ごとに表示します（車は動かしません）")


def update():
    global frames, dt_max
    frames += 1
    dt_max = max(dt_max, rc.get_delta_time())
    rc.drive.stop()


def update_slow():
    global frames, dt_max
    scan = rc.lidar.get_samples()
    n = len(scan)
    front = rc_utils.get_lidar_average_distance(scan, 0)        # 正面（0° のまわりの平均）
    right = rc_utils.get_lidar_average_distance(scan, 90)
    zeros = int((scan == 0).sum())                               # 測れなかった点の数
    image = rc.camera.get_color_image()
    size = "なし" if image is None else f"{image.shape[1]}×{image.shape[0]}"
    print(f"LIDAR {n} 点（1 点 {360 / n:.2f}°、測れない点 {zeros}）　正面 {front:.0f} cm　右 {right:.0f} cm")
    if hasattr(rc, "vision"):                                   # シミュレータの rc には vision がない
        found = f"{len(rc.vision.get_detections())} 個"
    else:
        found = "（rc.vision なし）"
    print(f"  カメラ {size}　電圧 {rc.physics.get_battery_voltage():.2f} V　"
          f"車輪 {rc.physics.get_encoder_speed():.2f} m/秒　見つけた物 {found}")
    print(f"  update() {frames} 回/秒（いちばん長いコマ {dt_max * 1000:.0f} ミリ秒）")
    frames, dt_max = 0, 0.0


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

- `rc_utils.get_lidar_average_distance(scan, 0)` のように、角度で距離を読みます。1 点だけでなく、そのまわりの点の平均なので、ばらつきに強くなります（5-3）
- `hasattr(rc, "vision")` は、「`rc` に `vision` があるか」を調べます。シミュレータの `rc` には `vision` がないので、そのまま `rc.vision` と書くとエラーになります
- `frames` と `dt_max` で、1 秒に `update()` が何回呼ばれたかと、いちばん長かった 1 コマの時間を数えます

この本で作った代わりの `racecar_core` で、6-18 のコースに車を置いて動かすと、次のように表示されました（2 秒めの表示です）。実機の値ではありません。実機では、電圧はバッテリーによって変わり、見つけた物の数は、カメラに写っている物で変わります。

```text
（シミュレータに近い設定）
LIDAR 720 点（1 点 0.50°、測れない点 0）　正面 607 cm　右 76 cm
  カメラ 640×480　電圧 0.00 V　車輪 0.00 m/秒　見つけた物 （rc.vision なし）
  update() 60 回/秒（いちばん長いコマ 17 ミリ秒）
（実機に近い設定）
LIDAR 720 点（1 点 0.50°、測れない点 0）　正面 607 cm　右 75 cm
  カメラ 640×480　電圧 8.05 V　車輪 0.00 m/秒　見つけた物 0 個
  update() 60 回/秒（いちばん長いコマ 17 ミリ秒）
```

実機で動かしたら、次のことを確かめましょう。

1. LIDAR の点の数が 720 か。正面と右の距離が、巻き尺で測った距離と合っているか（ずれていたら、ガラスや黒い物がないか。9-3）
2. 測れない点が、ふだんより多すぎないか
3. 電圧が、満充電の 2S のバッテリーなら 8 V 前後か（9-2）
4. `update()` が 1 秒に 60 回近くか。いちばん長いコマが、大きくなりすぎていないか

### はじめて走らせるときの手順

1. 車を台の上に載せて、車輪を浮かせる
2. `real_check.py` で、センサの値を確かめる
3. 走らせたいプログラムを、車輪を浮かせたまま動かし、RB を押して、ハンドルの向き（右に切ると右に曲がるか）と、車輪の回る向きを確かめる
4. 広い場所で、人が車の前に立たないようにして、ゆっくり（`set_max_speed(0.25)`、小さい `speed`）走らせる。RB から、いつでも指をはなせるようにしておく

## ④ 数式・コード

### 1 秒の中で、いちばん長いコマ

`update()` が 1 秒に $N$ 回呼ばれたとき、1 コマの時間の平均は $1/N$ 秒です。60 回なら約 17 ミリ秒です。

$$
\text{平均の 1 コマ} = \frac{1}{N} \ \text{秒}
$$

平均が 17 ミリ秒でも、ときどき 100 ミリ秒かかるコマがあると、その間、車は前の命令のまま進みます。速さが 1 m/秒なら、100 ミリ秒で 10 cm 進みます。`real_check.py` が平均ではなく、いちばん長いコマを表示するのは、このためです。

## ⑤ つまずきポイント

### START を押したのに、車が動かない

RB を押しているか確かめましょう（2-4）。`real_check.py` のように `rc.drive.stop()` を呼び続けるプログラムでは、RB を押しても動きません。

### 実機で `rc.vision` を使わないのに、`hasattr` を書くのはなぜ？

同じファイルを、シミュレータでも実機でも動かせるようにするためです。シミュレータで `rc.vision` を使うと、`AttributeError` で止まります。

### シミュレータよりずっと速く走った

`set_max_speed()` のはじめの値が、実機は 0.50 だからです。`start()` で `rc.drive.set_max_speed(0.25)` を呼びましょう。

## ⑥ 確認問題

**問1**　`set_max_speed()` を呼ばずに、実機で `rc.drive.set_speed_angle(0.6, 0)` とすると、車に送られる速さは、シミュレータの何倍ですか。

:::details 答え
シミュレータは $0.6 \times 0.25 = 0.15$、実機は $0.6 \times 0.50 = 0.30$ なので、2 倍です。
:::

**問2**　実機のプログラムを終えるには、どうしますか。車をすぐ止めたいときは、どうしますか。

:::details 答え
プログラムを終えるには、BACK と START を同時に押します。車をすぐ止めたいときは、押している RB から指をはなします。
:::

**問3**　`real_check.py` で「update() 60 回/秒（いちばん長いコマ 120 ミリ秒）」と表示されました。速さ 0.8 m/秒で走っているとき、そのコマの間に、車は何 cm 進みますか。

:::details 答え
$0.8 \times 0.12 = 0.096$ m、約 10 cm です。
:::

## ⑦ 原典

- 実機での START・BACK・BACK と START（終える）の働き、ふつうの運転モードの操作、1 秒に 60 回の `update()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `real/racecar_core_real.py`（GPL-3.0）
- `set_max_speed()` のはじめの値（シミュレータ 0.25、実機 0.50）と、`speed` に上限をかけること：同じく `drive.py`・`real/drive_real.py`
- 実機に `rc.vision` があり、シミュレータにないこと：同じく `real/racecar_core_real.py`・`simulation/racecar_core_sim.py`
- RB の関所：[racecar_neo_ros2_driver](https://github.com/MITRacecarNeo/racecar_neo_ros2_driver)（GPL-3.0）の README（Autonomy gate）
- `rc.drive`・`rc.lidar`・`rc.physics`・`rc.vision`・`rc.telemetry` などの関数の説明（関数の定義集）：[racecar-neo-library documentation, Modules](https://mitracecarneo.github.io/racecar-neo-library/modules/index.html)

`real_check.py` は、この本で作ったものです。表示の例は、この本で作った説明用の簡単なモデル（上から見た2次元の車と壁、LIDAR の計算）によるもので、実機の値ではありません。ドライバとライブラリは更新が続いているので、操作方法は変わることがあります。
