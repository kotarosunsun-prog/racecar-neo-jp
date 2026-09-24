---
title: "5-2 色で信号を見分ける（Lab E）"
free: true
---

この回の課題は、オンライン事前コースの **Lab E**「信号チャレンジ（Stoplight Challenge）」です。交差点の信号の役をする色つきの箱を、カメラで見分けます。色に合わせて、右に曲がる・左に曲がる・まっすぐ進む・止まる、を車が自分で選びます。人はボタンを押しません。この本ではじめての、**車が自分で見て決める**プログラムです。

## ① この回でできるようになること

1. 色の範囲から「色のかたまり（輪郭）」を見つけ、いちばん大きいものの中心と面積を求められる
2. 面積を使って、物にどれくらい近づいたかを判断できる
3. 見えたものに合わせて、命令の列（第4章）に動きを1回だけ加えられる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Contour | 輪郭（りんかく） | マスクの白いかたまりの、ふちを1周した線 |
| Area | 面積 | かたまりの大きさ。中に入っている画素の数で表す |
| Center | 中心 | かたまりの真ん中の位置 (行, 列) |
| Stoplight | 信号 | この課題では、色で進み方を指示する箱 |
| Intersection | 交差点 | 道が交わるところ |
| Flag | フラグ | 「もう〇〇した」かどうかを覚えておく True / False の変数 |

## ③ 本文

### 色のかたまりを見つける：輪郭

5-1 で、色の範囲を決めてマスクを作りました。マスクの中の白いかたまりの1つ1つを、ふちに沿って囲んだ線を**輪郭**といいます。`racecar_utils`（`rc_utils` という名前で読みこみます）には、輪郭を扱う関数がそろっています。

| 関数 | はたらき |
|---|---|
| `rc_utils.find_contours(image, 下限, 上限)` | 画像を HSV に変え、範囲に入る画素のかたまりの輪郭を、すべてリストで返す |
| `rc_utils.get_largest_contour(contours, min_area)` | いちばん大きい輪郭を返す。`min_area` より小さければ `None` |
| `rc_utils.get_contour_center(contour)` | 輪郭の中心 (行, 列) を返す |
| `rc_utils.get_contour_area(contour)` | 輪郭の面積（画素の数）を返す |

![説明用の画像に、青の範囲で見つけた輪郭を描いたもの。手前の大きい青い箱は緑の線で囲まれ、中心は (232, 191)、面積は 34200 で、いちばん大きい。奥の小さい青い箱は黄色の線で囲まれ、中心は (208, 498)、面積は 2646。空中の小さな青い点は、面積が小さいので無視されている](/images/racecar-neo-jp/5-2/fig1-contours.png)
*図1　青の範囲で見つけた輪郭と、その中心・面積（説明用に作った画像）*

- 画像の中に同じ色の物がいくつあっても、`get_largest_contour()` はいちばん大きいものを1つだけ選びます。近い物ほど大きく写るので、ふつうは**いちばん近い物**が選ばれます
- 空中の小さな点のような、とても小さなかたまりは、`min_area` で無視できます。カメラの画像には、こうした小さなかたまり（ノイズ）がよく混ざります
- 何も見つからないと `None` が返ります。`None` のまま `get_contour_center()` に渡すとエラーになるので、先に確かめます

次のプログラムは、いちばん大きい青いかたまりを見つけて、輪郭と中心を画面に描きます。B ボタンを押している間、中心と面積を表示します。Lab E のひな形と同じ変数名にしてあります。

