---
title: "1-3 はじめてのスクリプト（Lab A）"
free: true
---

いよいよ、自分でプログラムを書きます。この回で取り組むのは、オンライン事前コースの最初の課題 **Lab A「文字を表示する（Printing Statements）」** です。車はまだ動かしませんが、RACECAR のプログラムがどんなリズムで動いているのかを、画面に文字を出しながら確かめます。

## ① この回でできるようになること

1. `print` で文字や計算の結果を表示できる
2. 変数と f 文字列を使って、値を文章の中に埋め込める
3. `start()`・`update()`・`update_slow()` が、それぞれ**いつ・何回**動くのかを説明できる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Script | スクリプト | 上から順に実行される、短めのプログラム |
| Function | 関数 | 名前を付けてひとまとめにした処理 |
| Variable | 変数 | 値に名前を付けて、しまっておく箱 |
| String | 文字列 | `"Hello"` のように、引用符で囲んだ文字の並び |
| f-string | f 文字列 | 文字列の中に `{ }` で値を埋め込める書き方 |
| Global variable | グローバル変数 | 関数の外で作り、どの関数からも使える変数 |
| Frame | フレーム（コマ） | シミュレータが画面を1回更新する単位。1秒に約60コマ |
| Delta time | 経過時間 | 前のコマから今のコマまでにかかった時間 |
| Terminal window | ターミナル | `print` の結果が表示される画面 |

## ③ 本文

### RACECAR のプログラムの形

RACECAR のプログラムは、どれも同じ形をしています。課題のフォルダにある `template.py` を、日本語のコメントにして見てみましょう。

```python:template.py（コメントを日本語にしたもの）
import racecar_core

# 車を操作するための「リモコン」を作る。以後、rc. で始まる命令で車を操作する
rc = racecar_core.create_racecar()

# グローバル変数はここに書く


# start() は、User Program モードに入ったときに1回だけ動く
def start():
    pass


# update() は、start() のあと、1コマごとに動く（1秒に約60回）
def update():
    pass


# update_slow() は、update() と同じように繰り返し動くが、1秒に1回だけ
def update_slow():
    pass


# ここは書き換えない：3つの関数を登録して、シミュレータとのやりとりを始める
if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```

あなたが書くのは、`start()`・`update()`・`update_slow()` の中身だけです。最後の2行が「この3つの関数を、決まったタイミングで呼んでください」とライブラリに頼んでいます。`pass` は「何もしない」という意味の命令で、中身がまだないときの置き物です。

### 3つの関数は、いつ動くのか

1-1 で、ロボットは「見る・考える・動く」を何度も繰り返すと学びました。RACECAR のプログラムで、この繰り返しを受け持つのが `update()` です。

![start は最初に1回だけ、update は1秒に約60回、update_slow は最初のコマで1回とそのあと1秒に1回動くことを示すタイムライン](/images/racecar-neo-jp/1-3/fig1-timeline.png)
*図1　3つの関数が動くタイミング*

| 関数 | 動くタイミング | 書く内容の例 |
|---|---|---|
| `start()` | User Program モードに入ったとき、**1回だけ** | 変数に最初の値を入れる、車を止めておく |
| `update()` | そのあと**1コマごと**（1秒に約60回） | センサを読んで、ハンドルとアクセルを決める |
| `update_slow()` | 最初のコマで1回、そのあと**1秒に1回** | 様子をターミナルに表示して確かめる |

`update()` は1秒に約60回も呼ばれるので、ここで `print` を書くと、ターミナルが文字であふれます。人が読むための表示は `update_slow()` に書く、というのが基本の使い分けです。Lab A は、まさにこの違いを体験する課題です。

### Lab A で使う Python の書き方

Lab A に必要な Python の書き方を、先にまとめておきます。

**文字を表示する：`print`**

```python
print("Hello World!")        # Hello World! と表示される
print(523 + 910)             # 計算した結果 1433 が表示される
```

