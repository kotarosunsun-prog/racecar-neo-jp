---
title: "6-8 ふらつきを観察する"
free: true
---

6-7 の P 制御では、車は壁にそって走るものの、行ったり来たりの揺れ（ふらつき）が止まらず、だんだん大きくなりました。この回では、走りの**記録**（ログ）をとってグラフにし、揺れの様子をくわしく見ます。そして、P 制御だけでは揺れが止まらない理由を考えます。

## ① この回でできるようになること

1. 毎コマの値をファイル（CSV）に書き出して、記録をとれる
2. 記録を読みこんで、matplotlib でグラフにできる
3. 「ずれが 0 でも、車はななめを向いている」ことから、行き過ぎる理由を説明できる
4. 遅れがあると、揺れがだんだん大きくなることを説明できる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Log | 記録（ログ） | プログラムが動いた様子を、あとで調べられるように残したもの |
| CSV | CSV | 値をカンマ（,）で区切って並べた、表のファイル |
| Overshoot | 行き過ぎ | 目標をこえて、反対側まで行ってしまうこと |
| Delay / Lag | 遅れ | 命令や測った値が、少し前のものになっていること |

## ③ 本文

### 1秒に1回の表示では足りない

6-7 では、`update_slow()` で1秒に1回、値を表示しました。でも、プログラムは1秒に 60 回動いています。1秒に1回の表示では、その間に何が起きたのかがわかりません。そこで、**毎コマの値をファイルに書き出して**、あとからグラフで見ることにします。

### 記録をとる

6-7 の `wall_follow_p.py` に、次の3か所を足します。`wall_follow_p_log.py` という名前で保存しましょう。

```python
# ① 変数を足す（distance と angle の下）
t = 0.0           # 走り始めてからの時間（秒）
log_file = None   # 記録を書き出すファイル


# ② start() で、ファイルを開いて、1行めに列の名前を書く
def start():
    global t, log_file
    rc.drive.stop()
    t = 0.0
    log_file = open("wall_log.csv", "w", buffering=1)   # buffering=1：1行ごとにすぐ書きこむ
    log_file.write("time,distance,error,angle\n")      # 1行め：列の名前
    print(f">> 右の壁から {TARGET:.0f} cm を保って走ります（P 制御、KP = {KP}）。記録は wall_log.csv")


# ③ update() の最後で、1行ずつ書く（global に t を足すのを忘れずに）
def update():
    global distance, angle, t
    # （ここまでは 6-7 と同じ）

    rc.drive.set_speed_angle(SPEED, angle)

    # 記録：壁が見えているコマだけ、1行ずつ書く
    t += rc.get_delta_time()
    if distance is not None:
        log_file.write(f"{t:.3f},{distance:.2f},{distance - TARGET:.2f},{angle:.3f}\n")
```

:::details wall_follow_p_log.py の全体
```python:wall_follow_p_log.py
"""
wall_follow_p_log.py
wall_follow_p.py に、記録（ログ）をとる部分を足したもの。
毎コマ、時刻・距離・ずれ・angle を wall_log.csv に書き出す。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

TARGET = 50.0     # 右の壁から保ちたい距離（cm）
SPEED = 0.3       # 走る速さ（一定）
KP = 0.02         # 比例ゲイン：50 cm ずれたら、ハンドルをいっぱいに切る
MAX_WALL = 300.0  # これより遠いときは「壁なし」とみなす

distance = None   # 右の壁までの距離（update_slow で表示する）
angle = 0.0
t = 0.0           # 走り始めてからの時間（秒）
log_file = None   # 記録を書き出すファイル


def right_wall_distance(scan):
    """右の壁までの距離（cm）。壁が見つからなければ None（6-6）"""
    closest_angle, closest = rc_utils.get_lidar_closest_point(scan, (45, 135))
    if closest > MAX_WALL:
        return None
    center = round(closest_angle * len(scan) / 360)
    near = []
    for d in scan[center - 10 : center + 11]:
        if 0 < d < closest + 5:
            near.append(d)
    return sum(near) / len(near)


def start():
    global t, log_file
    rc.drive.stop()
    t = 0.0
    log_file = open("wall_log.csv", "w", buffering=1)   # buffering=1：1行ごとにすぐ書きこむ
    log_file.write("time,distance,error,angle\n")      # 1行め：列の名前
    print(f">> 右の壁から {TARGET:.0f} cm を保って走ります（P 制御、KP = {KP}）。記録は wall_log.csv")


def update():
    global distance, angle, t

    scan = rc.lidar.get_samples()
    distance = right_wall_distance(scan)

    if distance is None:
        angle = 0.0                                     # 壁が見えないときは、まっすぐ
    else:
        error = distance - TARGET                       # ＋：壁から遠すぎる、－：近すぎる
        angle = rc_utils.clamp(KP * error, -1.0, 1.0)   # ずれに比例してハンドルを切る

    rc.drive.set_speed_angle(SPEED, angle)

    # 記録：壁が見えているコマだけ、1行ずつ書く
    t += rc.get_delta_time()
    if distance is not None:
        log_file.write(f"{t:.3f},{distance:.2f},{distance - TARGET:.2f},{angle:.3f}\n")


def update_slow():
    if distance is None:
        print("壁が見えない")
    else:
        print(f"右の壁まで {distance:5.1f} cm　ずれ {distance - TARGET:+5.1f} cm　angle {angle:+.2f}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```
