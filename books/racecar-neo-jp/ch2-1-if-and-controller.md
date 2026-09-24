---
title: "2-1 if 文でコントローラに反応する（Lab B 前半）"
free: true
---

ロボットの「考える」の中心にあるのは、「**もし〇〇なら、△△する**」という判断です。この回では、Python の if 文と、RACECAR のコントローラ（キーボード）の読み取り方を学びます。課題は、オンライン事前コースの **Lab B**「コントローラを使って文字を表示する（Printing Statements Using Controller）」の前半です。

## ① この回でできるようになること

1. if・elif・else を使って、条件によって違う処理をさせられる
2. 「ポーリング」とは何か、ロボットがなぜポーリングを使うのかを説明できる
3. `rc.controller` を使って、ボタン・トリガー・スティックの状態を読める

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Decision making | 意思決定 | 状況を見て、次に何をするかを決めること |
| Conditional statement | 条件文（if 文） | 条件が成り立つときだけ実行する文 |
| Boolean | 真偽値 | `True`（正しい）か `False`（正しくない）のどちらかの値 |
| Comparison operator | 比較演算子 | `==` や `<` のように、2つの値を比べる記号 |
| Polling | ポーリング | 状態を、こちらから定期的に問い合わせて確かめること |
| Controller | コントローラ | ゲームパッド。シミュレータではキーボードで代用できる |
| Trigger | トリガー | コントローラの奥にある、押し込み具合を測れるボタン |
| Joystick | スティック | 倒した向きと量を測れるレバー |

## ③ 本文

### ロボットの意思決定は if 文から

「前の壁が近ければ止まる」「信号が赤なら止まる」「A ボタンが押されたらあいさつする」。ロボットの判断は、どれも**条件**と**そのときの行動**の組み合わせです。Python では、これを if 文で書きます。

```python
distance = 30

if distance < 50:
    print("近い！止まる")
elif distance < 100:
    print("少し近い。ゆっくり進む")
else:
    print("遠い。進む")
```

- `if 条件:` の条件が正しければ、その下の字下げされた行を実行します
- そうでなければ `elif 条件:`（else if の略）を上から順に調べます。いくつ書いてもかまいません
- どれにも当てはまらなければ `else:` の下を実行します
- **上から順に調べて、最初に当てはまった1か所だけ**が実行されます。上の例では `distance < 50` が正しいので、`distance < 100` も正しいのに「少し近い」は表示されません

### 条件の書き方

条件は、正しいか正しくないか、つまり `True` か `False` になる式です。

| 書き方 | 意味 | 例（x = 3 のとき） |
|---|---|---|
| `x == 3` | 等しい | `True` |
| `x != 3` | 等しくない | `False` |
| `x < 5` / `x > 5` | より小さい／より大きい | `True` / `False` |
| `x <= 3` / `x >= 4` | 以下／以上 | `True` / `False` |
| `a and b` | a も b も正しい | `x > 0 and x < 5` は `True` |
| `a or b` | a か b のどちらかが正しい | `x < 0 or x == 3` は `True` |
| `not a` | a が正しくない | `not x == 3` は `False` |

**「等しい」は `=` ではなく `==`** です。`=` は「右の値を左の変数に入れる」という別の意味です。

### ポーリング：こちらから何度も聞きにいく

ボタンが押されたかどうかを知る方法は、大きく2つあります。

1. **待つ**：ボタンが押されるまで、その場で止まって待つ
2. **聞きにいく**：何か別のことをしながら、ときどき「今、押されている？」と確かめる

2つめを**ポーリング**（polling）と呼びます。「世論調査（poll）」と同じ語源で、「こちらから問い合わせる」という意味です。

ふつうの Python のプログラムで使う `input()` は、1つめの「待つ」やり方です。

```python
name = input("名前は？ ")    # キーボードで入力されるまで、ここで止まる
```

ロボットでこれをしてはいけません。1-1 で学んだとおり、**世界は待ってくれない**からです。ボタンを待っている間は、センサも読めず、ハンドルも切れません。シミュレータは `update()` が終わるのを待ってから次のコマに進むので、`update()` の中で止まると、シミュレータ全体が固まってしまいます。

そこで RACECAR では、**毎コマ `update()` の中でボタンの状態を聞きにいく**、つまりポーリングを使います。1秒に約60回確かめるので、人がボタンを押したことは、ほとんど遅れなく気づけます。

