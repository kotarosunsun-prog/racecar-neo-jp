---
title: "2-2 「押した瞬間」と「押している間」（Lab B 後半）"
free: true
---

2-1 で、A ボタンを押したままにしても `Hello World!` が1回しか表示されないことを確かめました。この回では、その理由と、ボタンの状態を読む3つの命令の使い分けを学びます。Lab B の Part 3〜5 に取り組み、Lab B を完成させます。

## ① この回でできるようになること

1. `is_down`・`was_pressed`・`was_released` が、どのコマで `True` になるかを説明できる
2. 「押している間ずっと」「押した瞬間だけ」「離した瞬間だけ」を、正しい命令で書き分けられる
3. ボタンで状態を切り替える「トグル」を書ける

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| is down | 押されている | 今この瞬間、ボタンが押しこまれている状態 |
| was pressed | 押された | このコマで、離していた状態から押した状態に変わった |
| was released | 離された | このコマで、押していた状態から離した状態に変わった |
| Held down | 押し続ける | ボタンを押したままにすること |
| Toggle | トグル | 押すたびに、オンとオフを切り替えること |
| Flag | フラグ | オンかオフかを覚えておくための変数（`True` / `False`） |

## ③ 本文

### 3つの命令は、どのコマで True になるか

1-3 で学んだとおり、`update()` は1秒に約60回、1コマごとに呼ばれます。人がボタンを「ちょっと押す」だけでも、そのあいだに何コマも進みます。3つの命令が、それぞれどのコマで `True` になるかを並べると、図1のようになります。

![キーを3〜8コマ目に押していたとき、is_down は3〜8コマ目がすべて True、was_pressed は押し始めた3コマ目だけ True、was_released は離した直後の9コマ目だけ True になることを示す図](/images/racecar-neo-jp/2-2/fig1-button-timing.png)
*図1　ボタンを6コマのあいだ押したときの、3つの命令の値*

| 命令 | True になるコマ | 図1の例 | 向いている使い方 |
|---|---|---|---|
| `is_down` | 押しているあいだ、**毎コマ** | 3〜8コマ目の6回 | アクセルのように、押している間ずっと効かせたいもの |
| `was_pressed` | 押しはじめた**1コマだけ** | 3コマ目の1回 | モードの切り替えのように、1回押したら1回だけ起こしたいもの |
| `was_released` | 離した直後の**1コマだけ** | 9コマ目の1回 | 押している長さを測ったあとで何かするもの |

2-1 で A ボタンを押したままにしても1回しか表示されなかったのは、`was_pressed` を使っていたからです。もし `is_down` を使っていたら、押している間じゅう、1秒に約60回 `Hello World!` が表示されます。

### Lab B をやってみよう（Part 3〜5）

#### Part 3：B ボタンを離したら表示する

B ボタンを**離した**ときに、`Welcome to RACECAR 〇〇!` と1回表示します。`〇〇` には、Part 1 で決めた `your_name` を f 文字列で埋め込みます。

ひな形の `rc.controller._____(rc.controller.Button._)` の2か所の空欄に、何を入れればよいか考えましょう。

:::details 答えの例（Part 3）
```python
if rc.controller.was_released(rc.controller.Button.B):
    print(f"Welcome to RACECAR {your_name}!")
```
:::

#### Part 4：X ボタンを押している間、経過時間を表示し続ける

X ボタンを押している間ずっと、`The current script has been running for 〇〇 seconds!` と表示します。経過時間は、Lab A と同じ変数 `counter` に入っています。**小数第2位まで丸める**ことも忘れずに。

:::details 答えの例（Part 4）
```python
if rc.controller.is_down(rc.controller.Button.X):
    print(f"The current script has been running for {round(counter, 2)} seconds!")
```
押している間ずっと表示したいので `is_down` を使います。1秒押すと、約60行表示されます。
:::

#### Part 5：Y ボタンを押したら、経過時間を1回だけ表示する

Part 5 は、if 文を**まるごと自分で書きます**。Y ボタンを押したら、Part 4 と同じ文を表示します。ただし、押し続けても**1回だけ**です。

:::details 答えの例（Part 5）
```python
if rc.controller.was_pressed(rc.controller.Button.Y):
    print(f"The current script has been running for {round(counter, 2)} seconds!")
```
押し続けても1回だけにしたいので `was_pressed` を使います。
:::

#### 実行結果

A を軽く押し、B を押して離し、X を少しだけ押し、Y を1秒ほど押し続けると、ターミナルは次のようになります。

```text
Hello Taro, welcome to RACECAR!
Hello World!
Welcome to RACECAR Taro!
The current script has been running for 1.67 seconds!
The current script has been running for 1.68 seconds!
The current script has been running for 1.7 seconds!
The current script has been running for 1.72 seconds!
The current script has been running for 1.73 seconds!
The current script has been running for 2.33 seconds!
```

- `Welcome to RACECAR Taro!` は、B を押したときではなく**離したとき**に出ます
- X は5コマほど押していたので、5行表示されています
- 最後の1行は Y です。1秒押し続けても、1行だけです

時間の数字は、キーを押したタイミングによって変わります。

## ④ 数式・コード

### Lab B の完成例