:::

- `open("wall_log.csv", "w", buffering=1)`：書きこみ用（`"w"`）にファイルを開きます。同じ名前のファイルがあれば、中身は消えて、新しく書き直されます。`buffering=1` にすると、1行書くたびに、すぐファイルに書きこまれます。プログラムを Ctrl＋C で止めても、それまでの記録が残ります
- `f"{t:.3f},{distance:.2f},..."`：値をカンマで区切って1行にします。これが **CSV** の形です

できた `wall_log.csv` の中身は、次のようになります（説明用の簡単なモデルで走らせたもの）。

```text
time,distance,error,angle
0.017,70.11,20.11,0.402
0.033,70.11,20.11,0.402
0.050,70.63,20.63,0.413
```

### グラフにする

記録をグラフにするプログラムです。これは `racecar sim` ではなく、ふつうの Python で動かします。インストーラで入れた環境には、グラフをかく **matplotlib** が入っています。

```python:plot_log.py
"""
plot_log.py
wall_log.csv を読んで、ずれと angle の変わり方をグラフにする。
wall_follow_p_log.py で走らせたあとに、ふつうの Python で実行する（racecar sim は使わない）。
"""

import csv
import matplotlib.pyplot as plt

times, errors, angles = [], [], []
with open("wall_log.csv") as f:
    for row in csv.DictReader(f):          # 1行めの列の名前を使って読む
        times.append(float(row["time"]))
        errors.append(float(row["error"]))
        angles.append(float(row["angle"]))

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 5))
ax1.plot(times, errors)
ax1.axhline(0, color="gray", linestyle="--")
ax1.set_ylabel("error [cm]")
ax1.grid(True)
ax2.plot(times, angles, color="tab:orange")
ax2.axhline(0, color="gray", linestyle="--")
ax2.set_ylabel("angle")
ax2.set_xlabel("time [s]")
ax2.grid(True)
fig.tight_layout()
fig.savefig("wall_log.png")                # 画像にも保存する
plt.show()
```

手順は次のとおりです。

1. `racecar sim wall_follow_p_log.py` で走らせる。しばらく走ったら、シミュレータで Esc を押し、ターミナルで Ctrl＋C を押して止める（1-2）
2. 同じフォルダで `python3 plot_log.py` を実行する

`csv.DictReader` は、CSV の1行めを列の名前として使い、2行めからを `row["time"]` のように名前で取り出せるようにしてくれます。取り出した値は文字なので、`float()` で数に直しています。

### 記録から見えること

![plot_log.py でかいたグラフ。横は時間（0〜15 秒）。上はずれ（error）、下は angle。ずれは +20 cm から始まり、2.5 秒ごろに 0 をこえて、4.7 秒ごろに −24 cm、9.6 秒ごろに +28 cm、14.2 秒ごろに −33 cm と、行ったり来たりしながら、だんだん大きく揺れている。angle も、ずれと同じ形で、+0.4 から −0.65 まで揺れている。どちらの線も、なめらかではなく、小さな階段のような形をしている](/images/racecar-neo-jp/6-8/fig1-log.png)
*図1　plot_log.py でかいた記録（KP 0.02、speed 0.3。説明用の簡単なモデルで走らせたもの）*

