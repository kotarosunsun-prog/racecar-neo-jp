---
title: "9-4 コラム：実機での調整"
free: true
---

シミュレータで合わせた数値は、実機ではたいてい合いません。`speed` は速さそのものではなく「アクセルの踏み込み具合」なので、床のすべりやすさ、バッテリーの残り、車の重さで、実際の速さが変わるからです（4-2）。このコラムでは、実機で数値を合わせ直す手順をまとめます。新しい考え方は少なく、8-2 の「まず測る」「1つずつ変える」「何回も走らせる」を、実機でくり返します。

## ① この回でできるようになること

1. 実機で数値を合わせ直す順番を言える
2. 車輪の速さのセンサと `rc.telemetry` で、`speed` と実際の速さの関係を測れる
3. バッテリーの残りで、走りが変わることを考えに入れて、調整できる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Encoder | エンコーダ | 車輪（モーター）の回転を数えるセンサ。実機の `get_encoder_speed()` の元 |
| Telemetry | テレメトリ | 走っている間の値を記録して、あとで表やグラフで見るしくみ |
| Calibration | 較正（こうせい） | 命令の値と、実際の値の関係を測って合わせること |
| Repeatability | くり返しの安定さ | 同じ条件で何回走らせても、同じ結果になること |

## ③ 本文

### 合わせ直す順番

下から順に、1つずつ確かめます。下のものが合っていないと、上のものは合わせられません。

1. **ハンドルと車輪の向き**：車輪を浮かせて、`angle` が＋のとき右に切れるか、`speed` が＋のとき前に回るか（9-1）
2. **センサ**：`real_check.py` で、LIDAR の点の数と距離、カメラ、電圧（9-1）。ガラスや鏡がないか（9-3）
3. **速さ**：`speed` と実際の速さの関係（この回の `speed_log.py`）
4. **止まるまでの距離**：7-1 の `brake_test.py` で測り直し、`STOP_PER_SPEED` を決め直す
5. **時間で決めている動き**：4-2 のような「何秒まっすぐ、何秒曲がる」は、3 で測った速さをもとに、時間を決め直す
6. **PID の係数**：第6章の手順で、P から順に合わせ直す
7. **状態ごとの速さ**：8-2 の手順で、1つずつ上げる

### `speed` と実際の速さを測る

実機では、`rc.physics.get_encoder_speed()` で、車輪の回転から測った速さ（m/秒）がわかります（シミュレータでは 0.0）。次のプログラムは、A ボタンを押すと 2 秒まっすぐ走り、その間の値を `rc.telemetry` で記録します。

