---
title: "5-14 学習させて、Edge TPU 用に変換する"
free: true
---

いよいよ、5-12 で集めて 5-13 で正解を付けた写真で、物体検出のモデルを学習させます。そして、できたモデルを実機の Edge TPU（2-4）で動く形に変換し、車のプログラムから `rc.vision.get_detections()` で使えるようにします。この回は、夏のプログラムの課題 **efficientdet-edgetpu.ipynb** の流れに沿って進めます。

## ① この回でできるようになること

1. 物体検出のモデルを作ってから車で使うまでの、全体の流れを説明できる
2. 学習用のノートブックの各段で、何をしているかを説明できる
3. 量子化と、Edge TPU 用の変換が必要な理由を説明できる
4. 変換したモデルを車に入れて、プログラムから使うまでの手順を説明できる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Jupyter Notebook | ジュピター ノートブック | プログラムを「セル」に分けて、1つずつ実行しながら結果を見られる道具。拡張子は `.ipynb` |
| Transfer learning | 転移学習 | たくさんのデータですでに学習したモデルを出発点にして、自分のデータで学習し直すこと |
| Epoch | エポック | 学習用データを1周ぶん使って学習すること |
| Batch | バッチ | 1回の学習で、まとめて使うデータのかたまり |
| TensorFlow Lite | TensorFlow Lite | スマートフォンや小さな機械で動かすための、モデルの形式。拡張子は `.tflite` |
| Quantization | 量子化 | モデルの中の小数を、整数で表して小さく・速くすること |
| Edge TPU | Edge TPU | Google の、ニューラルネットワークの計算を速くする小さな部品。実機に積まれている |
| Compiler | コンパイラ | モデルやプログラムを、ある機械で動く形に変換する道具 |

## ③ 本文

### 全体の流れ

![物体検出のモデルを作って車で使うまでの流れ。車で ① 写真を撮り（capture.py、5-12）、scp でパソコンにコピーする。パソコンで ② 正解を付け（Label Studio、5-13）、③ 学習 60%・検証 20%・テスト 20% に分け、④ EfficientDet-Lite0 を 50 周（エポック）学習させ、⑤ テスト用データで AP を評価して .tflite（整数に量子化）を書き出す。x86-64 の Linux のパソコンで ⑥ edgetpu_compiler で Edge TPU 用に変換し、_edgetpu.tflite とラベルを車へ送って、⑦ 車で rc.vision として使う](/images/racecar-neo-jp/5-14/fig1-pipeline.png)
*図1　物体検出のモデルを作って、車で使うまでの流れ*

この回は、③〜⑦を扱います。

:::message alert
**学習の道具について**
このノートブックは、Google の **TensorFlow Lite Model Maker** という道具を使います。この道具は古く、最後の版（0.4.3）は 2024年1月ごろのものです。古い版のライブラリを指定しているため、新しい Python には、そのままでは入らないことがよくあります。夏のプログラムでは、学習用の環境が用意されています。自分で用意するときは、Python 3.9 ごろの古い環境が必要になると考えておきましょう。
この回のノートブックのコードは、原典を読んで説明したもので、この本では実行して確かめていません。
:::

### ③ データを置いて、分ける

ノートブックのはじめのセルで、データの場所と、ラベルの名前を決めます。

```python
dataset_path = "../../dataset/name_of_dataset"
images_path = dataset_path + "/images"
labels_path = dataset_path + "/Annotations"

# Label Map
label_map = {1: 'name_of_object'}
```

- `name_of_dataset` の中に、5-13 で書き出した `images` と `Annotations` の2つのフォルダを置きます
- `label_map` の `'name_of_object'` を、5-13 で決めたラベルの名前（例：`'cone'`）に書きかえます。種類が2つなら `{1: 'cone', 2: 'person'}` のように、1 から番号を付けて並べます

次のセルの `split_dataset()` で、写真と正解を、**学習用 60%・検証用 20%・テスト用 20%** に分けます（5-6）。写真の順番は、決まった乱数でまぜてから分けるので、何度実行しても同じ分け方になります。

```python
train_dir, val_dir, test_dir = split_dataset(images_path, labels_path, val_split=0.2, test_split=0.2, out_path='split-dataset')
```