```python:find_blue.py
"""
find_blue.py
いちばん大きい青いかたまりを見つけて、輪郭と中心を画面に描く。
B ボタン（キーボードの 2）を押している間、中心と面積を表示する。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

BLUE = ((90, 50, 50), (120, 255, 255))   # 青の HSV の範囲（Lab E のひな形より）
MIN_CONTOUR_AREA = 30                      # これより小さいかたまりは無視する

contour_center = None   # いちばん大きい青の中心 (行, 列)
contour_area = 0        # その面積（画素の数）


def update_contour():
    global contour_center, contour_area

    image = rc.camera.get_color_image()
    if image is None:
        contour_center = None
        contour_area = 0
        return

    contours = rc_utils.find_contours(image, BLUE[0], BLUE[1])
    contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

    if contour is None:          # 青が見つからなかった
        contour_center = None
        contour_area = 0
    else:
        contour_center = rc_utils.get_contour_center(contour)
        contour_area = rc_utils.get_contour_area(contour)
        rc_utils.draw_contour(image, contour)              # 輪郭を緑で描く
        rc_utils.draw_circle(image, contour_center)        # 中心に点を描く

    rc.display.show_color_image(image)


def start():
    rc.drive.stop()
    print(">> B ボタン（キーボードの 2）を押している間、青の中心と面積を表示します")


def update():
    update_contour()

    if rc.controller.is_down(rc.controller.Button.B):
        if contour_center is None:
            print("No contour found")
        else:
            print("Center:", contour_center, "Area:", contour_area)


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
```

図1の画像を見せたときの表示は、次のとおりです。画面から青がなくなると `No contour found` に変わります。

```text
Center: (232, 191) Area: 34200.0
```

### 中心と面積から、何がわかるか

- **中心の列**からは、物が左右どちらにあるかがわかります。列が 320（画面の真ん中）より小さければ左、大きければ右です
- **面積**からは、物にどれくらい近いかがわかります。近づくほど、大きく写るからです

![箱までの距離と、画像の中の面積の関係を表したグラフ。距離が近いほど面積は急に大きくなる。1メートルで約8671、2メートルで約2168と、距離が2倍になると面積は4分の1になる。緑の点線は、たとえば「面積がこれをこえたら交差点に着いた」とするしきい値](/images/racecar-neo-jp/5-2/fig2-area-distance.png)
*図2　距離と面積の関係（20 cm の箱を、横の視野が 69° のカメラで見たとして計算した、説明用のグラフ）*

面積は距離の2乗に反比例します（④）。「面積があるしきい値をこえたら、交差点に着いた」と判断すれば、距離を直接測らなくても、動き出すタイミングを決められます。

### Lab E をやってみよう

課題のファイルは、labs フォルダの中の `lab_e/lab_e.py` です。課題のゴールは次のとおりです（原典の Expected Outcome より）。

| 信号の色 | 車の動き |
|---|---|
| 青（BLUE） | 交差点で右に曲がる |
| だいだい（ORANGE） | 交差点で左に曲がる |
| 緑（GREEN） | まっすぐ進む |
| 赤（RED） | 止まる |
| それ以外の色 | 止まる |

シミュレータのレベルは、**Neo Labs** の **Lab E: Stoplight Challenge** です。探索モードでは、信号の箱をクリックして選び、右クリックするたびに色が変わります。自動採点モードでは、次の7つのコースを順番に走ります。どのコースも、ゴールの範囲の中で止まり、1秒じっとしていると完了です。

| 順番 | コース | 内容 | 制限時間 |
|---|---|---|---|
| 1 | Turn Right | 交差点で右に曲がって止まる | 15秒 |
| 2 | Turn Left | 交差点で左に曲がって止まる | 15秒 |
| 3 | Go Straight | 交差点をまっすぐ抜けて止まる | 15秒 |
| 4 | Two Intersections | 交差点2つのコース | 30秒 |
| 5 | Three Intersections | 交差点3つのコース | 30秒 |
| 6 | Full Course | コース全体 | 30秒 |
| 7 | Challenge: The City | 街の中を進む | 60秒 |

:::message alert
**訳注：ひな形の食い違いと、そのままでは動かないところ**
原典のひな形には、次の食い違いがあります。どれも、1-3〜第4章で学んだことで直せます。

