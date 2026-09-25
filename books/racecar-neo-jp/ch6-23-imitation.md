---
title: "6-23 人の運転をまねる"
free: true
---

ここまでは、「ずれに合わせてハンドルを切る」というルールを、人が考えてプログラムに書いてきました。この回では、5-6 で学んだ「ルールを人が書くかわりに、データから見つけさせる」考え方を、運転そのものに使います。**人がコントローラーで運転した記録**から、「この見え方なら、このくらいハンドルを切る」をニューラルネットワークに学ばせ、そのネットワークに運転させます。

## ① この回でできるようになること

1. 人の運転を記録して、学習用のデータを作れる
2. 5-10 のニューラルネットワークで、「見え方 → ハンドルの角度」を学習させられる
3. 学習したネットワークで車を走らせられる
4. 上手な運転だけをまねると失敗する理由と、その直し方を説明できる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Imitation learning | 模倣学習 | 手本の行動をまねるように学習すること |
| Behavior cloning | 行動のコピー | 「この場面では、手本はこうした」の組を集めて、そのまま学ぶ模倣学習 |
| Feature | 特徴 | ネットワークに入れる数。この回では、9つの向きの距離 |
| Distribution shift | 分布のずれ | 学習したときの場面と、実際に使うときの場面がちがってくること |
| DAgger | ダガー | ネットワークに運転させ、そのとき人が「正しい操作」を教えて、データに足していく方法 |

## ③ 本文

### 何を記録し、何を学ばせるか

人が運転しているとき、車の LIDAR の見え方と、人が決めたハンドルの角度を、毎コマいっしょに記録します。

- **入力（特徴）**：LIDAR の 9 つの向き（正面、右ななめ前 30°・60°、真横 90°、右ななめ後ろ 120°、左側も同じ）の距離。100 cm を 1 とする数にします
- **正解**：そのとき人が左スティックで決めたハンドルの角度（−1〜1）

これは、5-7 の「入力と正解の組」そのものです。ちがうのは、正解を人が1つずつ書くのではなく、**運転しながら自然に集まる**ことです。

特徴を作る関数は、記録するときも、走るときも、まったく同じものを使う必要があります。そこで、別のファイルにしておきます。

```python:features.py
"""
features.py
LIDAR のデータから、ニューラルネットワークに入れる9つの数（特徴）を作る（6-23）。
record_drive.py と drive_net.py の両方で、この同じ関数を使う。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_utils as rc_utils

ANGLES = (0, 30, 60, 90, 120, 240, 270, 300, 330)   # 見る向き（度）。0 が正面、時計回り
FAR = 300.0                                         # これより遠い（または見えない）ときは、この値にする


def lidar_features(scan):
    """9つの向きの距離を、100 cm を 1 とする数にして、リストで返す"""
    features = []
    for a in ANGLES:
        d = rc_utils.get_lidar_average_distance(scan, a, 6)
        if d == 0.0 or d > FAR:
            d = FAR
        features.append(d / 100)
    return features
```

- 見えない（0.0）ときや、300 cm より遠いときは、300 cm にそろえます。遠すぎる値が入ると、学習がうまく進まないからです

### 人の運転を記録する

