---
title: "5-13 正解を付ける — アノテーション（Label Studio）"
free: true
---

5-12 で集めた写真は、まだ「ただの写真」です。教師あり学習（5-6）には、それぞれの写真に**正解**が必要です。物体検出の正解は、「写真のどこに、何があるか」、つまり**枠と名前**です。この作業を**アノテーション**といいます。この回では、無料で使えるアノテーションの道具「Label Studio」で正解を付け、5-14 の学習で使える形に書き出します。

## ① この回でできるようになること

1. Label Studio を用意して、写真を読みこめる
2. 写真の中の物に、枠と名前（ラベル）を付けられる
3. 正解を Pascal VOC 形式で書き出し、その中身（XML）を読める
4. 書き出した正解を、プログラムで確かめられる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Annotation | アノテーション（正解付け） | データに正解を付ける作業 |
| Label | ラベル | 物の名前。この回では「cone」など |
| Label Studio | Label Studio | ブラウザで使える、アノテーションの無料の道具 |
| Task | タスク | Label Studio での、正解を付ける1枚1枚の写真 |
| Pascal VOC | Pascal VOC（パスカル ボック） | 物体検出の正解を XML で書く、よく使われる形式 |
| XML | XML | `<名前>中身</名前>` のような「タグ」で、データを書く方法 |
| Virtual environment | 仮想環境 | Python の道具を、ほかと混ざらないように入れておく専用の場所 |

## ③ 本文

### Label Studio を用意する

Label Studio は、自分のパソコンの中で動かし、ブラウザで操作する道具です。Python 3.8 以降が必要です。Windows の人は、1-2 で用意した WSL の Ubuntu のターミナルで操作します。

```bash
python3 -m venv ls-env              # Label Studio 専用の仮想環境を作る
source ls-env/bin/activate          # 仮想環境に入る
python -m pip install label-studio  # Label Studio を入れる
label-studio                        # 起動する
```

起動すると、ブラウザで `http://localhost:8080` が開きます（開かなければ、自分でこのアドレスを開きます）。はじめて使うときは、アカウントを作る画面が出るので、メールアドレスとパスワードを決めて登録します。このアカウントは、自分のパソコンの Label Studio の中だけで使うものです。

次に使うときは、ターミナルで `source ls-env/bin/activate` をしてから `label-studio` を打ちます。終わるときは、ターミナルで Ctrl＋C を押します。

### 正解を付ける流れ

![Label Studio で正解を付ける4つの手順。1 プロジェクトを作る：Create Project、Data Import で写真を読みこむ。2 ラベルを決める：Labeling Setup で Object Detection with Bounding Boxes を選び、名前（例：cone）を登録する。3 枠を描く：名前を選び、物をドラッグで囲み、Submit で次の写真へ。4 書き出す：Export で Pascal VOC XML を選ぶと、ZIP の中に images（写真）と Annotations（XML）が入っている。3 の作業を、すべての写真について行う。1枚の写真に物がいくつあっても、全部に枠を付ける](/images/racecar-neo-jp/5-13/fig1-flow.png)
*図1　Label Studio で正解を付ける流れ*

#### 1. プロジェクトを作る

1. **Create Project**（または Create）を押し、**Project Name** にプロジェクトの名前（例：`cone-detection`）を入れる
2. **Data Import** で、5-12 で撮った写真（`dataset/images` の中の `.jpg`）を、ドラッグ・アンド・ドロップで読みこむ。枚数が多いときは、何回かに分けて読みこむとよい

#### 2. ラベルを決める

1. **Labeling Setup** で、**Computer Vision** の中の **Object Detection with Bounding Boxes** を選ぶ
2. 見本として入っているラベル（`Airplane` と `Car`）を消し、自分のラベルを加える（例：`cone`）。見つけたい物が何種類もあるなら、その数だけ加える
3. **Save** で保存する

ラベルの名前は、5-14 の学習のプログラムに、**一字一句同じ**に書くことになります。大文字・小文字も区別されるので、`cone` と決めたら、ずっと `cone` を使います。

#### 3. 枠を描く

1. プロジェクトの写真の一覧から、1枚めを開く（**Label All Tasks** で、順番に開いていくこともできる）
2. 画面の下などに並んでいるラベルの中から、`cone` をクリックして選ぶ（ラベルの横に出ている数字のキーでも選べる）
3. 写真の上で、物を囲むようにドラッグして、枠を描く。枠の角やふちをドラッグすると、大きさを直せる
4. 写真の中のすべての物に枠を描いたら、**Submit** を押して、次の写真へ進む

#### 4. 書き出す

すべての写真に枠を付けたら、プロジェクトの画面で **Export** を押し、形式に **Pascal VOC XML** を選んで書き出します。ZIP ファイルがダウンロードされます。