1. 説明文のレベル名は「Lab 3: Stoplight Challenge」ですが、今のシミュレータでは **Lab E: Stoplight Challenge** です。開始時に表示される文字も「Lab 3」のままです
2. `update()` の if・elif の中身がコメントだけなので、このままでは `IndentationError: expected an indented block` で、プログラムが始まりません。中身を書きこむまでは、仮に `pass` と書いておきます
3. 最後の行の `rc.set_start_update(start, update, update_slow)` にある `update_slow` が、どこにも作られていません。このままだと `NameError: name 'update_slow' is not defined` で止まります。`update_slow()` を自分で作るか、`rc.set_start_update(start, update)` にします
4. `update()` の最後の `rc.drive.set_speed_angle(speed, angle)` の前に、`speed` と `angle` の値を決めておく必要があります。決めずに実行すると `NameError: name 'speed' is not defined` で止まります。4-1 の訳注と同じく、`speed = 0`、`angle = 0` から始めます
5. ヒントの「Lab 2」は、この本の **Lab D**（4-1）のことです
6. `goStraight()` のコメントが「左に曲がる命令」になっていますが、正しくは「まっすぐ進む命令」です
7. 「TODO Part 2」と「TODO Part 3」が、`update_contour()` と `update()` の両方に出てきます。下の説明では、`update_contour()` のほうを「見る」、`update()` のほうを「決める・動く」と呼び分けます
:::

#### 見る：信号の色を見分ける（Part 1〜3 の前半）

:::message
Lab E は自動採点つきの課題なので、この本では、色の範囲や曲がる時間など、答えになる数値は載せません。考え方と、別の例を示します。
:::

1. **Part 1：色の範囲を決める**。青の範囲はひな形に書いてあります。ほかの色（緑・赤・だいだい・黄・紫）は、5-1 の `hsv_probe.py` で信号の箱の色を測って決めます。赤は H が 0 と 179 をまたぐことに注意しましょう（5-1 の⑤）
2. **1つの色で、いちばん大きいかたまりを見つける**。上の `find_blue.py` の `update_contour()` と同じです。`MIN_CONTOUR_AREA` の値も決めます
3. **すべての色で同じことをして、いちばん面積の大きい色を選ぶ**。色の範囲と名前を組にしたリストを作り、`for` で1つずつ調べます。面積がそれまでの最大より大きければ、その色の名前と中心・面積を覚えておきます。選んだ色の名前を `stoplight_color` に入れます

#### 決める：いつ、何回、命令を加えるか（Part 2・3 の後半）

原典には、考えておくべきこと（Considerations）として、次の3つの問いがあります。

- **信号が2つ見えたら、どうする？**（今の交差点の信号と、その先の交差点の信号）
- **命令を加える条件は何にする？** 信号の位置か、面積か、その両方か
- **命令を加える関数は、何回呼ぶ？** 1回か、2回か、1秒に60回か

3つめは、とくに大事です。`update()` は1秒に約60回動くので、「信号が見えたら命令を加える」とだけ書くと、見えている間じゅう、毎コマ命令が加わります。1秒で約60個の命令がたまり、車は同じ動きを延々とくり返してしまいます。命令を加えるのは、**1回だけ**にする工夫が必要です。

次のプログラムは、Lab E とは別の例です。ゆっくり前に進み、青い箱に近づいたら（面積がしきい値をこえたら）、1秒だけ下がってから止まります。**面積のしきい値**で「近づいた」を判断し、**フラグ**で「1回だけ」を実現しています。