```python:record_drive.py
"""
record_drive.py
人がコントローラーで運転しながら、LIDAR の見え方と、そのときのハンドルの角度を記録する（6-23）。
右トリガー：前へ（いっぱいに押すと speed 0.5）　左スティック：ハンドル
B ボタン：それまでの記録を drive_log.csv の最後に書き足す（何回走っても、記録がたまっていく）
features.py を同じフォルダに置いて使う。
"""

import sys

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
from features import lidar_features

rc = racecar_core.create_racecar()

MAX_SPEED = 0.5   # 右トリガーをいっぱいに押したときの speed
rows = []         # 記録：1コマごとに [特徴9つ, ハンドルの角度]


def start():
    rows.clear()
    rc.drive.stop()
    print(">> 右トリガーで前へ、左スティックでハンドル。B ボタンで記録を保存します")


def update():
    speed = rc.controller.get_trigger(rc.controller.Trigger.RIGHT) * MAX_SPEED
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]
    rc.drive.set_speed_angle(speed, angle)

    # 走っているときだけ、見え方と、人が決めたハンドルの角度を記録する
    if speed > 0.4:
        scan = rc.lidar.get_samples()
        rows.append(lidar_features(scan) + [angle])

    if rc.controller.was_pressed(rc.controller.Button.B) and len(rows) > 0:
        with open("drive_log.csv", "a") as f:         # "a"：前の記録の後ろに書き足す
            np.savetxt(f, np.array(rows), delimiter=",", fmt="%.4f")
        print(f"{len(rows)} コマ分を drive_log.csv に書き足しました")
        rows.clear()


def update_slow():
    print(f"記録したコマ数 {len(rows)}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

- 右トリガーをいっぱいに押して走っている間だけ記録します。止まっている間の記録は、運転のお手本になりません
- B ボタンを押すと、それまでの記録を `drive_log.csv` の**最後に書き足し**ます（`open(..., "a")`）。何回走っても、記録がたまっていきます。いらなくなったら、ファイルを消してやり直します
- シミュレータでは、キーボードの A・D キーでもハンドルを切れますが、角度は −1・0・1 の3つだけになります。細かい角度を記録するには、ゲームパッドのスティックを使いましょう

### ネットワークを学習させる

5-10 の `backprop_red.py` と同じ形の、2層のネットワークを使います。ちがうのは、次の3つです。

- 入力が 9 つになった
- かくれ層のニューロンは **tanh** 関数（−1〜1 を出す、シグモイド関数の仲間）で、16 個
- 出力は、ハンドルの角度（−1〜1）なので、シグモイド関数を通さずに、そのままの値を使う

```python:train_drive.py
"""
train_drive.py
drive_log.csv（record_drive.py の記録）から、「見え方 → ハンドルの角度」を答える
ニューラルネットワークを学習させ、重みを drive_net.npz に保存する（6-23）。
かくれ層は tanh のニューロン 16 個、出力は1つ（そのままの値）、損失は平均二乗誤差。
"""

import numpy as np

rng = np.random.default_rng(0)

data = np.loadtxt("drive_log.csv", delimiter=",")
x = data[:, :-1]                  # 見え方（特徴9つ）
y = data[:, -1]                   # そのとき人が決めたハンドルの角度

# 特徴ごとに、平均 0、ばらつき 1 になるようにそろえる（走るときも、同じ平均とばらつきを使う）
x_mean = x.mean(axis=0)
x_std = x.std(axis=0) + 1e-6
x = (x - x_mean) / x_std

# 5コマに1コマを、学習に使わない「確かめ用」にする
test = np.arange(len(x)) % 5 == 0
x_train, y_train = x[~test], y[~test]
x_test, y_test = x[test], y[test]

HIDDEN = 16                       # かくれ層のニューロンの数
LR = 0.1                          # 学習率

W1 = rng.normal(0, 0.5, (x.shape[1], HIDDEN))   # 入力 → かくれ層 の重み
b1 = np.zeros(HIDDEN)                           # かくれ層のバイアス
W2 = rng.normal(0, 0.5, HIDDEN)                 # かくれ層 → 出力 の重み
b2 = 0.0                                        # 出力のバイアス


def predict(x):
    return np.tanh(x @ W1 + b1) @ W2 + b2


for step in range(5001):
    # ---- 前向きの計算 ----
    a1 = np.tanh(x_train @ W1 + b1)       # かくれ層の出力
    out = a1 @ W2 + b2                    # 出力：ハンドルの角度の予想
    loss = np.mean((out - y_train) ** 2)

    # ---- 後ろ向きの計算（5-10）----
    d_out = 2 * (out - y_train) / len(y_train)
    d_W2 = a1.T @ d_out
    d_b2 = d_out.sum()
    d_a1 = np.outer(d_out, W2)
    d_z1 = d_a1 * (1 - a1 ** 2)           # tanh の傾きは 1 - a^2
    d_W1 = x_train.T @ d_z1
    d_b1 = d_z1.sum(axis=0)

    if step in (0, 100, 1000, 5000):
        test_loss = np.mean((predict(x_test) - y_test) ** 2)
        print(f"{step:4d} 回め：学習用の損失 {loss:.4f}　確かめ用の損失 {test_loss:.4f}")

    W1 -= LR * d_W1
    b1 -= LR * d_b1
    W2 -= LR * d_W2
    b2 -= LR * d_b2

