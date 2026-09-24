---
title: "5-4 AR マーカーを見つける"
free: true
---

AR マーカーは、白と黒の四角い模様で番号を表した「ロボット用の標識」です。カメラの画像から見つけやすく、番号も読みとれるので、「この先で右に曲がれ」「ここがゴール」のような合図に使えます。この回では、`racecar_utils` の関数を使って、AR マーカーの番号・向き・色・位置を読みとります。第6章の「AR マーカーで進む方向を決める」の土台になります。

## ① この回でできるようになること

1. AR マーカーが、白黒の模様で番号を表していることを説明できる
2. `get_ar_markers()` で、画像の中の AR マーカーを見つけられる
3. 見つけたマーカーの番号・向き・ふちの色・中心の位置を取り出せる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| AR marker | AR マーカー | 白黒の模様で番号を表した四角い印。AR は Augmented Reality（拡張現実）の略 |
| ArUco | ArUco（アルコ） | AR マーカーの種類の1つ。OpenCV で読みとれる |
| ID | ID（番号） | マーカーの模様が表している番号 |
| Dictionary | 辞書 | 使う模様の種類の決まり。6×6 マスの模様が250種類、など |
| Corner | 角 | マーカーの四すみ |
| Orientation | 向き | マーカーの上が、画像の中でどちらを向いているか |

## ③ 本文

### AR マーカーのしくみ

AR マーカーは、黒いふちの中に、白と黒のマスを並べた模様です。模様ごとに番号が決まっていて、OpenCV の ArUco という機能で、画像の中から見つけて番号を読みとれます。

- 模様のマスの数と種類を決めたものを**辞書**といいます。RACECAR のシミュレータでは、**6×6 マスの模様が 250 種類**ある辞書（`DICT_6X6_250`）が使われています
- 実機の授業では、**5×5 マス**の辞書（`DICT_5X5_250`）のマーカーが使われます（⑤）
- 模様は上下左右の区別がつくように作られているので、マーカーが傾いていても、どちらが「上」かがわかります

### マーカーを見つける：get_ar_markers()

```python
markers = rc_utils.get_ar_markers(image)
```

画像の中で見つけたマーカーを、リストで返します。1つも見つからなければ、空のリストです。リストの1つ1つは、次のことを教えてくれます。

| 書き方 | 返すもの |
|---|---|
| `marker.get_id()` | マーカーの番号 |
| `marker.get_corners()` | 4つの角の (行, 列)。模様の左上の角から、時計回りの順 |
| `marker.get_orientation()` | 向き。`UP`・`RIGHT`・`DOWN`・`LEFT` のどれか |
| `marker.get_color()` | ふちの色の名前（色の候補を渡したときだけ） |

![説明用に作った画像で、AR マーカーを2つ見つけたところ。左の大きいマーカーは、ID 1、向き UP、色 blue、中心 (220, 190) で、角の番号は左上から時計回りに 0・1・2・3。右の小さいマーカーは右に90度回っていて、ID 3、向き RIGHT、色 red、中心 (218, 498)。角の0番は右上にあり、そこから時計回りに1・2・3と続く](/images/racecar-neo-jp/5-4/fig1-markers.png)
*図1　`get_ar_markers()` で見つけたマーカー。オレンジの数字は角の順番（説明用に作った画像）*

**向き**は、模様の「上」が画像の中でどちらを向いているかを表します。図1の右のマーカーは、時計回りに 90° 回して置いたので、上が右を向き、`RIGHT` になっています。角の順番も、模様にくっついて回ります。0番の角は、いつも**模様の左上**です。

### ふちの色を調べる

シミュレータの AR マーカーは、色のついたふちで囲まれています。色の候補を渡すと、マーカーのまわりでいちばん多く見つかった色の名前を調べてくれます。

```python
BLUE = ((90, 100, 100), (120, 255, 255), "blue")
RED = ((170, 100, 100), (10, 255, 255), "red")
markers = rc_utils.get_ar_markers(image, [BLUE, RED])
```

色の候補は、「HSV の下限・上限・色の名前」の組です（範囲の決め方は 5-1）。候補を渡さなかったとき、またはどの色も見つからなかったときは、`get_color()` が `"not detected"` を返します。