そのあとの `clean_xml_declaration()` は、Label Studio が書き出した XML の1行め（`<?xml version="1.0" encoding="utf-8"?>`）を取りのぞく関数です。ノートブックでは「Label Studio から来たデータをきれいにする」と説明されています。最後に `DataLoader.from_pascal_voc()` で、Pascal VOC 形式の正解を読みこみます。

### ④ 学習する

```python
spec = object_detector.EfficientDetLite0Spec()

model = object_detector.create(train_data=train_data,
                               model_spec=spec,
                               validation_data=validation_data,
                               epochs=50,
                               batch_size=10,
                               train_whole_model=True)
```

- **`EfficientDetLite0Spec()`**：5-11 で紹介した EfficientDet-Lite0 を使います。このモデルは、たくさんの写真（COCO という大きなデータセット）で**すでに学習してある**ものを出発点にします。「物の形を見分ける力」はすでに身についているので、自分の写真が数百枚でも、コーンの見分け方を学べます。このように学習し直すことを**転移学習**といいます
- **`epochs=50`**：学習用データを 50 周使います（**エポック**）
- **`batch_size=10`**：10 枚ずつまとめて損失と勾配を求め、パラメータを動かします（**バッチ**）。5-8 の勾配降下法を、10 枚ずつ区切って行うイメージです
- **`train_whole_model=True`**：モデル全体のパラメータを学習し直します。`False` にすると、最後のほうの層だけを学習します

たとえば学習用の写真が 120 枚なら、1エポックは $120 \div 10 = 12$ 回の更新で、50 エポックで 600 回、パラメータを動かすことになります。

### ⑤ 評価して、書き出す

```python
metrics = model.evaluate(test_data)
```

テスト用データで、5-11 で学んだ AP などを計算します。結果には、次のような値が入っています。

| 名前 | 意味 |
|---|---|
| `AP` | IoU の基準を 0.5〜0.95 まで変えて平均した AP。いちばん厳しい、総合の点数 |
| `AP50` | IoU が 0.5 以上なら当たりとしたときの AP |
| `AP75` | IoU が 0.75 以上なら当たりとしたときの AP（枠の位置の正確さも見る） |
| `APs`・`APm`・`APl` | 小さい物・中くらいの物・大きい物だけで測った AP |
| `AP_/cone` など | 種類ごとの AP |

遠くの小さなコーンを見のがしやすいモデルなら、`APs` が低くなります。どの値が低いかを見ると、どんな写真を足せばよいかのヒントになります。

```python
model.export(export_dir='.', tflite_filename=TFLITE_FILENAME, label_filename=LABELS_FILENAME,
             export_format=[ExportFormat.TFLITE, ExportFormat.LABEL])
```

`TFLITE_FILENAME`（例：`'cone.tflite'`）と `LABELS_FILENAME`（`'objects.txt'`）を決めて、モデルとラベルのファイルを書き出します。ラベルのファイルは、1行に1つずつ、種類の名前が書かれたテキストファイルです。

このとき、モデルは**量子化**されます。モデルの中の重みは、もともと小数（32ビットの浮動小数点数）ですが、これを −128〜127 の整数（8ビット）で近似して表します（④）。大きさはおよそ 4分の1 になり、計算も速くなります。Edge TPU は整数の計算しかできないので、量子化は欠かせません。

そのあとの `model.evaluate_tflite()` で、量子化したモデルの AP を測り直します。量子化で少しだけ精度が下がるので、下がりすぎていないかを確かめます。

### ⑥ Edge TPU 用に変換する

量子化した `.tflite` は、まだ Edge TPU で動く形ではありません。Google の **Edge TPU コンパイラ**（`edgetpu_compiler`）で変換します。このコンパイラは、**x86-64 の CPU を積んだ Debian・Ubuntu などの Linux** でしか動きません。車の Raspberry Pi では動かないので、パソコンで変換します（Windows なら、1-2 で用意した WSL の Ubuntu が候補になります）。

Coral の説明書では、次の手順で入れるように書かれています。

```bash
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
sudo apt-get update
sudo apt-get install edgetpu-compiler
```

変換は、次の1行です。

```bash
edgetpu_compiler cone.tflite
```

同じフォルダに、名前の最後に `_edgetpu` が付いた `cone_edgetpu.tflite` と、変換の記録（`.log`）ができます。記録には、モデルの計算のうち、いくつを Edge TPU で動かせたかが書かれています。Edge TPU で動かせない計算が残ると、その部分は Raspberry Pi の CPU で動くので、遅くなります。