np.savez("drive_net.npz", W1=W1, b1=b1, W2=W2, b2=b2, x_mean=x_mean, x_std=x_std)
print(f"{len(x_train)} コマで学習し、drive_net.npz に保存しました")
```

- **特徴をそろえる**：9つの特徴は、正面の距離（3 まで）と真横の距離（0.5 くらい）のように、大きさがばらばらです。そのままでは学習がうまく進まないので、特徴ごとに平均を引いて、ばらつき（標準偏差）で割ります。走るときも、学習のときの平均とばらつきを使うので、いっしょに保存します
- **確かめ用のデータ**：5コマに1コマは学習に使わず、学習したネットワークが、見ていないデータでも正しく答えられるかを確かめます（5-12・5-14 の「検証用」と同じ考え方）

説明用のモデルで、上手な運転を1周記録して学習させると、次のように表示されました。

```text
   0 回め：学習用の損失 2.9570　確かめ用の損失 2.9553
 100 回め：学習用の損失 0.0385　確かめ用の損失 0.0381
1000 回め：学習用の損失 0.0120　確かめ用の損失 0.0129
5000 回め：学習用の損失 0.0081　確かめ用の損失 0.0092
2400 コマで学習し、drive_net.npz に保存しました
```

学習用も確かめ用も、損失が小さくなりました。ネットワークは、記録した場面では、人とほとんど同じ角度を答えられるようになっています。

### 学習したネットワークで走る

```python:drive_net.py
"""
drive_net.py
train_drive.py で学習させたニューラルネットワーク（drive_net.npz）で、ハンドルを決めて走る（6-23）。
LB ボタンを押している間は、人が左スティックで「自分ならこう切る」を示すと、
そのときの見え方といっしょに記録する（ネットワークの運転はそのまま）。B ボタンで drive_log.csv に書き足す。
features.py と drive_net.npz を同じフォルダに置いて使う。
"""

import sys

import numpy as np

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils
from features import lidar_features

rc = racecar_core.create_racecar()

SPEED = 0.5                       # 記録したときと同じ速さで走る
net = np.load("drive_net.npz")
W1, b1, W2, b2 = net["W1"], net["b1"], net["W2"], float(net["b2"])
x_mean, x_std = net["x_mean"], net["x_std"]   # 学習のときと同じように、特徴をそろえる

angle = 0.0
rows = []         # 教えた記録：[特徴9つ, 人が示したハンドルの角度]


def start():
    rc.drive.stop()
    print(">> 学習したネットワークで走ります")


def update():
    global angle
    scan = rc.lidar.get_samples()
    x = (np.array(lidar_features(scan)) - x_mean) / x_std
    out = np.tanh(x @ W1 + b1) @ W2 + b2        # 前向きの計算だけ
    angle = rc_utils.clamp(float(out), -1.0, 1.0)
    rc.drive.set_speed_angle(SPEED, angle)

    # LB を押している間は、人が示した角度を記録する（車を動かすのは、ネットワークのまま）
    if rc.controller.is_down(rc.controller.Button.LB):
        teach = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]
        rows.append(lidar_features(scan) + [teach])
    if rc.controller.was_pressed(rc.controller.Button.B) and len(rows) > 0:
        with open("drive_log.csv", "a") as f:
            np.savetxt(f, np.array(rows), delimiter=",", fmt="%.4f")
        print(f"{len(rows)} コマ分を drive_log.csv に書き足しました")
        rows.clear()


def update_slow():
    print(f"angle {angle:+.2f}　教えたコマ数 {len(rows)}")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

`update()` の中は、前向きの計算（5-9）だけです。LB ボタンと B ボタンの部分は、あとで使います。

:::message
この回の結果は、この本で作った説明用の簡単なモデル（6-18 のコース、speed 0.5）で確かめたものです。モデルの中の「人」は、6-18 の `wall_follow_course.py` です。上手な運転は、そのままの `wall_follow_course.py`、ふらつきのある運転は、それに、なめらかにゆれるでたらめな角度を足したものです。
:::

### 上手な運転だけをまねると、失敗する

上手な運転を1周だけ記録して学習させたネットワークで走らせると、3回とも、広い所で左の壁にぶつかりました（図1の左の灰色）。学習用のデータでは、損失がとても小さかったのに、です。

