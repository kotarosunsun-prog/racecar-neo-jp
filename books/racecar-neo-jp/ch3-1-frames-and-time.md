---
title: "3-1 フレームと時間"
free: true
---

「1秒まっすぐ進んでから、右に曲がる」。人に頼むなら、これで十分です。ところがロボットのプログラムでは、この「1秒」をどう書くかに、大事な考え方が隠れています。この回では、RACECAR のプログラムの土台になっている**考え方の型**（パラダイム）と、時間の扱い方を学びます。

## ① この回でできるようになること

1. 「上から順に書いて待つ」書き方と「毎コマ判断する」書き方の違いを説明できる
2. 経過時間を使って、「いつ」「どのくらいの間」動くかを決められる
3. 一定の間隔でくり返すタイマーを書ける

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Programming paradigm | プログラミング・パラダイム | プログラムを組み立てるときの、考え方の型 |
| Frame | フレーム（コマ） | 画面や状態を1回更新する単位 |
| Frame rate | フレームレート | 1秒あたりのコマの数。RACECAR は約60 |
| Delta time | 経過時間（デルタタイム） | 前のコマから今のコマまでにかかった時間 |
| Blocking | ブロッキング | 何かが終わるまで、その場で止まって待つこと |
| Timer | タイマー | 時間をはかって、決まった時刻に何かをするしくみ |
| Timeline | タイムライン | 時間の順に並べた「することの予定表」 |

## ③ 本文

### 2つの書き方

「1秒まっすぐ進み、1秒右に曲がって、止まる」をプログラムにするとき、まず思いつくのは、次のように上から順に書き、`time.sleep()`（指定した秒数だけ待つ命令）で時間をはかる方法です。

```python
rc.drive.set_speed_angle(1, 0)   # まっすぐ進む
time.sleep(1)                    # 1秒待つ
rc.drive.set_speed_angle(1, 1)   # 右に曲がる
time.sleep(1)                    # 1秒待つ
rc.drive.stop()                  # 止まる
```

読みやすいのですが、ロボットではうまくいきません。`time.sleep(1)` の1秒間、プログラムは**完全に止まっている**からです。

![2つの書き方の比較。左は、命令と time.sleep を上から順に並べた書き方で、待っている間はセンサもボタンも読めない。右は RACECAR の書き方で、start のあと、update が1コマに1回、経過時間を足し、センサやボタンを読み、今どう動くかを決め、命令を送ることをくり返す](/images/racecar-neo-jp/3-1/fig1-paradigm.png)
*図1　上から順に書いて待つ書き方と、毎コマ判断する書き方*

- 待っている間に前に壁が現れても、センサを読めないので気づけません
- 途中でボタンを押しても、反応できません
- RACECAR のシミュレータは `update()` が終わるのを待ってから次のコマに進むので、`update()` の中で `sleep` すると、**シミュレータの画面そのものが固まります**

そこで RACECAR では、図1の右のように考えます。

- **くり返しは、ライブラリに任せる。** `rc.go()` が、`update()` を1秒に約60回呼び続けます
- **あなたは「1コマ分」だけを書く。** `update()` の中では、「今の時間、今の様子なら、どう動くか」を決めて命令を送り、**すぐに終わる**

この「毎コマ、状況を見て判断し直す」考え方が、RACECAR の**プログラミング・パラダイム**です。ゲームも同じ考え方で作られていて、画面を1コマ描くたびに、キャラクターの位置や当たり判定を計算し直しています。

### 時間は「経過時間を足して」はかる

1-3 の Lab A で、経過時間を `counter` に足していったことを思い出しましょう。

```python
counter += rc.get_delta_time()
```

`rc.get_delta_time()` は、前のコマから今のコマまでにかかった時間（秒）を返します。理想的には 1/60 秒ですが、計算が重いときなどは、1コマが長くなることがあります。

「60コマ数えたら1秒」という数え方をすると、1コマが長くなったときに時間がずれます。たとえば1コマに 1/30 秒かかる状態が続くと、60コマ数えたときには2秒たっています。**毎コマ、実際にかかった時間を足していけば**、コマの長さが変わっても、正しい時間がわかります。

### 経過時間で、することを切り替える

時間がわかれば、「何秒から何秒までは何をする」という**タイムライン**を、if・elif で書けます。