図1から、次のことが読みとれます。

- **揺れは、だんだん大きくなる**：ずれの山と谷は、−24 cm（4.7秒）、+28 cm（9.6秒）、−33 cm（14.2秒）と、だんだん大きくなっている。1往復にかかる時間は、約 9 秒
- **angle は、ずれと同じ形**：P 制御では、angle はずれに KP をかけただけなので、同じ形になる
- **線が階段のようになっている**：LIDAR が1秒に6回転しながら測るので、右側の値は、1秒に 10 回くらいしか変わらない（6-6）。その間、プログラムは同じ値を使い続けている

### なぜ行き過ぎるのか：ずれが 0 でも、車はななめを向いている

![左は、P 制御で走った道すじ。横は進んだ距離、たては右の壁までの距離。道すじが目標の 50 cm の線をよこぎる3か所に、そのときの車の向きが青い矢印でかいてある。1回めは壁のほうへ 19°、2回めは壁から離れる向きに 22°、3回めは壁のほうへ 26° ななめを向いていて、どれも、そのまま目標の線を通りすぎていく。右は、ずれの変わり方を、3つの場合でくらべたグラフ。遅れがないとき（緑）は、ずれが +20 cm と −20 cm の間を、同じ大きさで行ったり来たりし続ける。ハンドルの遅れだけのとき（青）は、揺れが少しずつ大きくなる。ハンドルの遅れに加えて LIDAR の遅れとノイズもあるとき（オレンジ）は、揺れがもっと早く大きくなり、20 秒ごろには 38 cm まで広がる](/images/racecar-neo-jp/6-8/fig2-why.png)
*図2　P 制御だけでは揺れが止まらない理由（説明用の簡単なモデル。左の図は、たての目もりを広げているので、矢印が実際より急に見える）*

図2の左は、車が目標の線（50 cm）をよこぎった瞬間の、車の向きです。ずれが 0 になったとき、P 制御の angle も 0 になり、ハンドルはまっすぐにもどります。ところが、そのとき車は、壁に対して **20° 前後ななめ**を向いています。ハンドルをまっすぐにしても、車はその向きのまま進むので、目標の線を通りすぎてしまいます。

通りすぎると、ずれの符号が反対になり、ハンドルも反対に切られます。でも、車の向きがもどるまでには時間がかかり、その間にさらに行き過ぎます。これをくり返すので、揺れが止まりません。

これは、ばねにつるしたおもりに似ています。ばねは、おもりを真ん中に引きもどそうとします（P 制御のはたらき）。でも、真ん中に来たとき、おもりは速さをもっているので、通りすぎます。何かで動きにブレーキをかけないかぎり、おもりはいつまでも上下し続けます。

### 遅れがあると、揺れは大きくなる

図2の右は、説明用の簡単なモデルで、「遅れ」の条件を変えて走らせたものです。

| 条件 | 揺れの大きさ（最初の5秒 → 15〜20秒） |
|---|---|
| 遅れなし（LIDAR もハンドルも、すぐに反応する） | 20 cm → 20 cm（同じ大きさで続く） |
| ハンドルの遅れだけ | 22 cm → 26 cm |
| ハンドルの遅れ ＋ LIDAR の遅れとノイズ | 24 cm → 38 cm |

遅れがまったくなくても、揺れは同じ大きさで続き、止まりません。そこに遅れが加わると、揺れはだんだん大きくなります。

実際の車にも、シミュレータにも、遅れがあります。

- **ハンドルの遅れ**：angle を送っても、ハンドルがその角度まで回るには、少し時間がかかる
- **LIDAR の遅れ**：シミュレータの LIDAR は1秒に6回転するので、使っている値は、最大で 1/6 秒ほど前のもの
- **やりとりの遅れ**：プログラムとシミュレータ（または車）の間で、値をやりとりする時間