**変数に値をしまう**

```python
your_name = "Taro"           # your_name という名前の箱に "Taro" を入れる
counter = 0                  # counter という箱に 0 を入れる
counter += 1                 # counter に 1 を足す（counter = counter + 1 と同じ）
```

**f 文字列で値を埋め込む**

文字列の前に `f` を付けると、`{ }` の中に書いた変数や計算の結果が埋め込まれます。

```python
print(f"Hello {your_name}!")           # Hello Taro! と表示される
print(f"523 + 910 = {523 + 910}")      # 523 + 910 = 1433 と表示される
```

**小数を丸める：`round`**

```python
round(3.14159, 1)            # 小数第1位までに丸めて 3.1
round(3.14159, 2)            # 小数第2位までに丸めて 3.14
```

**関数の中でグローバル変数を書き換える：`global`**

関数の外で作った変数を、関数の中で**書き換える**ときは、関数の最初に `global 変数名` と書きます。

```python
counter = 0

def update():
    global counter           # 外の counter を使う、という宣言
    counter += 1
```

**インデント（字下げ）**

Python では、行の先頭の空白（インデント）で「どこまでが関数の中か」を表します。関数の中身は、半角スペース4つ分下げて書きます。

### Lab A をやってみよう

課題のファイルは、`racecar cd` で移動した labs フォルダの中の `lab_a/lab_a.py` です。VS Code などのエディタで開いてください。

課題のゴールは、実行したときにターミナルへ次の4つを表示することです（原典の Expected Outcome より）。

- `Hello World!`
- 523 + 910 の合計
- 自分の名前を入れた歓迎のメッセージ
- プログラムが始まってからの経過時間（秒）。**1秒に1回**表示する

ファイルの中の `# TODO` と書かれた場所が、あなたが書く部分です。Part 1 から Part 5 まであります。

#### Part 1〜3：start() の中で表示する

`start()` の中に、3つの `print` を書きます。`start()` は1回しか動かないので、この3行は最初に1回ずつ表示されます。

- **Part 1**：`Hello World!` と表示する
- **Part 2**：523 + 910 の合計を、**Python に計算させて** f 文字列で埋め込み、`The sum of 523 + 910 is: 〇〇` と表示する
- **Part 3**：変数 `your_name` に自分の名前を入れ、`Hello 〇〇, welcome to RACECAR!` と表示する

:::details 答えの例（Part 1〜3）
```python
def start():
    # Part 1
    print("Hello World!")

    # Part 2
    print(f"The sum of 523 + 910 is: {523 + 910}")

    # Part 3
    your_name = "Taro"
    print(f"Hello {your_name}, welcome to RACECAR!")
```
Part 2 で `{1433}` と答えを直接書かないのがポイントです。計算を Python に任せれば、数字を変えても正しい答えが表示されます。
:::

#### Part 4：update() の中で経過時間を表示する

`update()` の中には、次の行がすでに書いてあります。

```python
counter += rc.get_delta_time()
```

`rc.get_delta_time()` は、前のコマから今のコマまでに**かかった時間**を、秒の単位で返します。これを毎コマ `counter` に足していくので、`counter` には「プログラムが始まってからの時間」がたまっていきます。

**Part 4**：`counter` を使って、`〇〇 seconds have passed since the program started!` と表示する行を書き、コメントを外して実行してみましょう。

実行すると、ターミナルは次のようになります。

```text
Hello World!
The sum of 523 + 910 is: 1433
Hello Taro, welcome to RACECAR!
0.01666666753590107 seconds have passed since the program started!
0.03333333507180214 seconds have passed since the program started!
0.05000000260770321 seconds have passed since the program started!
0.06666667014360428 seconds have passed since the program started!
（1秒に約60行ずつ、どんどん流れていく）
```

1秒に約60行も表示されて、とても読めません。これが「`update()` で `print` をしてはいけない」理由です。