```python:speed_log.py
"""
speed_log.py（実機用）
A ボタンを押すと、まっすぐ RUN_TIME 秒だけ走って止まる（9-4）。
走っているあいだ、speed の命令・車輪で測った速さ・バッテリーの電圧を、rc.telemetry で記録する。
記録は labs/logs フォルダに、CSV（表）と PNG（グラフ）で保存される。
Y ボタンで speed を 0.1 上げ、X ボタンで 0.1 下げる。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core

rc = racecar_core.create_racecar()

RUN_TIME = 2.0         # 1 回に走る時間（秒）
speed = 0.3            # 走るときの speed
running = False
timer = 0.0
fastest = 0.0          # 1 回の走りで、いちばん速かった速さ（m/秒）


def start():
    rc.drive.set_max_speed(0.25)
    rc.drive.stop()
    rc.telemetry.declare_variables("speed", "encoder_m_s", "voltage")
    print(f">> A ボタンで {RUN_TIME} 秒まっすぐ走ります。Y・X ボタンで speed を変えます（今 {speed:.1f}）")


def update():
    global speed, running, timer, fastest
    if not running:
        if rc.controller.was_pressed(rc.controller.Button.A):
            running, timer, fastest = True, 0.0, 0.0
            print(f"speed {speed:.1f} で走ります")
        if rc.controller.was_pressed(rc.controller.Button.Y):
            speed = min(speed + 0.1, 1.0)
            print(f"speed {speed:.1f}")
        if rc.controller.was_pressed(rc.controller.Button.X):
            speed = max(speed - 0.1, 0.1)
            print(f"speed {speed:.1f}")
        rc.drive.stop()
        return

    timer += rc.get_delta_time()
    measured = rc.physics.get_encoder_speed()
    fastest = max(fastest, measured)
    rc.telemetry.record(speed, measured, rc.physics.get_battery_voltage())
    rc.drive.set_speed_angle(speed, 0.0)
    if timer >= RUN_TIME:
        running = False
        rc.drive.stop()
        rc.telemetry.visualize()               # 実機では、自分で呼ばないとグラフが保存されない
        print(f"止まりました。いちばん速かったのは {fastest:.2f} m/秒")


def update_slow():
    pass


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

- `rc.telemetry.declare_variables()` で、記録する値の名前を決めます。はじめに 1 回だけ呼びます
- `rc.telemetry.record()` で、名前と同じ順番に値を渡します。時間は自動で記録されます
- 記録は、labs フォルダの中の `logs` フォルダに、日時とファイル名の付いた CSV（表）で保存されます
- `rc.telemetry.visualize()` で、グラフ（PNG）を保存します。シミュレータでは、プログラムを終えたときに自動で呼ばれますが、実機では呼ばれないので、自分で呼びます

この本で作った代わりの `racecar_core` で動かすと、次のように表示されました（モデルの車は、`speed` 1.0 で 1.5 m/秒になるように作ってあります）。実機では、この値はちがいます。

```text
>> A ボタンで 2.0 秒まっすぐ走ります。Y・X ボタンで speed を変えます（今 0.3）
speed 0.3 で走ります
止まりました。いちばん速かったのは 0.45 m/秒
speed 0.4
speed 0.4 で走ります
止まりました。いちばん速かったのは 0.60 m/秒
```

実機で、`speed` を 0.1 ずつ変えながら 3 回ずつ測り、表にしましょう。`speed` を 2 倍にしても、速さはぴったり 2 倍にはならないことが多いです（小さい `speed` では、摩擦で動かないこともあります）。

### 走らせる条件をそろえる

実機では、同じプログラムでも、条件で結果が変わります。調整の間は、次のことをそろえます。

- **バッテリー**：電圧が下がると、同じ `speed` でも遅くなります。調整の前に `real_check.py` で電圧を確かめ、記録に残します（`speed_log.py` は電圧も記録しています）。電圧が大きくちがう日の結果は、そのまま比べません
- **床とタイヤ**：ほこりや、床の材質で、すべり方が変わります。本番と同じ床で調整します
- **スタートの位置と向き**：テープで印を付けて、毎回同じ所から走らせます

### 1つずつ変えて、何回も走らせる

8-2 と同じく、変えるのは一度に 1つだけです。変えるたびに 5 回ずつ走らせて、いちばん速い回ではなく、5 回の中のばらつき（いちばん遅い回、ぶつかった回）を見ます。実機では、1 回走らせるのに時間がかかり、バッテリーも減ります。変える数値の候補を、あらかじめ紙に書いて、順番を決めておくとよいでしょう。

## ④ 数式・コード

### 速さと距離

速さ $v$（m/秒）で $t$ 秒走ると、進む距離は $v \times t$ です。4-2 のように「1 m まっすぐ進む」時間は、次のように決め直せます。

$$
t = \frac{\text{進みたい距離}}{v}
$$

たとえば、`speed_log.py` で `speed` 0.4 のとき 0.6 m/秒と測れたら、1 m 進むには $1 \div 0.6 \approx 1.7$ 秒です。ただし、走りはじめは速さが 0 から上がっていくので、実際には少し長めになります。記録の CSV で、速さが上がりきるまでの時間を確かめましょう。

### 記録を読む

保存された CSV は、表計算のアプリや、Python の `pandas` で開けます。

```python
import pandas as pd

log = pd.read_csv("logs/20260926_101500_speed_log.csv")   # 自分のファイル名に変える
print(log["encoder_m_s"].max())                           # いちばん速かった速さ
print(log["voltage"].mean())                              # 電圧の平均
```

1 行めには、`time` と、`declare_variables()` で決めた名前が並びます。

## ⑤ つまずきポイント

### グラフ（PNG）が保存されない

実機では、`rc.telemetry.visualize()` を自分で呼ばないと、グラフは保存されません。CSV は、`record()` のたびに書きこまれています。

### `declare_variables()` を 2 回呼んだら、名前が変わらない

`declare_variables()` は、はじめの 1 回だけが使われ、2 回め以降は何もしません。名前を変えたいときは、プログラムを終えて、動かし直します。

### 昨日合わせた数値で、今日は曲がりきれない

バッテリーの電圧がちがうか、床がちがう可能性があります。電圧を記録しておくと、原因を見つけやすくなります（9-2）。

## ⑥ 確認問題

**問1**　`speed` 0.3 で 0.45 m/秒、`speed` 0.4 で 0.60 m/秒と測れました。1.5 m まっすぐ進むには、`speed` 0.4 で何秒走らせればよいですか（走りはじめの加速は考えない）。

:::details 答え
$1.5 \div 0.60 = 2.5$ 秒です。実際には、加速の分だけ少し長めにして、測って確かめます。
:::

**問2**　PID の係数を合わせる前に、ハンドルの向きと、止まるまでの距離を確かめるのはなぜですか。

:::details 答え
ハンドルの向きが逆だと、PID はずれを大きくする向きに切ってしまい、どんな係数でも合わせられないからです。止まるまでの距離がわからないと、安全停止（7-1）が間に合うかどうかわからず、係数を試している間に、ぶつかるおそれがあるからです。
:::

## ⑦ 原典

- `rc.telemetry` の `declare_variables()`・`record()`・`visualize()`、保存先（labs/logs）と、シミュレータだけプログラムの終わりに自動で `visualize()` を呼ぶこと：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `telemetry.py`・`real/telemetry_real.py`・`simulation/racecar_core_sim.py`（GPL-3.0）
- `rc.physics.get_encoder_speed()`（実機は車輪の回転から測った m/秒、シミュレータは 0.0）：同じく `physics.py`・`real/physics_real.py`

`speed_log.py` と、調整の順番は、この本で作ったものです。表示の例は、この本で作った説明用の簡単なモデルによるもので、実機の値ではありません。