:::message
**ポーリングの中身**
シミュレータでは、`rc.controller.is_down(...)` などを呼ぶたびに、プログラムからシミュレータへ「このボタンは押されている？」という問い合わせが、ネットワークで送られます。答えはそのコマの間だけ覚えておかれるので、同じコマの中で何度呼んでも、同じ答えが返ります。
:::

### RACECAR のコントローラを読む

コントローラの状態は、`rc.controller` を通して読みます。

| 命令 | 返す値 | 何がわかるか |
|---|---|---|
| `rc.controller.is_down(ボタン)` | `True` / `False` | そのボタンを**今押しているか** |
| `rc.controller.was_pressed(ボタン)` | `True` / `False` | そのボタンが**このコマで押されたか**（押した瞬間） |
| `rc.controller.was_released(ボタン)` | `True` / `False` | そのボタンが**このコマで離されたか**（離した瞬間） |
| `rc.controller.get_trigger(トリガー)` | 0.0 〜 1.0 | トリガーをどれだけ押し込んでいるか |
| `rc.controller.get_joystick(スティック)` | (x, y)、それぞれ −1.0 〜 1.0 | スティックを倒した向きと量 |

ボタンは `rc.controller.Button.A` のように、名前で指定します。

| 書き方 | ボタン | キーボード |
|---|---|---|
| `rc.controller.Button.A` / `.B` / `.X` / `.Y` | A / B / X / Y | 1 / 2 / 3 / 4 |
| `rc.controller.Button.LB` / `.RB` | 左バンパー / 右バンパー | Z / /（スラッシュ） |
| `rc.controller.Button.LJOY` / `.RJOY` | スティックの押し込み | 5 / 6 |
| `rc.controller.Trigger.LEFT` / `.RIGHT` | 左トリガー / 右トリガー | 左 Shift / 右 Shift |
| `rc.controller.Joystick.LEFT` / `.RIGHT` | 左スティック / 右スティック | W・A・S・D / 矢印キー |

START ボタン（Enter）と BACK ボタン（Backspace）は、シミュレータのモードの切り替えに使われるので、プログラムからは読めません。

`is_down`・`was_pressed`・`was_released` の3つの違いは、次の 2-2 で詳しく見ます。この回では、`was_pressed`（押した瞬間）だけを使います。

### Lab B をやってみよう（Part 1・2）

課題のファイルは、labs フォルダの中の `lab_b/lab_b.py` です。Lab B では、`update()` の中でボタンの状態を調べて、押されたボタンによって違う文字を表示します。

課題のゴールは次の4つです（原典の Expected Outcome より）。この回では、準備の Part 1 と、1つめの Part 2 に取り組みます。

- **A** ボタンを押したら、`Hello World!` を1回表示する（Part 2）
- **B** ボタンを離したら、`Welcome to RACECAR <自分の名前>!` を1回表示する（Part 3、2-2）
- **X** ボタンを押したら、経過時間を表示する。**押し続けている間は表示し続ける**（Part 4、2-2）
- **Y** ボタンを押したら、経過時間を表示する。**押し続けても1回だけ**（Part 5、2-2）

#### Part 1：start() で名前を決める

`start()` の中で、変数 `your_name` に自分の名前を入れ、`Hello 〇〇, welcome to RACECAR!` と表示します。1-3 の Lab A とほとんど同じです。

:::message alert
**訳注：Part 1 の指示とひな形が食い違っている**
原典のコメントは「`Hello {your name}, welcome to RACECAR!` と表示せよ」と指示していますが、その下のひな形の行は `print(f"Welcome {_____}, welcome to RACECAR!")` と、先頭が `Welcome` になっています。コメントの指示に合わせて `Hello` にすれば問題ありません。
:::

:::details 答えの例（Part 1）
```python
def start():
    global your_name
    your_name = "Taro"
    print(f"Hello {your_name}, welcome to RACECAR!")
```
`your_name` は、あとで `update()` の中（Part 3）でも使います。そのため `start()` の最初に `global your_name` と書いて、関数の外の変数に入れています。
:::

#### Part 2：A ボタンを押したら表示する

`update()` の中には、次の if 文がすでに書いてあります。

```python
if rc.controller.was_pressed(rc.controller.Button.A):
    print("_____")
```

