---
title: "6-3 AR マーカーで進む方向を決める"
free: true
---

5-4 で、AR マーカーの番号・向き・位置を読みとれるようになりました。この回では、それを走りに使います。マーカーの**位置**を使って、比例制御でマーカーのほうへ向かい、マーカーの**大きさ**で近づいたことを知り、マーカーの**番号**で曲がる向きを決めます。道の分かれ目に置かれた標識を見て、進む道を選ぶイメージです。

:::message
オンライン事前コースの Lab H は、AR マーカーを使う課題ですが、そのひな形は、公開されているリポジトリ（racecar-neo-prereq-labs）には入っていません。そこでこの回は、5-4 のライブラリの関数を使って、この本で作った例で進めます。なお、シミュレータの **Neo Labs** には「Lab H: Cone Slalom」というレベルがありますが、これはコーンの間をぬって走るレベルです。
:::

## ① この回でできるようになること

1. AR マーカーの中心の位置を使って、比例制御でマーカーのほうを向ける
2. マーカーの写った大きさで、近づいたかどうかを判断できる
3. マーカーの番号に合わせて、曲がる向きを変えられる
4. 曲がっている間は新しい判断をしない、という流れを組み立てられる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Landmark | 目印（ランドマーク） | 場所や進み方を知るための、目立つ印 |
| Junction | 分かれ道（T 字路） | 道が2つ以上に分かれるところ |
| Look-up table | 対応表 | 「この番号なら、こうする」を並べた表。Python では辞書で書ける |
| Dictionary | 辞書（Python） | `{キー: 値}` の組を集めたもの。5-4 の「マーカーの辞書」とは別のもの |

## ③ 本文

### 3つの情報を、3つの目的に使う

AR マーカー1つから、次の3つの情報がとれます（5-4）。

| 情報 | 求め方 | 何に使うか |
|---|---|---|
| 中心の列 | 4つの角の列の平均 | マーカーのほうを向く（比例制御） |
| 写った高さ | 4つの角の行の、最大 − 最小 | どれくらい近づいたか（5-2 の面積と同じ考え方） |
| 番号 | `get_id()` | どちらに曲がるか |

### マーカーのほうを向く：比例制御

マーカーの中心の列から、6-2 のライントレースと同じように、ずれを −1〜1 で表します。

$$
\text{error} = \frac{\text{中心の列} - 320}{320}, \qquad \text{angle} = K_P \times \text{error}
$$

マーカーが右にあれば右に、左にあれば左にハンドルを切るので、車はマーカーの正面へと向かっていきます。

### 近づいたら、番号に合わせて曲がる

マーカーは、近づくほど大きく写ります。写った高さがしきい値 `NEAR_HEIGHT` をこえたら、分かれ道に着いたと判断して、曲がる命令を加えます。

どちらに曲がるかは、番号で決めます。この例では、**番号 0 なら左、番号 1 なら右**というきまりにしました。このきまりは、Python の**辞書**で書くと、見やすく、あとから変えやすくなります。

```python
TURN_ANGLE = {0: -1.0, 1: 1.0}   # マーカーの番号 → ハンドルの向き（-1：左、1：右）
turn = TURN_ANGLE[marker.get_id()]
```

`TURN_ANGLE[0]` は −1.0、`TURN_ANGLE[1]` は 1.0 です。`marker.get_id() in TURN_ANGLE` で、その番号がきまりの中にあるかを調べられます。

曲がる動きは、第4章の命令の列で実行します。5-2 で学んだように、命令を加えるのは**1回だけ**にします。この例では、「命令の列が空のときだけマーカーを見る」ことで、曲がっている最中に、また曲がる命令が加わらないようにしています。

### やってみよう：T 字路でマーカーを見て曲がる