:::details lab_b.py の update() の完成例
```python
def update():
    global counter
    counter += rc.get_delta_time()

    # Part 2：A を押した瞬間に1回
    if rc.controller.was_pressed(rc.controller.Button.A):
        print("Hello World!")

    # Part 3：B を離した瞬間に1回
    if rc.controller.was_released(rc.controller.Button.B):
        print(f"Welcome to RACECAR {your_name}!")

    # Part 4：X を押している間ずっと
    if rc.controller.is_down(rc.controller.Button.X):
        print(f"The current script has been running for {round(counter, 2)} seconds!")

    # Part 5：Y を押した瞬間に1回
    if rc.controller.was_pressed(rc.controller.Button.Y):
        print(f"The current script has been running for {round(counter, 2)} seconds!")
```
ここでは if・elif ではなく、**独立した if 文を4つ**並べています。同じコマで A と X を同時に押したときも、両方の表示を出すためです。
:::

### 発展：トグルでモードを切り替える

`was_pressed` のいちばん大事な使い道が、**トグル**です。押すたびにオンとオフが入れ替わるスイッチを、`True` / `False` を覚えておく変数（フラグ）で作ります。

```python:toggle.py
import racecar_core

rc = racecar_core.create_racecar()

is_on = False      # フラグ：今オンかどうか


def start():
    global is_on
    is_on = False  # User Program モードに入るたびにオフから始める


def update():
    global is_on
    if rc.controller.was_pressed(rc.controller.Button.A):
        is_on = not is_on          # True と False を入れ替える
        print("オン" if is_on else "オフ")  # is_on が True なら「オン」、そうでなければ「オフ」


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
```

`not is_on` は、`is_on` が `True` なら `False`、`False` なら `True` になります。ここで `is_down` を使うと、押しているあいだ毎コマ入れ替わってしまい、オンとオフが1秒に約60回点滅します。**1回押したら1回だけ切り替える**には、`was_pressed` が必要です。

1-2 で動かした `demo.py` も、B ボタンを押したら `isDriving` というフラグを `True` にして、車を走らせはじめています。フラグで「今どの状態か」を覚えておく考え方は、第7章のステートマシンにつながります。

## ⑤ つまずきポイント

### update_slow() の中で was_pressed を使うと、押しても気づかない

`was_pressed` が `True` になるのは、押しはじめた**1コマだけ**です。1秒に1回しか呼ばれない `update_slow()` の中で調べると、そのコマにちょうど当たらない限り、`True` を見ることができません。

ボタンを読むのは `update()` の中で行います。`update_slow()` でボタンを確かめたいときは、`is_down` を使います。1-2 の `demo.py` の `update_slow()` が、右バンパーを `is_down` で調べているのはこのためです。

### round で小数第2位まで丸めたのに、1.7 と表示された

`round(1.7, 2)` の結果は `1.7` です。`round` は値を丸めるだけで、「小数第2位まで必ず表示する」わけではありません。表示の桁数をそろえたいときは、f 文字列の書式指定を使います。

```python
print(f"{counter:.2f}")    # 1.70 のように、小数第2位まで必ず表示する
```

### 押したのに反応しない

キーボードの入力は、選ばれているウィンドウにしか届きません。ターミナルを触ったあとは、シミュレータの画面を一度クリックしてからキーを押してください（1-2 のつまずきポイントと同じです）。

## ⑥ 確認問題

**問1**　次の動きをさせたいとき、`is_down`・`was_pressed`・`was_released` のどれを使いますか。

(1) 右トリガーの代わりに、Y ボタンを押している間だけ前に進む
(2) X ボタンを押すたびに、ライトのオンとオフを切り替える
(3) B ボタンを押してから離すまでの時間を測り、離したときに表示する

:::details 答え
(1) `is_down`　(2) `was_pressed`　(3) 押しはじめを `was_pressed` で、離したときを `was_released` で調べます。押しはじめたときの `counter` を変数に覚えておき、離したときの `counter` との差を表示します。
:::

**問2**　Lab B を実行して、X ボタンを2秒間押し続けました。Part 4 の行は、およそ何行表示されますか。

:::details 答え
約120行です。`update()` は1秒に約60回呼ばれ、押している間は毎回 `is_down` が `True` になるからです。
:::

**問3**　問1の(3)を実際に書いてみましょう。B ボタンを押してから離すまでの時間を、`Pressed for 〇〇 seconds` と小数第2位まで表示します。

:::details 答えの例
```python
counter = 0
press_time = 0


def update():
    global counter, press_time
    counter += rc.get_delta_time()

    if rc.controller.was_pressed(rc.controller.Button.B):
        press_time = counter                 # 押しはじめた時刻を覚えておく

    if rc.controller.was_released(rc.controller.Button.B):
        print(f"Pressed for {counter - press_time:.2f} seconds")
```
`global` のあとにカンマで区切って、2つの変数をまとめて書けます。
:::

## ⑦ 原典

- **Lab B - Printing Statements Using Controller**（`labs/lab_b/lab_b.py`）と `demo.py`：[racecar-neo-prereq-labs](https://github.com/MITRacecarNeo/racecar-neo-prereq-labs)（MIT License）
- 3つの命令の定義：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `controller.py`（GPL-3.0）。シミュレータ側では、Unity の「押している」「押した」「離した」の判定がそのまま使われています（[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `Controller.cs`）

実行結果は、ボタンを押す順番を決めて、1コマずつ `update()` を呼ぶプログラムで確かめたものです。