```python
if counter < 1:
    rc.drive.set_speed_angle(1, 0)   # 0〜1秒：まっすぐ
elif counter < 2:
    rc.drive.set_speed_angle(1, 1)   # 1〜2秒：右に曲がる
else:
    rc.drive.stop()                  # 2秒から：止まる
```

これが `update()` の中で毎コマ実行されます。1秒未満のうちは毎コマ「まっすぐ」を、1秒を過ぎると毎コマ「右」を選びます。`sleep` と違って、プログラムは一度も止まりません。1-2 で動かした `demo.py` の B ボタンの動きは、この書き方で作られています。

### やってみよう：カウントダウンしてから走る

A ボタンを押すと「3・2・1・GO!」と1秒ごとに表示し、GO! のあと2秒まっすぐ進み、1秒右に曲がって止まるプログラムです。

![A ボタンを押してからの時間の流れ。0〜3秒は止まったままカウントダウンし、0秒で3、1秒で2、2秒で1、3秒で GO! と表示する。3〜5秒はまっすぐ進み、5〜6秒は右に曲がり、6秒で止まる](/images/racecar-neo-jp/3-1/fig2-countdown.png)
*図2　カウントダウンのプログラムのタイムライン*

```python:countdown.py
import racecar_core

rc = racecar_core.create_racecar()

timer = 0.0        # A ボタンを押してからの時間（秒）
running = False    # タイムラインを実行中かどうか（フラグ）


def start():
    global timer, running
    timer = 0.0
    running = False
    rc.drive.stop()


def update():
    global timer, running

    if rc.controller.was_pressed(rc.controller.Button.A):
        timer = 0.0
        running = True
        print("3")

    if running:
        before = timer
        timer += rc.get_delta_time()

        # カウントダウン：その時刻を「またいだ」コマで、1回だけ表示する
        if before < 1 <= timer:
            print("2")
        if before < 2 <= timer:
            print("1")
        if before < 3 <= timer:
            print("GO!")

        # タイムライン：経過時間によって、することを切り替える
        if timer < 3:
            rc.drive.stop()                  # カウントダウン中は止まっておく
        elif timer < 5:
            rc.drive.set_speed_angle(1, 0)   # 2秒間まっすぐ進む
        elif timer < 6:
            rc.drive.set_speed_angle(1, 1)   # 1秒間右に曲がる
        else:
            rc.drive.stop()
            running = False
            print("おしまい")


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
```

ポイントは3つです。

- **フラグ `running`**（2-2 のトグルと同じ考え方）で、「今タイムラインを実行中か」を覚えておきます。A を押すまでは何もしません
- **`timer` は A を押したときに 0 に戻します。** こうすると「A を押してから何秒」がはかれます
- **カウントダウンの表示は「またいだ」コマで出します。** `before < 1 <= timer` は「足す前は1秒より前で、足したあとは1秒以上」という意味で、Python ではこのように比べる式をつなげて書けます。ちょうど1秒を過ぎたコマで、1回だけ `True` になります

User Program モードで A（キーボードの 1）を押すと、ターミナルに `3`・`2`・`1`・`GO!`・`おしまい` が順に表示され、車が動きます。

:::message
このプログラムの車の動きは、第4章の Lab D「命令を並べて図形を走る」で使う書き方そのものです。
:::

### 一定の間隔でくり返す：タイマー

「0.5秒ごとに何かをする」には、自分でタイマー用の変数を用意します。

```python:blink.py
import racecar_core

rc = racecar_core.create_racecar()

blink_timer = 0.0


def start():
    global blink_timer
    blink_timer = 0.0


def update():
    global blink_timer
    blink_timer += rc.get_delta_time()
    if blink_timer >= 0.5:
        blink_timer -= 0.5       # 0 に戻すのではなく、0.5 を引く
        print("ピッ")


if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
```

0.5秒たつたびに `ピッ` と表示されます。

`blink_timer = 0` と0に戻さずに `0.5` を引いているのには理由があります。0.5秒ちょうどのコマはまずないので、気づいたときには 0.51秒のように少し過ぎています。0に戻すと、この 0.01秒の「過ぎた分」が毎回捨てられ、くり返すうちに間隔が少しずつ長くなってしまいます。0.5 を引けば過ぎた分が次に持ち越されるので、長く動かしてもずれません。