「A ボタンがこのコマで押されたなら」という条件です。`_____` を `Hello World!` に書き換えましょう。

:::details 答えの例（Part 2）
```python
if rc.controller.was_pressed(rc.controller.Button.A):
    print("Hello World!")
```
:::

ここまでで一度実行してみます。

```bash
racecar cd
cd lab_b
racecar sim lab_b.py
```

User Program モードに入ると、まず名前入りのあいさつが1回表示されます。そのあと **1** キーを押すたびに、`Hello World!` が1回ずつ表示されれば成功です。キーを押したままにしても、表示は1回だけです。なぜ1回だけなのかは、次の 2-2 で説明します。

:::message
Part 3〜5 の if 文にはまだ `_____` が残っているので、このままではエラーで止まります。先に Part 2 だけを試したいときは、Part 3・4 の if 文を、**その下の print の行も含めて**、行の先頭に `#` を付けてコメントにしておきましょう。if の行だけをコメントにすると、残った print の行が、字下げの深さが同じ Part 2 の if の中身だと解釈されます。その結果、A ボタンを押したときに `NameError: name '_____' is not defined` というエラーで止まります。
:::

## ⑤ つまずきポイント

### `==` のつもりで `=` と書いた

```python
if x = 3:
```

と書くと、`SyntaxError: invalid syntax` というエラーになります。比べるときは `==` です。

### if の行の最後の `:` を忘れた

`if x == 3` のように行の最後の `:`（コロン）を忘れても、同じ `SyntaxError: invalid syntax` になります。エラーが出た行の、行末を確かめてください。

### ボタンの名前を小文字で書いた

`rc.controller.Button.a` のように小文字で書くと、`AttributeError: a` というエラーになります。ボタンの名前は大文字で `Button.A` と書きます。

### elif の順番で、思ったとおりに動かない

if・elif は、上から順に調べて**最初に当てはまった1か所だけ**を実行します。「両方押されているとき」のような、より細かい条件は上に書きます（問3）。

## ⑥ 確認問題

**問1**　`speed = 0.7` のとき、次のプログラムは何と表示しますか。

```python
if speed > 0.9:
    print("速すぎる")
elif speed > 0.5:
    print("ちょうどよい")
elif speed > 0:
    print("ゆっくり")
else:
    print("止まっている")
```

:::details 答え
`ちょうどよい` と表示されます。`speed > 0` も正しいのですが、その前の `speed > 0.5` で当てはまった時点で、残りは調べられません。
:::

**問2**　ボタンを待つのに `input()` を使ってはいけないのはなぜですか。1-1 の「ロボットのプログラミングが難しい理由」と結びつけて説明しましょう。

:::details 答え
`input()` は入力があるまでプログラムを止めてしまうからです。ロボットは待っている間も動き続けているので、その間センサを読んだりハンドルを切ったりできないと危険です。RACECAR のシミュレータでは、`update()` が止まるとシミュレータ全体も止まってしまいます。
:::

**問3**　左バンパー（LB）だけを押しているときは「左」、右バンパー（RB）だけのときは「右」、両方押しているときは「両方」と、押している間ずっと表示するプログラムを、`update()` の中に書きましょう。`is_down` を使います。

:::details 答えの例
```python
def update():
    lb = rc.controller.is_down(rc.controller.Button.LB)
    rb = rc.controller.is_down(rc.controller.Button.RB)

    if lb and rb:
        print("両方")
    elif lb:
        print("左")
    elif rb:
        print("右")
```
「両方」の条件を一番上に書くのがポイントです。`elif lb:` を先に書くと、両方押しているときも「左」になってしまいます。ボタンの状態をいったん変数 `lb`・`rb` に入れておくと、条件が読みやすくなります。
:::

## ⑦ 原典

- **Lab B - Printing Statements Using Controller**（`labs/lab_b/lab_b.py`）：[racecar-neo-prereq-labs](https://github.com/MITRacecarNeo/racecar-neo-prereq-labs)（MIT License。ライセンスの全文は 1-3 の最後に載せています）
- コントローラの API：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `controller.py` と `simulation/controller_sim.py`（GPL-3.0）
- BWSI オンライン事前コース 第2章「意思決定とデータのポーリング」（[BWSIx](https://learn.bwsix.edly.io/course/autonomous-racecar-2026/)、英語）