### よい正解を付けるきまり

5-6 で学んだように、正解がまちがっていると、モデルはまちがいも学んでしまいます。はじめに、次のようなきまりを決めて、全部の写真で同じように付けましょう。何人かで分けて作業するときは、とくに大事です。

- **枠は、物にぴったり合わせる**：すき間を空けすぎたり、物の一部を枠の外にはみ出させたりしない
- **写っている物には、全部付ける**：1枚に3つ写っていたら、3つとも。付け忘れると、「これはコーンではない」と教えることになる
- **一部がかくれた物をどうするか、決めておく**：たとえば「半分以上見えていれば付ける」のように
- **同じ物には、いつも同じラベル**：`cone` と `Cone` をまぜない

### 書き出したファイルの中身

ZIP を展開すると、次の2つのフォルダが入っています。

| フォルダ | 中身 |
|---|---|
| `images` | 写真。Label Studio に読みこんだとき、名前の先頭に `1a2b3c4d-` のような記号が付く |
| `Annotations` | 写真1枚ごとの正解の XML ファイル。写真と同じ名前で、拡張子だけ `.xml` |

![左は写真 1a2b3c4d-img_0000.jpg で、2つのコーンに枠が付いている。左のコーンの枠の左上が (xmin, ymin)、右下が (xmax, ymax)。右はその正解ファイル Annotations/1a2b3c4d-img_0000.xml の一部。annotation の中に、folder、filename、size（width 640、height 480、depth 3）と、枠ごとの object がある。1つめの object は name が cone で、bndbox の xmin が 104、ymin が 203、xmax が 177、ymax が 320](/images/racecar-neo-jp/5-13/fig2-voc.png)
*図2　写真と、その正解の XML ファイル（説明用に作った例）*

XML ファイルは、`<タグの名前>` と `</タグの名前>` で中身をはさんで書く形式です。大事なのは次のところです。

- `<filename>`：どの写真の正解か
- `<size>`：写真の幅・高さ・色の数
- `<object>`：枠1つにつき1つ。中の `<name>` がラベル、`<bndbox>` が枠の**左上** (`xmin`, `ymin`) と**右下** (`xmax`, `ymax`) の画素の位置（5-11 の「左上と右下」の表し方）

### 正解をプログラムで確かめる

何百枚もの写真の正解を、目で1つずつ確かめるのはたいへんです。次のプログラムは、書き出した正解を読んで、枠を写真に描いて保存します。ラベルごとの枠の数を数え、正解のない写真も知らせます。

```python:check_voc.py
"""
check_voc.py
Label Studio から書き出した Pascal VOC の正解（Annotations フォルダの XML）を読んで、
枠を写真に描き、check フォルダに保存する。名前ごとの枠の数と、正解のない写真も調べる。
"""

import os
import xml.etree.ElementTree as ET
import cv2 as cv

EXPORT_DIR = "export"                               # 書き出した ZIP を展開したフォルダ
IMAGE_DIR = os.path.join(EXPORT_DIR, "images")
ANNOT_DIR = os.path.join(EXPORT_DIR, "Annotations")
CHECK_DIR = os.path.join(EXPORT_DIR, "check")
os.makedirs(CHECK_DIR, exist_ok=True)

counts = {}   # 名前ごとの枠の数
for name in sorted(os.listdir(IMAGE_DIR)):
    if not name.endswith(".jpg"):
        continue
    xml_path = os.path.join(ANNOT_DIR, name[:-4] + ".xml")   # 写真と同じ名前の XML
    if not os.path.exists(xml_path):
        print(f"正解がない写真：{name}")
        continue

    image = cv.imread(os.path.join(IMAGE_DIR, name))
    root = ET.parse(xml_path).getroot()
    for obj in root.findall("object"):                       # 枠の1つ1つについて
        label = obj.find("name").text
        box = obj.find("bndbox")
        x0, y0, x1, y1 = [int(float(box.find(k).text)) for k in ("xmin", "ymin", "xmax", "ymax")]
        cv.rectangle(image, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv.putText(image, label, (x0, max(y0 - 5, 12)), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        counts[label] = counts.get(label, 0) + 1
    cv.imwrite(os.path.join(CHECK_DIR, name), image)

for label, n in counts.items():
    print(f"{label}：枠 {n} 個")
```

写真3枚のうち2枚に正解を付けた例で試すと、次のように表示されました。

```text
正解がない写真：9c0d1e2f-img_0002.jpg
cone：枠 3 個
```