:::details 答えの例（Part 4）
```python
def update():
    global counter
    counter += rc.get_delta_time()
    print(f"{counter} seconds have passed since the program started!")
```
:::

:::message
数字の最後が `...753590107` のように中途半端なのは、シミュレータが時間を送るときに使う小数の形式（32ビットの浮動小数点数）の誤差です。1/60 = 0.01666… はコンピュータの中でぴったり表せないため、ごくわずかなずれが出ます。Part 5 で丸めて表示するのには、この理由もあります。
:::

#### Part 5：update_slow() で1秒に1回だけ表示する

**Part 5**：`update_slow()` の中に、`counter` を**小数第1位まで丸めて**表示する行を書きます。`pass` の行はコメントにしてください（消しても大丈夫です）。あわせて、Part 4 の `print` の行をコメントに戻します。

正しく書けると、ターミナルは次のようになります。

```text
Hello World!
The sum of 523 + 910 is: 1433
Hello Taro, welcome to RACECAR!
0.0 seconds have passed since the program started!
1.0 seconds have passed since the program started!
2.0 seconds have passed since the program started!
3.0 seconds have passed since the program started!
```

1秒に1行ずつ、読みやすく表示されます。最初の `0.0` は、`update_slow()` が最初のコマでも1回呼ばれるためです（図1）。

:::details 答えの例（Part 5）
```python
def update_slow():
    print(f"{round(counter, 1)} seconds have passed since the program started!")
```
`update_slow()` の中では `counter` を読むだけで書き換えないので、`global counter` はなくても動きます。
:::

#### 実行のしかた

1-2 と同じ手順で実行します。

```bash
racecar cd
cd lab_a
racecar sim lab_a.py
```

シミュレータでレベルを開き、Enter で User Program モードに入ると、`start()` の3行が表示され、続いて経過時間が表示されはじめます。

## ④ 数式・コード

### 経過時間を足し合わせるしくみ

Part 4 でしていることを式で書くと、次のようになります。$n$ コマ目の経過時間を $\Delta t_n$ とすると、

$$
\text{counter} = \Delta t_1 + \Delta t_2 + \cdots + \Delta t_n
$$

1コマの長さがぴったり $\frac{1}{60}$ 秒なら、60コマで1秒です。ただし実際には、パソコンの忙しさによって1コマの長さは少しずつ変わります。だから「60回数えたら1秒」ではなく、**毎回かかった時間を足していく**のが正しいやり方です。この考え方は、第4章で車を決まった時間だけ走らせるときにも使います。

### 完成したコードの例

:::details lab_a.py の完成例（コメントは日本語にしています）
```python:lab_a.py
import racecar_core

rc = racecar_core.create_racecar()

counter = 0


def start():
    # Part 1
    print("Hello World!")

    # Part 2
    print(f"The sum of 523 + 910 is: {523 + 910}")

    # Part 3
    your_name = "Taro"
    print(f"Hello {your_name}, welcome to RACECAR!")


def update():
    global counter
    counter += rc.get_delta_time()
    # Part 4（確かめたらコメントに戻す）
    # print(f"{counter} seconds have passed since the program started!")


def update_slow():
    # Part 5
    print(f"{round(counter, 1)} seconds have passed since the program started!")


if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
```
:::

## ⑤ つまずきポイント

### `global` を書き忘れた

`update()` の中の `global counter` を消すと、次のエラーで止まります。

```text
UnboundLocalError: local variable 'counter' referenced before assignment
```

「関数の中の `counter` という変数に、まだ値が入っていない」という意味です。関数の中で外の変数を**書き換える**ときは、`global` が必要です。

:::message
原典の Lab A では、関数の外（ファイルの上のほう）にも `global counter` と書かれています。関数の外での `global` は何の働きもしないので、あってもなくてもかまいません。大事なのは、`update()` の中の `global counter` のほうです。
:::