### マーカーの位置と大きさ

`get_corners()` が返す4つの角は、NumPy の配列です。4つの平均をとると、マーカーの中心になります。

```python
corners = marker.get_corners()
center = corners.mean(axis=0)                           # (行の平均, 列の平均)
height = corners[:, 0].max() - corners[:, 0].min()      # 写った高さ（画素）
```

`corners.mean(axis=0)` は、「4つの行の平均」と「4つの列の平均」をまとめて計算します。`corners[:, 0]` は、4つの角の行だけを取り出したものです。5-2 と同じく、中心の列からマーカーが左右どちらにあるかが、写った大きさから近さの目安がわかります。

### やってみよう：マーカーを読みとる

```python:ar_check.py
"""
ar_check.py
画面の中の AR マーカーを見つけて、枠を描く。
A ボタン（キーボードの 1）を押すと、見つけたマーカーの情報を表示する。
"""

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

rc = racecar_core.create_racecar()

# マーカーのふちの色の候補：(HSV の下限, HSV の上限, 色の名前)
BLUE = ((90, 100, 100), (120, 255, 255), "blue")
RED = ((170, 100, 100), (10, 255, 255), "red")
POTENTIAL_COLORS = [BLUE, RED]


def start():
    rc.drive.stop()
    print(">> A ボタン（キーボードの 1）で、見つけた AR マーカーを表示します")


def update():
    image = rc.camera.get_color_image()
    if image is None:
        return

    markers = rc_utils.get_ar_markers(image, POTENTIAL_COLORS)

    if rc.controller.was_pressed(rc.controller.Button.A):
        print(f"見つけたマーカー：{len(markers)} 個")
        for marker in markers:
            corners = marker.get_corners()          # 4つの角の (行, 列)
            center = corners.mean(axis=0)           # 4つの角の平均 ＝ 中心
            height = corners[:, 0].max() - corners[:, 0].min()   # 写った高さ（画素）
            print(f"  ID {marker.get_id()}  向き {marker.get_orientation().name}"
                  f"  色 {marker.get_color()}"
                  f"  中心 ({center[0]:.0f}, {center[1]:.0f})  高さ {height}")

    rc_utils.draw_ar_markers(image, markers)   # 見つけたマーカーを緑の枠で囲む
    rc.display.show_color_image(image)


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
```

シミュレータのレベルは、**Sandbox Environments** の **AR Marker Sandbox** を使います。マーカーのついた箱をクリックして選び、左クリックで模様（番号）、右クリックで色を変えられます。マウスのホイールで回すこともできます。図1の画像を渡したときの表示は、次のとおりです。

```text
見つけたマーカー：2 個
  ID 3  向き RIGHT  色 red  中心 (218, 498)  高さ 79
  ID 1  向き UP  色 blue  中心 (220, 190)  高さ 149
```

リストの中でマーカーが並ぶ順番は、決まっていません（OpenCV の版によっても変わりました）。特定の番号のマーカーを使いたいときは、`get_id()` で番号を確かめてから使います。

箱を回して、向きが `UP`→`RIGHT`→`DOWN`→`LEFT` と変わることを確かめましょう。

## ④ 数式・コード

### 向きの決め方

ライブラリは、0番の角（模様の左上）と、その対角の2番の角の位置を比べて、向きを決めています。

| 0番の角が、2番の角より | 向き |
|---|---|
| 上にあり、左にある | `UP`（そのまま） |
| 上にあり、右にある | `RIGHT`（時計回りに 90°） |
| 下にあり、右にある | `DOWN`（180°） |
| 下にあり、左にある | `LEFT`（反時計回りに 90°） |

`get_orientation()` が返す値には番号もついていて、`marker.get_orientation().value` は、`UP` が 0、`LEFT` が 1、`DOWN` が 2、`RIGHT` が 3 です。この番号は、「画像で見て左上にある角が、何番の角か」を表しています。

### マーカーを印刷して、実物で試す

OpenCV を使うと、好きな番号のマーカーの画像を作れます。印刷すれば、実機で試せます。