なお、1秒に1回くり返すだけなら、1-3 で使った `update_slow()` と `rc.set_update_slow_time()` でもできます。いくつもの違う間隔を同時に使いたいときは、この回のように自分でタイマーを作ります。

## ⑤ つまずきポイント

### `time.sleep()` を使ってしまった

`update()` の中で `time.sleep()` を使うと、そのあいだシミュレータが固まります。RACECAR の旧版のドキュメントでも、`sleep()` は使わないようにと書かれています。「待つ」代わりに、経過時間を足して、if で切り替えましょう。

### `counter == 1` が一度も成り立たない

経過時間は `0.0166…` ずつ増えるので、**ちょうど 1.0 になるコマはまずありません**。1-3 で見たように、小数の計算には小さな誤差も入ります。時間を比べるときは `==` ではなく、`<`・`>=` や、「またいだ」ことを調べる `before < 1 <= timer` を使います。

### ボタンを押してからの時間をはかりたいのに、最初からの時間になっている

ボタンを押したときに、タイマーの変数を `0.0` に戻すのを忘れていないか確かめましょう。カウントダウンのプログラムでは、`was_pressed` の if の中で `timer = 0.0` としています。

### update() の中の処理が重くて、コマが遅くなった

1コマの処理に時間がかかると、1秒あたりのコマの数が減り、車の反応も遅れます。`update()` の中で大きなくり返しや、たくさんの `print` をしないようにしましょう。

## ⑥ 確認問題

**問1**　ある時間、計算が重くなり、1コマに 1/30 秒かかるようになりました。この状態で「60コマ数えたら1秒」という数え方をすると、実際には何秒たっていますか。また、正しく1秒をはかるにはどうすればよいですか。

:::details 答え
$60 \times \frac{1}{30} = 2$ 秒たっています。コマを数えるのではなく、`rc.get_delta_time()` で毎コマ実際にかかった時間を足していけば、コマの長さが変わっても正しくはかれます。
:::

**問2**　カウントダウンのプログラムを書きかえて、GO! のあと「1秒まっすぐ・1秒左に曲がる・1秒まっすぐ」と走って止まるようにしましょう。タイムラインの if・elif の部分だけを書けば十分です。

:::details 答えの例
```python
if timer < 3:
    rc.drive.stop()
elif timer < 4:
    rc.drive.set_speed_angle(1, 0)    # まっすぐ
elif timer < 5:
    rc.drive.set_speed_angle(1, -1)   # 左に曲がる（角度をマイナスにする）
elif timer < 6:
    rc.drive.set_speed_angle(1, 0)    # まっすぐ
else:
    rc.drive.stop()
    running = False
    print("おしまい")
```
左に曲がるには、角度を `-1` にします。`set_speed_angle` の詳しい使い方は 3-2 で学びます。
:::

**問3**　`blink.py` を書きかえて、0.5秒ごとに `ピッ`、2秒ごとに `ポーン` と表示するようにしましょう。

:::details 答えの例
```python
blink_timer = 0.0
long_timer = 0.0


def update():
    global blink_timer, long_timer
    dt = rc.get_delta_time()
    blink_timer += dt
    long_timer += dt

    if blink_timer >= 0.5:
        blink_timer -= 0.5
        print("ピッ")
    if long_timer >= 2.0:
        long_timer -= 2.0
        print("ポーン")
```
タイマーごとに変数を分けるのがポイントです。`rc.get_delta_time()` はいったん変数 `dt` に入れて、2つのタイマーに同じ値を足しています。`start()` の中でも、2つの変数を 0.0 に戻しておきましょう。
:::

## ⑦ 原典

- BWSI オンライン事前コース 第3章「プログラミング・パラダイム」（[BWSIx](https://learn.bwsix.edly.io/course/autonomous-racecar-2026/)、英語）
- `demo.py` の、経過時間で動きを切り替える書き方：[racecar-neo-prereq-labs](https://github.com/MITRacecarNeo/racecar-neo-prereq-labs)（MIT License）
- `update()` が終わるまでシミュレータが待つしくみ：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の README（Python Interface）
- `sleep()` を使わないという注意：旧版 RACECAR-MN のドキュメント「[Connecting a Python Program](https://mitll-racecar-mn.readthedocs.io/en/latest/simulation/python.html)」

この回のプログラムは、ライブラリと同じ順番で `start()` と `update()` を呼び、ボタンの押し方を決めて1コマずつ動かすプログラムで確かめたものです。