理由は、**記録には、上手な場面しか入っていない**からです。上手な運転では、車はいつも通路の真ん中近くを走っています。「真ん中から大きくずれてしまったとき、どうもどるか」の場面は、一度も記録されていません。

ネットワークの答えには、少しだけ誤差があります。その誤差で少しずれると、記録にない場面になり、答えの誤差がもっと大きくなり、さらにずれる……をくり返して、ぶつかってしまうのです。学習したときの場面と、実際に走るときの場面がずれていくので、これを**分布のずれ**といいます。

![左は、6-18 のコースを上から見た図に、ネットワークだけで走らせた道すじをかいたもの。上手な運転1周だけで学習したネットワーク（灰色）は、広い所で少しずつ左へずれて、左の壁にぶつかる。教える運転を1回足して学習し直したネットワーク（オレンジ）は、最後まで走ってゴールする。右は、記録した場面の、通路の真ん中からのずれの時間変化。上手な運転の記録（灰色）は、ずっと ±30 cm 以内にある。教える運転の記録（オレンジ）は、30 秒をすぎたところから左へずれていき、真ん中から 140 cm 近くずれた所でぶつかっている。この「左へずれていく場面」は、上手な運転の記録にはない](/images/racecar-neo-jp/6-23/fig1-imitation.png)
*図1　ネットワークだけで走らせた道すじ（左）と、記録した場面の真ん中からのずれ（右）*

### 直し方1：ずれた場面も記録する

1つめの直し方は、わざと少しふらつきながら運転して、**ずれた所からもどる場面**も記録することです。ふらつきのある運転でも、ずれたときには、もどす向きにハンドルを切るので、その場面が記録に入ります。

### 直し方2：ネットワークに運転させて、人が教える（DAgger）

2つめの直し方は、**ネットワークに運転させながら、人が「自分ならこう切る」を示す**ことです。`drive_net.py` では、LB ボタンを押している間、人が左スティックで示した角度を、そのときの見え方といっしょに記録します。車を動かすのはネットワークのままです。

こうすると、ネットワークがずれていく場面（図1の右のオレンジ）で、人が「こうもどす」を教えることになります。ネットワークが実際に出会う場面の記録が集まるので、分布のずれが小さくなります。これを、何回かくり返す方法を **DAgger**（Dataset Aggregation、データを集めて足していく）といいます。

説明用のモデルで、2つの直し方を試しました。どれも、学習したあとで3回ずつ走らせています。

| 記録のしかた | 記録したコマ数 | 3回走らせた結果 |
|---|---|---|
| 上手な運転を1周 | 3000 | 3回とも、広い所でぶつかる |
| ふらつきのある運転を3周 | 6000 | 2回ゴール（45.7 秒・45.6 秒）、1回ぶつかる |
| ふらつきのある運転を5周 | 12000 | 3回ともゴール（45.6 秒） |
| 上手な運転1周 ＋ 教える運転1回 | 5040 | 3回ともゴール（46.3〜46.4 秒） |

教える運転は、1回めのネットワークが広い所でぶつかるまでの約 34 秒分（2040 コマ）だけでしたが、それを足して学習し直すと、3回ともゴールできるようになりました。ふらつきのある運転では、5周分の記録が必要でした。**ネットワークがまちがえる場面のデータ**が、いちばん役に立つのです。

### ルールを書く方法と、まねる方法

| | ルールを書く（6-1〜6-20） | まねる（この回） |
|---|---|---|
| 人がすること | ずれ、ゲイン、状態の切りかえを考えて書く | 運転して記録する |
| うまくいかないとき | どこがおかしいか、式を見て考えられる | どの場面のデータが足りないかを探す |
| 得意なこと | 壁沿いや、止まる位置のように、目標がはっきりしたこと | ルールにしにくい、人のかんのような運転 |

この回のネットワークは、6-18 のプログラムを「まねた」だけなので、手本より上手にはなりません。それでも、人のかんのように、ルールにしにくいものをまねられるのが、この方法の強みです。1989 年には、カメラの画像から人のハンドル操作をまねるネットワーク（ALVINN）が、本物の車で道路を走っています。

## ④ 数式・コード

### tanh 関数と、その傾き