- `xml.etree.ElementTree`（`ET`）は、XML を読むための、Python に最初から入っている道具です。`root.findall("object")` で、`<object>` をすべて取り出せます
- `check` フォルダにできた写真を、画像を見るソフトで次々に見ていけば、付け忘れや、ずれた枠に気づけます
- **正解がない写真**は、5-14 の学習の手順でエラーの原因になります（5-14 の⑤）。付け忘れなら Label Studio に戻って付け、物が写っていない写真なら `images` フォルダから取りのぞきます

## ④ 数式・コード

### 左上と右下から、中心と大きさへ

VOC の枠は「左上と右下」、実機の `rc.vision.get_detections()` は「中心と大きさ」でした（5-11）。変換は次のとおりです。

```python
def voc_to_center(xmin, ymin, xmax, ymax):
    """左上と右下 → (中心の x, 中心の y, 幅, 高さ)"""
    return ((xmin + xmax) / 2, (ymin + ymax) / 2, xmax - xmin, ymax - ymin)

print(voc_to_center(104, 203, 177, 320))   # (140.5, 261.5, 73, 117)
```

### 枠の大きさの分布を調べる

枠の大きさ（面積）を全部の正解について集めると、「遠くの小さなコーンの写真が少ない」のような、データのかたよりに気づけます。`check_voc.py` の中で、`(x1 - x0) * (y1 - y0)` をリストにためておき、最後に最小・最大・平均を表示してみましょう。

## ⑤ つまずきポイント

### ラベルの名前が、ところどころ違っている

`cone`、`Cone`、`cone ` （最後に空白）は、すべて別の名前として扱われます。`check_voc.py` の最後の表示で、ラベルの種類が思ったより多ければ、名前がそろっていません。Label Studio のラベルの設定を見直しましょう。

### 書き出しが終わらない、失敗する

Label Studio の無料版では、書き出しの処理に時間がかかりすぎると、とちゅうで止まることがあります（説明書では約 90 秒）。写真がとても多いときは、プロジェクトを分けて作るなどの工夫をします。

### ログインのパスワードを忘れた

アカウントは、自分のパソコンの中の Label Studio だけのものです。新しいアカウントを作ることもできますが、作ったプロジェクトは前のアカウントに入っているので、パスワードは控えておきましょう。

### 写真の名前の先頭に、知らない記号が付いている

Label Studio は、読みこんだ写真の名前の先頭に、ほかの写真と重ならないための記号を付けます。写真と XML は同じ名前になっているので、そのまま使ってかまいません。

## ⑥ 確認問題

**問1**　ある写真にコーンが2つ写っているのに、1つにしか枠を付けませんでした。学習にどんな悪い影響がありますか。

:::details 答え
枠を付けなかったコーンは、「コーンではないもの」として学習されてしまいます。モデルが、コーンを見のがしやすくなるおそれがあります。
:::

**問2**　XML の `<bndbox>` が `xmin 200, ymin 120, xmax 260, ymax 240` でした。枠の幅・高さと、中心の位置を求めましょう。

:::details 答え
幅は $260 - 200 = 60$、高さは $240 - 120 = 120$ です。中心は $\left(\frac{200 + 260}{2}, \frac{120 + 240}{2}\right) = (230, 180)$ です。
:::

**問3**　`check_voc.py` の表示が次のようになりました。何が起きていると考えられますか。

```text
cone：枠 250 個
Cone：枠 12 個
```

:::details 答え
同じコーンに、`cone` と `Cone` の2つのラベルが使われています。どちらかにそろえる必要があります。そのままでは、モデルは2つを別の種類として学ぼうとしてしまいます。
:::

## ⑦ 原典

この回は、夏のプログラムの手順を参考に、この本で加えた解説です。

- Label Studio の入れ方（Python 3.8 以降、`pip install label-studio`、`http://localhost:8080`）：[Label Studio のドキュメント「Install and upgrade」](https://labelstud.io/guide/install)
- 書き出しの形式（Pascal VOC XML）と、無料版の書き出しの時間の制限：[Label Studio のドキュメント「Export annotations」](https://labelstud.io/guide/export)
- 物体検出のテンプレート「Object Detection with Bounding Boxes」：[Label Studio のドキュメント](https://labelstud.io/templates/image_bbox)
- 書き出される XML の形（`images` と `Annotations` のフォルダ、タグの並び）：label-studio-converter（Label Studio の書き出しのプログラム）の `convert_to_voc()`
- Label Studio の XML を学習に使う手順：**efficientdet-edgetpu.ipynb**（[racecar-neo-summer-labs](https://github.com/MITRacecarNeo/racecar-neo-summer-labs)、GPL-3.0）

Label Studio の画面の名前は、使うバージョンによって少し違うことがあります。`check_voc.py` は、label-studio-converter と同じ形で作った XML で確かめました。