### 全角のスペースや引用符が混ざった

日本語入力のまま空白やカギかっこを打つと、見た目は同じでも別の文字になります。

```text
SyntaxError: invalid non-printable character U+3000    ← 全角スペースが混ざっている
SyntaxError: invalid character '“' (U+201C)            ← 全角の引用符が混ざっている
```

プログラムを書くときは、日本語入力をオフにします。文字列の**中身**（`"こんにちは"` のような部分）だけは、日本語を使っても大丈夫です。

### f を付け忘れた

`print("{counter} seconds ...")` のように `f` を付け忘れると、`{counter}` という文字がそのまま表示されます。

### もう一度 Enter を押したら、時間が 0 から始まらない

Backspace で手動運転に戻り、もう一度 Enter を押すと、`start()` はもう一度動きます。しかし `counter` を 0 に戻す命令がどこにもないので、前の続きから数えはじめます。毎回 0 から数えたいときは、`start()` の中で `counter` を 0 にします。

```python
def start():
    global counter
    counter = 0
    # （以下、Part 1〜3）
```

サンプルの `demo.py` の `start()` も、同じように変数を最初の値に戻しています。**変数の初期化は `start()` で行う**習慣をつけておくと、あとの章で困りません。

## ⑥ 確認問題

**問1**　User Program モードに入ってから5秒間で、`start()`・`update()`・`update_slow()` はそれぞれ何回くらい動きますか。

:::details 答え
`start()` は1回、`update()` は約300回（60回 × 5秒）、`update_slow()` は5回です。`update_slow()` は最初のコマ（約0秒）と、そのあと約1秒・2秒・3秒・4秒のときに動きます。次は約5.02秒なので、5秒間には入りません。
:::

**問2**　次のプログラムを実行すると、何と表示されますか。

```python
x = 7
print(f"{x} の2乗は {x * x}、半分は {x / 2}")
```

:::details 答え
`7 の2乗は 49、半分は 3.5` と表示されます。
:::

**問3**　`update_slow()` を1秒に1回ではなく、0.5秒に1回動かしたくなりました。RACECAR のライブラリには、`update_slow()` の間隔を変える `rc.set_update_slow_time(秒数)` という命令があります。この命令を、3つの関数のどこに書けばよいですか。また、Lab A の Part 5 の表示はどう変わりますか。

:::details 答え
`start()` の中に `rc.set_update_slow_time(0.5)` と書きます。表示は `0.0`、`0.5`、`1.0`、`1.5`、`2.0`……のように、0.5秒ごとになります。`update()` の中に書くと、1秒に60回も同じ設定をし直すことになり、むだが多くなります。
:::

**問4（発展）**　Part 5 の表示を `1.0 seconds` ではなく `1 seconds` のように整数で表示するには、どう書き換えればよいでしょうか。

:::details 答え
`round(counter)` のように、桁数を指定せずに `round` を使うと整数に丸められます。`int(counter)` を使う方法もありますが、こちらは小数点以下を切り捨てるので、1.99秒は `1` になります。
:::

## ⑦ 原典

- **Lab A - Printing Statements**（`labs/lab_a/lab_a.py`）と `template.py`：[racecar-neo-prereq-labs](https://github.com/MITRacecarNeo/racecar-neo-prereq-labs)（MIT License）
- `start()`・`update()`・`update_slow()` の呼ばれ方：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `racecar_core.py` と `simulation/racecar_core_sim.py`（GPL-3.0）

実行結果は、ライブラリと同じ手順で `start()`・`update()`・`update_slow()` を呼ぶプログラムで確かめたものです。実際のシミュレータでは1コマの長さが毎回少しずつ変わるため、Part 4 の数字は多少異なります。

:::details 原典のライセンス（MIT License）
この回のコードは、次のライセンスのもとで公開されている原典のプログラムをもとにしています。

```text
MIT License

Copyright (c) 2024 MITRacecarNeo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
:::