$$
\tanh z = \frac{e^{z} - e^{-z}}{e^{z} + e^{-z}}, \qquad \frac{d}{dz}\tanh z = 1 - \tanh^2 z
$$

シグモイド関数（0〜1）を上下に2倍に広げて、−1〜1 にしたような形です。傾きは、出力 $a = \tanh z$ を使って $1 - a^2$ と書けるので、5-10 の $a(1-a)$ と同じように、前向きの計算の結果を使い回せます。`train_drive.py` の `d_z1 = d_a1 * (1 - a1 ** 2)` がこれです。

### 特徴のそろえ方

特徴 $x_j$ ごとに、学習用のデータの平均 $\mu_j$ と標準偏差 $\sigma_j$ を求めて、

$$
x_j' = \frac{x_j - \mu_j}{\sigma_j}
$$

とします。どの特徴も「平均 0、ばらつき 1」になるので、重みの大きさがそろい、同じ学習率で、すべての重みが同じくらいずつ学べます。`1e-6` を足しているのは、ばらつきが 0 の特徴があったときに、0 で割らないためです。

### なぜ誤差がふくらむのか

1コマあたり、ネットワークが手本とちがう操作をしてしまう割合を $\varepsilon$ とします。手本の場面だけで学習すると、一度まちがえて記録にない場面に入ると、そこからは、まちがえ続けるかもしれません。$T$ コマ走る間の、まちがいの数は、最悪で $T^2 \varepsilon$ くらいまでふくらむことが知られています。DAgger のように、ネットワークが出会う場面でも教えると、$T \varepsilon$ くらいにおさえられます（Ross ほか、2011）。

## ⑤ つまずきポイント

### 学習では損失が小さいのに、走らせるとぶつかる

この回の「分布のずれ」です。記録にない場面に入っていないかを考えましょう。ぶつかる所の手前で、ネットワークに運転させながら、LB ボタンを押して正しい操作を教えます。

### 記録と、走るときの特徴がちがう

特徴の作り方（向き、窓の広さ、遠すぎるときの値、そろえ方）が、記録と走るときで少しでもちがうと、ネットワークは正しく答えられません。`features.py` を2つのプログラムで共有し、平均とばらつきも `drive_net.npz` に保存しているのは、このためです。

### 速さを変えると、うまく走れない

記録したときと同じ速さ（speed 0.5）で走らせましょう。速さがちがうと、同じ見え方でも、必要なハンドルの角度が変わります（6-19）。

### 下手な運転もまねる

ネットワークは、よい運転も悪い運転も区別せずにまねます。壁にこすった記録や、まちがえて逆に切った記録は、`drive_log.csv` から消してから学習させましょう。

## ⑥ 確認問題

**問1**　学習用のデータの損失も、確かめ用のデータの損失も小さいのに、走らせるとぶつかりました。確かめ用のデータで、この失敗を見つけられないのはなぜですか。

:::details 答え
確かめ用のデータも、同じ上手な運転の記録から取り出したものだからです。どちらにも「真ん中から大きくずれた場面」は入っていません。ネットワークが自分で運転して、ずれた場面に入ったときに、はじめて失敗がわかります。
:::

**問2**　ある特徴の、学習用のデータの平均が 1.2、標準偏差が 0.4 でした。走っているときに、この特徴が 2.0 だったら、ネットワークに入れる値はいくつですか。

:::details 答え
$(2.0 - 1.2) \div 0.4 = 2.0$ です。
:::

**問3**　DAgger で、ネットワークに運転させているのに、人が操作を記録するのはなぜですか。

:::details 答え
ネットワークが実際に出会う場面（ずれていく場面など）で、「正しい操作」を教えるためです。人が運転すると、その場面には入らないので、記録できません。
:::

## ⑦ 原典

- D. A. Pomerleau, "ALVINN: An Autonomous Land Vehicle in a Neural Network," *Advances in Neural Information Processing Systems 1* (1989)
- S. Ross, G. J. Gordon, J. A. Bagnell, "A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning," *Proceedings of AISTATS* (2011)（DAgger と、誤差が $T^2$ でふくらむことの説明）
- シミュレータで、キーボードの A・D キーが左スティックの −1・1 になること：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `Controller.cs`
- `get_lidar_average_distance()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）

図1、表と表示の数字は、この本で作った説明用の簡単なモデルによるものです。