```python:approach_stop.py
"""
approach_stop.py
ゆっくり前に進み、青い箱に近づいたら（面積が大きくなったら）、
1秒だけ下がってから止まる。反応するのは1回だけ。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

BLUE = ((90, 50, 50), (120, 255, 255))   # 青の HSV の範囲
MIN_CONTOUR_AREA = 30                      # これより小さいかたまりは無視する
SPEED = 0.3                                # 近づくときの速さ
NEAR_AREA = 15000                          # この面積をこえたら「近づいた」とする（調整する）

queue = []       # 命令の列（第4章と同じ）
reacted = False  # もう反応したかどうか


def get_blue_area():
    """いちばん大きい青いかたまりの面積を返す。見つからなければ 0"""
    image = rc.camera.get_color_image()
    if image is None:
        return 0
    contours = rc_utils.find_contours(image, BLUE[0], BLUE[1])
    contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)
    if contour is None:
        return 0
    return rc_utils.get_contour_area(contour)


def start():
    global reacted
    rc.drive.stop()
    queue.clear()
    reacted = False
    print(">> 青い箱に近づいたら、1秒下がって止まります")


def update():
    global reacted

    area = get_blue_area()

    # 近づいたら、1回だけ命令を加える
    if not reacted and area > NEAR_AREA:
        queue.append([1.0, -0.3, 0.0])   # 1秒、後ろに下がる
        reacted = True
        print(f"近づいた（面積 {area:.0f}）")

    # 反応する前は前に進み、反応したあとは止まる
    if reacted:
        speed = 0.0
    else:
        speed = SPEED
    angle = 0.0

    # 命令があれば、そちらを優先する（第4章と同じ）
    if len(queue) > 0:
        speed = queue[0][1]
        angle = queue[0][2]
        queue[0][0] -= rc.get_delta_time()
        if queue[0][0] <= 0:
            queue.pop(0)
            print("命令を実行し終えた")

    rc.drive.set_speed_angle(speed, angle)


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
```

`reacted` が `False` の間だけ命令を加え、加えたらすぐ `True` にします。こうすると、箱が見え続けていても、命令は1つしか加わりません。

Lab E では、交差点が2つ、3つと続きます。1回反応したら二度と反応しないフラグでは、2つめの交差点に対応できません。「命令の列が空のときだけ、次の信号を探す」のように、**いつ次の判断を受けつけるか**を考えてみましょう。

#### 動く：命令を実行して曲がる（Part 3〜6）

- **Part 3（`update()` のほう）**：命令の列を実行する部分です。4-1 の Part 1 と同じしくみで、`speed = 0`、`angle = 0` を先に決めておくことも忘れずに
- **Part 4〜6**：`turnRight()`・`turnLeft()`・`goStraight()` に、第4章と同じように `queue.append([時間, speed, angle])` で命令を並べます。時間は、実際に走らせて合わせます
- `stopNow()` は、命令の列を空にして止まる関数で、すでに完成しています

## ④ 数式・コード

### 面積と距離の関係

カメラに写る物の幅（画素の数）は、物までの距離 $d$ に反比例します。物の実際の幅を $W$、カメラで決まる数を $f$（焦点距離を画素で表したもの）とすると、次のようになります。

$$
\text{写った幅} = \frac{f \, W}{d}
$$

面積は「幅 × 高さ」なので、距離の**2乗**に反比例します。

$$
\text{面積} \approx \left( \frac{f \, W}{d} \right)^2
$$

距離が2倍になると、面積は $\frac{1}{4}$ になります。逆に、面積がわかれば、距離の目安を計算できます。

$$
d \approx \frac{f \, W}{\sqrt{\text{面積}}}
$$

図2は、横の視野が 69° のカメラ（$f \approx 466$ 画素）で、20 cm の箱を見たとして計算したものです。1 m で約 8,671、2 m で約 2,168 になります。箱の向きや、どこまでが1つのかたまりとして写るかでも面積は変わるので、あくまで目安です。

### 中心の求め方

`get_contour_center()` は、輪郭の中にある画素の、行の番号の平均と、列の番号の平均を求めています。紙を切りぬいた形の「つりあう点（重心）」と同じ考え方です。中にある画素の数を $n$、それぞれの行を $r_i$、列を $c_i$ とすると、次のようになります。