### ⑦ 車に入れて、使う

1. **ファイルを車にコピーする**：`cone_edgetpu.tflite` と `objects.txt` を、`scp` で車に送ります（5-12）。たとえば、車のホームフォルダの中に `models` というフォルダを作って、そこに置きます

2. **どのモデルを使うかを設定する**：車の中の `~/ros2_ws/src/racecar_neo_ros2_driver/config/` に、`edgetpu.local.yaml` というファイルを作り、次のように書きます。ファイルの場所は、`/home/` から始まる形（**絶対パス**）で書きます

```yaml:edgetpu.local.yaml
edgetpu_node:
  ros__parameters:
    model_path: "/home/ユーザー名/models/cone_edgetpu.tflite"
    labels_path: "/home/ユーザー名/models/objects.txt"
```

もとの `edgetpu.yaml` には、何も書きかえずに残しておきます。`.local.yaml` は、もとの設定のあとに読みこまれて、書いた項目だけを上書きします。

3. **設定を反映する**：車のターミナルで、次の2つを実行します

```bash
racecar build              # 設定ファイルを組みこみ直す
racecar service restart    # 車のプログラム（teleop）を起動し直す
```

4. **プログラムで使う**：5-11 の `detect_follow.py` の `TARGET` を、自分のラベルの名前にして動かします。コーンを画面の左右に動かすと、ハンドルがそちらに切れるはずです

うまく動いたら、写真を集めて、正解を付けて、学習し直す、をくり返して、モデルを育てていきます。見つけられなかった場面の写真を足すのが、いちばん効果的です。

## ④ 数式・コード

### 量子化のしくみ

小数 $x$ を、整数 $q$（−128〜127）で表すには、「整数1つぶんが、小数でいくつにあたるか」を表す数 $s$（スケール）と、「小数の 0 にあたる整数」$z$（ゼロ点）を使います。

$$
q = \operatorname{round}\!\left(\frac{x}{s}\right) + z, \qquad x \approx s\,(q - z)
$$

```python:quantize.py
"""
quantize.py
小数（float）の重みを、-128〜127 の整数（int8）で表す「量子化」を試す。
"""

import numpy as np

w = np.array([-0.82, -0.31, 0.0, 0.07, 0.45, 1.13])      # もとの重み（小数）

scale = (w.max() - w.min()) / 255                         # 整数1つぶんが、小数でいくつにあたるか
zero_point = round(-128 - w.min() / scale)                # 小数の 0 にあたる整数

q = np.clip(np.round(w / scale) + zero_point, -128, 127).astype(np.int8)   # 量子化：小数 → 整数
back = (q.astype(np.float32) - zero_point) * scale                          # 元にもどす：整数 → 小数

print("scale =", round(scale, 5), " zero_point =", zero_point)
print("整数にした値  ：", q)
print("元にもどした値：", np.round(back, 3))
print("ずれの最大    ：", round(float(np.max(np.abs(back - w))), 4))
```

```text
scale = 0.00765  zero_point = -21
整数にした値  ： [-128  -62  -21  -12   38  127]
元にもどした値： [-0.818 -0.314  0.     0.069  0.451  1.132]
ずれの最大    ： 0.0035
```

元にもどした値は、もとの重みとほとんど同じです。ずれは、どれも $s$ の半分（約 0.0038）以下に収まります。1つの重みを 4 バイトから 1 バイトで表せるので、モデルの大きさは約 4分の1 になります。

### 1エポックの更新の回数

学習用データが $N$ 枚、バッチの大きさが $B$ のとき、1エポックでパラメータを動かす回数は、次のとおりです（$\lceil\ \rceil$ は切り上げ）。

$$
\left\lceil \frac{N}{B} \right\rceil
$$

## ⑤ つまずきポイント

### `split_dataset()` で `FileNotFoundError` になる

`split_dataset()` は、写真1枚ごとに、同じ名前の XML ファイルがあるものとして、コピーします。正解を1つも付けなかった写真には XML がないので、ここで止まります。5-13 の `check_voc.py` で「正解がない写真」を探して、取りのぞくか、正解を付けましょう。