遅れがあると、ハンドルを切るのも、もどすのも、少しずつ遅くなります。ブランコをこぐとき、ちょうどよいタイミングで押すと、揺れがどんどん大きくなるのと同じように、遅れて切るハンドルは、揺れを大きくする向きにはたらいてしまいます。速く走るほど、同じ遅れの間に車が進む距離が長くなるので、影響は大きくなります（6-7）。

### 足りないのは「どちらに、どれくらいの速さで近づいているか」

P 制御は、今の**ずれ**しか見ていません。「目標まで 5 cm」でも、ゆっくり近づいているのか、勢いよく近づいているのかは区別しません。揺れを止めるには、目標に勢いよく近づいているときは、早めにハンドルをもどす、という**ブレーキ**が必要です。

- 6-9 では、**ずれが変わる速さ**を計算して、ブレーキに使います（D 制御）
- 6-10 では、**壁に対する車の向き**を LIDAR で直接測って、ブレーキに使います

## ④ 数式・コード

### 揺れの大きくなり方を数で表す

図1のずれの山と谷の大きさは、24 → 28 → 33 cm でした。半往復ごとに、およそ $28 \div 24 \approx 1.17$ 倍、$33 \div 28 \approx 1.18$ 倍になっています。このまま同じ割合で大きくなると、あと数回の半往復で、壁（ずれ −50 cm）に届いてしまいます。

### pandas で読む書き方

インストーラで入れた環境には、表のデータをあつかう **pandas** も入っています。pandas を使うと、CSV を読む部分を1行で書けます。

```python
import pandas as pd
log = pd.read_csv("wall_log.csv")
print(log["error"].abs().max())      # ずれのいちばん大きい値
```

## ⑤ つまずきポイント

### グラフの日本語が「□」になる

matplotlib は、はじめのままでは日本語の文字をもっていないことがあり、ラベルが「□」になります。この本の `plot_log.py` では、ラベルを英語にしています。

### ウィンドウが開かない

WSL などで、グラフのウィンドウが開かないことがあります。`plot_log.py` は、`wall_log.png` という画像にも保存しているので、その画像を開いて見ましょう。

### `wall_log.csv` が見つからない

`plot_log.py` は、実行したフォルダの中の `wall_log.csv` を読みます。`wall_follow_p_log.py` を動かしたのと同じフォルダで実行しましょう。

### 走らせ直すと、前の記録が消える

`start()` のたびに、`"w"` でファイルを開き直すので、前の記録は消えます。残したい記録は、ファイル名を変えてとっておきましょう。

## ⑥ 確認問題

**問1**　`wall_log.csv` の2行めが `0.017,70.11,20.11,0.402` でした。このときの KP はいくつだと考えられますか。

:::details 答え
angle ÷ ずれ ＝ $0.402 \div 20.11 \approx 0.02$ なので、KP は 0.02 です。
:::

**問2**　遅れがまったくなければ、P 制御の壁沿い走行の揺れは止まりますか。

:::details 答え
止まりません。図2の緑のように、同じ大きさで揺れ続けます。ずれが 0 のときに車がななめを向いていて、行き過ぎるからです。
:::

**問3**　揺れを止めるために、ずれのほかに、どんな情報があればよいですか。

:::details 答え
目標にどちら向きに、どれくらいの速さで近づいているか（ずれの変わる速さ、または壁に対する車の向き）です。
:::

## ⑦ 原典

この回は、この本で加えた解説です。

- シミュレータの LIDAR（1秒に6回転）：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `Lidar.cs`
- インストーラが入れるライブラリ（matplotlib 3.8.4、pandas 2.0.3 など）と、ターミナルで自動で使われる環境：[racecar-neo-installer](https://github.com/MITRacecarNeo/racecar-neo-installer) の `requirements.txt`・`setup.sh`
- `csv.DictReader`：Python の標準ライブラリ [csv](https://docs.python.org/ja/3/library/csv.html)

図1・図2は、この本で作った説明用の簡単なモデル（上から見た2次元の車と壁、LIDAR の計算）によるものです。図1は、モデルで `wall_follow_p_log.py` と同じ計算をして作った `wall_log.csv` を、`plot_log.py` でかいたものです。