```python:ar_turn.py
"""
ar_turn.py
AR マーカーのほうを向きながら近づき、十分に近づいたら、マーカーの番号に合わせて曲がる。
番号 0 なら左、番号 1 なら右（この例で決めたきまり）。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

SPEED = 0.4                 # 走る速さ
KP = 0.8                    # マーカーのほうを向くための比例ゲイン
NEAR_HEIGHT = 60            # マーカーがこの高さ（画素）より大きく写ったら、曲がり始める
TURN_TIME = 2.3             # 曲がり続ける時間（秒）
TURN_ANGLE = {0: -1.0, 1: 1.0}   # マーカーの番号 → ハンドルの向き（-1：左、1：右）

queue = []   # 命令の列（第4章と同じ）


def find_marker():
    """知っている番号のマーカーのうち、いちばん大きく写っているもの（いちばん近いもの）を返す"""
    image = rc.camera.get_color_image()
    if image is None:
        return None
    best = None
    best_height = 0
    for marker in rc_utils.get_ar_markers(image):
        if marker.get_id() not in TURN_ANGLE:
            continue
        corners = marker.get_corners()
        height = corners[:, 0].max() - corners[:, 0].min()
        if height > best_height:
            best, best_height = marker, height
    return best


def start():
    rc.drive.stop()
    queue.clear()
    print(">> AR マーカーに近づき、番号 0 なら左、1 なら右に曲がります")


def update():
    speed = SPEED
    angle = 0.0

    if len(queue) == 0:                          # 曲がっている最中は、マーカーを見ない
        marker = find_marker()
        if marker is not None:
            corners = marker.get_corners()
            center_col = corners[:, 1].mean()                     # マーカーの中心の列
            height = corners[:, 0].max() - corners[:, 0].min()    # 写った高さ（画素）
            error = (center_col - 320) / 320
            angle = rc_utils.clamp(KP * error, -1.0, 1.0)         # マーカーのほうを向く（比例制御）
            if height > NEAR_HEIGHT:                              # 十分に近づいたら、曲がる命令を1回だけ加える
                turn = TURN_ANGLE[marker.get_id()]
                queue.append([TURN_TIME, SPEED, turn])
                print(f"マーカー {marker.get_id()} を見つけた → {'右' if turn > 0 else '左'}に曲がる")

    if len(queue) > 0:
        speed = queue[0][1]
        angle = queue[0][2]
        queue[0][0] -= rc.get_delta_time()
        if queue[0][0] <= 0:
            queue.pop(0)
            print("曲がり終えた")

    rc.drive.set_speed_angle(speed, angle)


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
```

![左は、説明用の簡単なモデルでカメラに写したマーカー。番号 1 のマーカーが、画面の真ん中より少し右（中心の列 402）に、高さ 56 画素で写っている。ずれ ＝ (402 − 320) ÷ 320 ＝ +0.26 なので、マーカーのほうへ右にハンドルを切る。右は、T 字路を上から見た道すじ。車は下からまっすぐ進み、突き当たりの壁の真ん中にマーカーがある。曲がり始めた場所は、分かれ道の入口あたり（縦 450 cm 付近）。番号 1 のときは右の通路へ、番号 0 のときは左の通路へ曲がって進んでいる](/images/racecar-neo-jp/6-3/fig1-ar-turn.png)
*図1　カメラで見たマーカー（左）と、T 字路での道すじ（右）（説明用の簡単なモデル）*

説明用の簡単なモデルで、T 字路の突き当たりに番号 1 のマーカーを置いて走らせると、次のように表示され、右の通路に曲がりました。番号 0 のマーカーにすると、左の通路に曲がりました。

```text
>> AR マーカーに近づき、番号 0 なら左、1 なら右に曲がります
マーカー 1 を見つけた → 右に曲がる
曲がり終えた
```

`NEAR_HEIGHT` と `TURN_TIME` は、このモデルの道の幅と曲がり方に合わせて決めた値です。シミュレータの **AR Marker Sandbox** などで試すときは、マーカーの大きさ・道の幅・速さに合わせて、調整し直しましょう。

### この形は、この先も何度も出てくる