また、XML の名前は、写真の名前の `jpg` を `xml` に**すべて**置きかえて作っています。`jpg_photo.jpg` のように、名前の途中に `jpg` がある写真は、`xml_photo.xml` を探してしまって見つかりません。写真の名前に `jpg` という文字を入れないようにしましょう（5-12 の `capture.py` の名前なら大丈夫です）。

### `pip install tflite-model-maker` が失敗する

上の注意のとおり、古い道具なので、新しい Python では入らないことがよくあります。用意された学習用の環境を使いましょう。

### 車で、名前のかわりに数字（`0` など）が出る

`class_id` が `'0'` のような数字の文字列になるのは、ラベルのファイルが読めていないときです。`edgetpu.local.yaml` の `labels_path` の書きまちがいや、ファイルの場所を確かめましょう。ラベルのファイルが見つからないと、Edge TPU のプログラムは警告（`Labels file not found`）を出します。

### 変換の記録に「CPU で動く」計算がたくさんある

Edge TPU で動かせない計算が入っていると、その部分は CPU で動くので、とても遅くなります。このノートブックの EfficientDet-Lite0 は、Edge TPU で動くように作られたモデルです。モデルの種類や書き出し方を変えたときに起きやすいので、まずはノートブックの手順どおりに書き出しましょう。

### 学習用データではよく見つかるのに、車ではうまく見つからない

5-6 の過学習や、5-12 のドメインギャップが考えられます。テスト用データの AP を確かめ、車を走らせる場所で撮った写真を足して、学習し直しましょう。

## ⑥ 確認問題

**問1**　学習用の写真が 150 枚、`batch_size=10`、`epochs=50` のとき、学習の間にパラメータを何回動かしますか。

:::details 答え
1エポックは $150 \div 10 = 15$ 回なので、50 エポックで $15 \times 50 = 750$ 回です。
:::

**問2**　量子化で、モデルの大きさがおよそ 4分の1 になるのはなぜですか。

:::details 答え
1つの重みを、32 ビット（4 バイト）の小数から、8 ビット（1 バイト）の整数で表すようにするからです。
:::

**問3**　`AP50` は高いのに、`AP75` がとても低いモデルがあります。このモデルは、どんなことが苦手だと考えられますか。

:::details 答え
物がある場所はだいたい当てられるものの、枠の位置や大きさを**正確に**合わせるのが苦手だと考えられます。IoU 0.5 なら当たりでも、0.75 の厳しい基準では外れになる枠が多いということです。
:::

**問4**　車の Raspberry Pi の上で `edgetpu_compiler` を動かせないのはなぜですか。

:::details 答え
Edge TPU コンパイラは、x86-64 の CPU を積んだ Linux でしか動かないからです。Raspberry Pi の CPU は ARM という種類なので、パソコンで変換してから、車にコピーします。
:::

## ⑦ 原典

- 学習と書き出しの手順（データの場所、`label_map`、`split_dataset()`、`clean_xml_declaration()`、`EfficientDetLite0Spec`、`epochs=50`、`batch_size=10`、`train_whole_model=True`、`evaluate`・`export`・`evaluate_tflite`）：**efficientdet-edgetpu.ipynb**（[racecar-neo-summer-labs](https://github.com/MITRacecarNeo/racecar-neo-summer-labs)、GPL-3.0）
- 実機での設定（`config/edgetpu.yaml` の `model_path`・`labels_path`、`.local.yaml` による上書き、`racecar build`、`racecar service restart`、ラベルがないときの数字の表示）：[racecar_neo_ros2_driver](https://github.com/MITRacecarNeo/racecar_neo_ros2_driver) の README・`config/edgetpu.yaml`・`launch_common.py`・`edgetpu_node.py`・`scripts/racecar-tool.sh`（GPL-3.0）
- TensorFlow Lite Model Maker と、書き出すときの量子化（初期設定で整数に量子化）：[Google AI Edge「Object Detection with TensorFlow Lite Model Maker」](https://developers.google.com/edge/litert/libraries/modify/object_detection)
- Edge TPU コンパイラ（x86-64 の Debian 系 Linux が必要、入れ方、`_edgetpu` の名前）：[Coral「Edge TPU Compiler」](https://gweb-coral-full.uc.r.appspot.com/docs/edgetpu/compiler/)
- tflite-model-maker の最後の版（0.4.3）と、古い版のライブラリの指定：PyPI の配布ファイルの情報

`quantize.py` は、実行して確かめたものです。