$$
\text{中心} = \left( \frac{1}{n}\sum_{i=1}^{n} r_i ,\ \frac{1}{n}\sum_{i=1}^{n} c_i \right)
$$

## ⑤ つまずきポイント

### 命令が何十個もたまって、同じ動きをくり返す

見えている間、毎コマ命令を加えています。フラグや、「命令の列が空のときだけ」という条件で、1回だけ加えるようにしましょう。ためしにフラグを外して同じ箱を見せ続けると、1秒後には命令が 60 個たまっていました。

### 遠くの信号に反応してしまう

面積のしきい値を大きくして、十分近づいてから反応するようにします。画像の上のほうを使わないように、`rc_utils.crop()` で画像を切りとってから探す方法もあります。

### 小さな色のかたまりを、信号とまちがえる

`MIN_CONTOUR_AREA` を大きくします。ただし、大きくしすぎると、遠くの信号が見えなくなります。

### `cv2.error: ... (-215:Assertion failed) npoints >= 0 ...` で止まる

`get_largest_contour()` が `None` を返したのに、そのまま `get_contour_area()` に渡すと、このエラーになります。`get_contour_center()` に `None` を渡した場合はエラーにならず `None` が返り、あとで `center[1]` のように使ったところで `TypeError: 'NoneType' object is not subscriptable` になります。どちらも、`if contour is not None:` の中で使えば防げます。

### `AssertionError: The hue of hsv_lower ...` で止まる

`find_contours()` に渡した範囲がおかしいときのエラーです。H は 0〜179、S と V は 0〜255 の範囲で書きます。また、S と V は下限が上限以下でなければなりません（H だけは、下限が上限より大きくてもかまいません）。

## ⑥ 確認問題

**問1**　`rc_utils.get_largest_contour(contours, 30)` が `None` を返すのは、どんなときですか。2つ答えましょう。

:::details 答え
(1) `contours` が空のとき（その色のかたまりが1つもない）。
(2) いちばん大きいかたまりでも、面積が 30 より小さいとき。
:::

**問2**　2 m 先にある信号の面積が 2,000 でした。1 m まで近づくと、面積はおよそいくつになりますか。

:::details 答え
距離が $\frac{1}{2}$ になると、面積は $2^2 = 4$ 倍になるので、およそ 8,000 です。
:::

**問3**　いちばん大きい青いかたまりの中心が `(250, 100)` でした。信号は画面の左右どちらにありますか。画面の横は 640 画素です。

:::details 答え
中心の列が 100 で、真ん中の 320 より小さいので、画面の左側にあります。中心は (行, 列) の順なので、2つめの数を見ます。
:::

**問4**　`approach_stop.py` から `reacted` を使うのをやめて、`if area > NEAR_AREA:` だけにすると、どうなりますか。

:::details 答え
箱が見えている間、毎コマ命令が加わります。1秒で約60個の「1秒下がる」がたまるので、車は長い間下がり続けます。しかも、下がって箱が小さく見えるまでは、さらに命令が増え続けます。
:::

## ⑦ 原典

- **Lab E - Stoplight Challenge**（`labs/lab_e/lab_e.py`）：[racecar-neo-prereq-labs](https://github.com/MITRacecarNeo/racecar-neo-prereq-labs)（MIT License。ライセンスの全文は 1-3 の最後に載せています）
- 輪郭の関数（`find_contours`・`get_largest_contour`・`get_contour_center`・`get_contour_area`・`draw_contour`）：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）
- Lab E のレベル（コース、制限時間、ゴールで1秒止まる判定、箱の色の変え方）：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `LevelCollection.cs`・`DestinationStop.cs`

ひな形のエラーは、Python 3.9 で実行して確かめました。`find_blue.py` と `approach_stop.py` は、作った画像を1コマずつ渡すプログラムで確かめたものです。図2は、カメラの簡単な計算モデルによる説明用のグラフです。