```python:make_marker.py
import cv2 as cv

dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_5X5_250)
image = cv.aruco.generateImageMarker(dictionary, 7, 400)   # 番号 7 のマーカーを 400 画素角で
image = cv.copyMakeBorder(image, 80, 80, 80, 80, cv.BORDER_CONSTANT, value=255)   # まわりに白い余白
cv.imwrite("marker_7.png", image)
```

まわりに白い余白をつけているのは、黒いふちの外側が白くないと、マーカーを見つけにくくなるからです。余白は、マーカーの幅の5分の1くらいとると安心です。この本で試したところ、余白が細い（マーカーの幅の1割くらいの）画像は、新しい版の OpenCV では見つかるのに、インストーラが入れる版（4.8）では見つからないことがありました。

## ⑤ つまずきポイント

### 実機で、マーカーが1つも見つからない

`get_ar_markers()` は、何も指定しないと 6×6 の辞書でさがします。実機の授業で使う 5×5 のマーカーは、次のように辞書を指定しないと見つかりません。説明用に作った 5×5 のマーカーの画像でも、何も指定しないと 0 個、5×5 を指定すると 1 個見つかりました。

```python
import cv2 as cv
markers = rc_utils.get_ar_markers(image, marker_type=cv.aruco.DICT_5X5_250)
```

### 色が `not detected` になる

色の候補を渡していないか、候補の HSV の範囲に合う色が、マーカーのまわりになかったときです。5-1 の `hsv_probe.py` で、ふちの色を測り直しましょう。

### 遠くや、ななめから見たマーカーが見つからない

模様のマスが小さく写りすぎたり、大きくゆがんだりすると、読みとれなくなります。近づくか、正面から見るようにしましょう。マーカーの一部が隠れていても、見つかりません。

### `draw_ar_markers()` を呼んだら、次のコマの画像まで変わってしまった

`draw_ar_markers()` は、渡した画像に直接描きこみます。`rc.camera.get_color_image()` は毎回コピーを返すので問題ありませんが、`get_color_image_no_copy()` を使った場合は、自分でコピーを作ってから描きます。

## ⑥ 確認問題

**問1**　`get_ar_markers()` が空のリストを返しました。考えられる原因を2つ答えましょう。

:::details 答えの例
(1) 画面の中にマーカーが写っていない、または一部が隠れている。
(2) マーカーの辞書が違う（たとえば 5×5 のマーカーを、6×6 の辞書でさがしている）。
ほかに、小さく写りすぎている、ななめすぎる、なども考えられます。
:::

**問2**　マーカーを反時計回りに 90° 回して置きました。`get_orientation()` は何を返しますか。

:::details 答え
`LEFT` です。模様の上が、画像の中で左を向くからです。
:::

**問3**　4つの角が `(100, 300)`、`(100, 380)`、`(180, 380)`、`(180, 300)` のマーカーの中心はどこですか。画面の左右どちら寄りですか（画面の横は 640 画素）。

:::details 答え
行の平均は $(100 + 100 + 180 + 180) \div 4 = 140$、列の平均は $(300 + 380 + 380 + 300) \div 4 = 340$ なので、中心は (140, 340) です。列が 320 より少し大きいので、ほぼ真ん中の、わずかに右寄りです。
:::

## ⑦ 原典

- `get_ar_markers()`・`ARMarker`・`Orientation`・`draw_ar_markers()`（6×6 と 5×5 の辞書、ふちの色の調べ方、向きの決め方）：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_utils.py`（GPL-3.0）
- 色の候補 `BLUE`・`RED` の範囲：同じく `racecar_utils.py` の使用例
- AR Marker Sandbox の操作：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `LevelCollection.cs`
- マーカーの作り方：[OpenCV のドキュメント「Detection of ArUco Markers」](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)

図1は、OpenCV で作ったマーカーを貼りつけた、説明用の画像です。`ar_check.py`・`make_marker.py` と⑤の結果は、この画像を1コマずつ渡すプログラムで、インストーラが入れる版（OpenCV 4.8.1）と新しい版（4.13）の両方で確かめたものです。