この例のプログラムは、「マーカーを探しながら進む」と「曲がる」の2つの**状態**を、命令の列が空かどうかで切りかえています。状態が3つ、4つと増えると、このやり方では見通しが悪くなります。第7章では、状態をはっきり名前で分けて切りかえる**ステートマシン**を学びます。

## ④ 数式・コード

### マーカーの高さから、距離の目安を求める

5-2 と同じく、写った高さ $h$（画素）は、距離 $d$ に反比例します。マーカーの実際の大きさを $W$、カメラで決まる数を $f$ とすると、

$$
h \approx \frac{f \, W}{d}, \qquad d \approx \frac{f \, W}{h}
$$

図1のモデルでは $f = 466$ 画素、マーカーの黒い部分の大きさは $W = 20$ cm としています。`NEAR_HEIGHT = 60` は、$d \approx 466 \times 20 \div 60 \approx 155$ cm、つまり、マーカーの 1.5 m ほど手前で曲がり始める、という意味になります。

### 番号ごとに、動きをまとめて決める

番号ごとに、曲がる時間や速さも変えたいときは、辞書の値を組にします。

```python
ACTIONS = {
    0: (2.3, 0.4, -1.0),    # 番号 0：2.3 秒、速さ 0.4、左
    1: (2.3, 0.4, 1.0),     # 番号 1：2.3 秒、速さ 0.4、右
    2: (1.0, 0.0, 0.0),     # 番号 2：1 秒止まる
}
turn_time, speed, angle = ACTIONS[marker.get_id()]
queue.append([turn_time, speed, angle])
```

## ⑤ つまずきポイント

### 曲がり終えたあと、同じマーカーでまた曲がってしまう

曲がり終えても、まだマーカーが画面に大きく写っていると、また曲がる命令が加わります。曲がる時間を長くして、マーカーが画面から外れるまで曲がるか、「最後に反応した番号」を覚えておき、同じ番号にはしばらく反応しないようにします。

### 遠くのマーカーを見失う

遠くのマーカーは小さく写るので、読みとれないことがあります（5-4）。見失っている間は、まっすぐ進む（この例のように `angle = 0.0`）か、前の角度を使い続けるかを決めておきます。

### 知らない番号のマーカーで、プログラムが止まる

`TURN_ANGLE[marker.get_id()]` で、辞書にない番号を使うと `KeyError` で止まります。この例の `find_marker()` のように、`in` で辞書にある番号かを先に確かめましょう。

## ⑥ 確認問題

**問1**　マーカーの4つの角の列が 380、460、460、380 でした。`KP = 0.8` のときの `angle` を求めましょう。

:::details 答え
中心の列は $(380 + 460 + 460 + 380) \div 4 = 420$ です。ずれは $(420 - 320) \div 320 = 0.3125$、`angle` は $0.8 \times 0.3125 = 0.25$ です。少し右にハンドルを切ります。
:::

**問2**　`TURN_ANGLE = {0: -1.0, 1: 1.0}` のとき、`TURN_ANGLE[1]` と `3 in TURN_ANGLE` の値はそれぞれ何ですか。

:::details 答え
`TURN_ANGLE[1]` は `1.0`、`3 in TURN_ANGLE` は `False` です。
:::

**問3**　図1のモデルで、マーカーの大きさを 2 倍（40 cm）にしました。同じ場所で曲がり始めるには、`NEAR_HEIGHT` をどう変えればよいですか。

:::details 答え
同じ距離なら、写る高さも 2 倍になるので、`NEAR_HEIGHT` も 2 倍の 120 にします。
:::

## ⑦ 原典

この回は、この本で加えた解説です。

- `get_ar_markers()`・`get_corners()`・`get_id()`・`draw_ar_markers()`・`clamp()`：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）
- シミュレータの Lab H（Cone Slalom）と AR Marker Sandbox：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `LevelCollection.cs`

図1と `ar_turn.py` の表示は、この本で作った説明用の簡単なモデル（上から見た2次元の車と壁、マーカーを写すカメラの計算）によるもので、インストーラが入れる版の OpenCV（4.8.1）でも確かめました。
