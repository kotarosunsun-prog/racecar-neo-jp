---
title: "3-2 手動で操縦する（Lab C）"
free: true
---

いよいよ、自分のプログラムで車を運転します。この回の課題は、オンライン事前コースの **Lab C**「RACECAR のコントローラ（RACECAR Controller）」です。トリガーでアクセル、スティックでハンドルを操作する、手動運転のプログラムを自分で書きます。

## ① この回でできるようになること

1. `rc.drive.set_speed_angle()` で、車の速さとハンドルの角度を決められる
2. トリガーとスティックの値から、速さと角度を計算して車に送れる
3. 値が決められた範囲からはみ出さないように、プログラムで押さえこめる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Throttle | スロットル（アクセル） | 後輪を回す力の強さ |
| Steering angle | 舵角（だかく） | 前輪を左右に切る角度 |
| Teleoperation | 遠隔操縦 | 人がコントローラで、離れたところからロボットを動かすこと |
| Offset | オフセット（ここでは調整量） | ボタンで上げ下げする、速さや角度の強さ |
| Threshold | しきい値 | 「これより大きければ」と判断するための境目の値 |
| Clamp | クランプ（範囲に収める） | 値が上限・下限をはみ出さないように押さえこむこと |

## ③ 本文

### 車を動かす命令：set_speed_angle

車に「どれくらいの強さで進み、どれくらいハンドルを切るか」を伝えるのが `rc.drive.set_speed_angle()` です。

```python
rc.drive.set_speed_angle(speed, angle)
```

| 引数 | 範囲 | 意味 |
|---|---|---|
| `speed` | −1.0 〜 1.0 | 後輪を回す強さ。1.0 で前に全開、−1.0 で後ろに全開、0 で止まる |
| `angle` | −1.0 〜 1.0 | 前輪の向き。−1.0 で左いっぱい、1.0 で右いっぱい、0 でまっすぐ |

- `speed` は「速さ」そのものではなく、**アクセルの踏み込み具合**です。1.0 にしても、いきなり最高速になるわけではなく、だんだん速くなります。0 にするとブレーキがかかって止まります
- シミュレータでは、`angle` が 1.0 のとき、前輪が 20° 切れます
- `rc.drive.stop()` は `set_speed_angle(0, 0)` と同じです
- シミュレータの車には、**最高速の上限**がかかっています。はじめは 0.25 で、`speed` が 1.0 でも、全開の25%の力しか出ません。上限は `rc.drive.set_max_speed(0.5)` のように変えられますが、ぶつかると危ないので、最初はそのままにしておきましょう

:::message alert
`speed` と `angle` は、必ず −1.0 〜 1.0 の範囲にしなければなりません。範囲をはみ出すと、プログラムがエラーで止まります（⑤つまずきポイント）。
:::

### update() は「読む・決める・送る」

手動運転のプログラムの `update()` は、毎コマ次の3つをくり返します。1-1 で学んだ「見る・考える・動く」そのものです。

![update の中の3段階。① 読む：トリガー、スティック、ボタンを読む（見る）。② 決める：トリガーから speed、スティックから angle を決め、ボタンで強さを調整する（考える）。③ 送る：決めた speed と angle を update の最後で1回だけ車に送る（動く）。次のコマでまた①から](/images/racecar-neo-jp/3-2/fig1-update-flow.png)
*図1　手動運転のプログラムの `update()` の流れ*

命令は、**`update()` の最後で1回だけ**送ります。途中で何度も `set_speed_angle()` を呼ぶと、最後に呼んだものだけが効くので、どこで何が決まったのかがわかりにくくなるからです。変数 `speed`・`angle` に決めた値をためておき、最後にまとめて送ります。

### Lab C をやってみよう

課題のファイルは、labs フォルダの中の `lab_c/lab_c.py` です。課題のゴールは次のとおりです（原典の Expected Outcome より）。

| 操作 | キーボード | 車の動き |
|---|---|---|
| 右トリガーを押す | 右 Shift | 前に進む |
| 左トリガーを押す | 左 Shift | 後ろに進む |
| 左スティックを右／左に倒す | D ／ A（※） | 前輪を右／左に切る |
| A ボタン／B ボタン | 1 ／ 2 | 速さを上げる／下げる。今の速さを表示する |
| X ボタン／Y ボタン | 3 ／ 4 | 曲がる角度を上げる／下げる。今の角度を表示する |

※ ここでの A は、左スティックの左にあたるキーボードの **A キー**です。「A ボタン」はキーボードの **1** なので、取り違えないようにしましょう。

`start()` では、4つの変数に最初の値が入ります。

| 変数 | 最初の値 | 役割 |
|---|---|---|
| `speed` | 0.0 | 今のコマで車に送る速さ |
| `angle` | 0.0 | 今のコマで車に送る角度 |
| `speed_offset` | 0.5 | トリガーを押したときの速さの強さ（A・B で上げ下げする） |
| `angle_offset` | 1.0 | スティックを倒したときの角度の強さ（X・Y で上げ下げする） |

:::message alert
**訳注：初期値のコメントが食い違っている**
原典の `start()` には `speed = 0.0 # The initial speed is at 1.0`（最初の速さは 1.0）と書かれていますが、実際に入る値は 0.0 です。コメントの誤りで、0.0 のままで正しく動きます。
:::

#### Part 1：トリガーで前後に進む

右トリガーが押されていたら `speed` を `speed_offset` に、左トリガーが押されていたら `-speed_offset`（後ろ向き）にします。どちらも押されていなければ 0 です。

`get_trigger()` は 0.0〜1.0 の値を返すので、「押されている」は「0 より大きい」で調べられます。キーボードでは、押すと 1.0、離すと 0.0 になります。

:::details 答えの例（Part 1）
```python
if rc.controller.get_trigger(rc.controller.Trigger.RIGHT) > 0:
    speed = speed_offset
elif rc.controller.get_trigger(rc.controller.Trigger.LEFT) > 0:
    speed = -speed_offset
else:
    speed = 0
```
:::

#### Part 2：スティックでハンドルを切る

左スティックの左右の値 `x` が 0.5 より大きければ右（`angle_offset`）、−0.5 より小さければ左（`-angle_offset`）に切ります。この 0.5 のような「境目の値」を**しきい値**といいます。スティックは、少し触れただけでも小さな値が出るので、しきい値を決めておくと、うっかり曲がるのを防げます。

:::details 答えの例（Part 2）
```python
(x, y) = rc.controller.get_joystick(rc.controller.Joystick.LEFT)
if x > 0.5:
    angle = angle_offset
elif x < -0.5:
    angle = -angle_offset
else:
    angle = 0
```
`get_joystick()` は `(x, y)` の2つの値を返すので、`(x, y) = ...` と2つの変数で受け取ります。ここでは左右の `x` だけを使います。
:::

#### Part 3・4：ボタンで強さを変える

A・B ボタンで速さを、X・Y ボタンで曲がる角度を、少しずつ上げ下げします。上げ下げするたびに、今の値を表示します。

:::message alert
**訳注：変えるのは speed ではなく speed_offset**
原典のコメントは「A ボタンで speed（速さ）を上げる」と書いていますが、変数 `speed` を変えても意味がありません。`speed` は Part 1 で毎コマ上書きされるからです。ボタンで変えるのは、トリガーを押したときに使われる **`speed_offset`** です。角度も同じく、変えるのは **`angle_offset`** です。
:::

Part 3・4 は、if 文をまるごと自分で書きます。1回押したら1回だけ変えたいので、2-2 で学んだ `was_pressed` を使います。変える量は 0.1 ずつにしてみましょう。

ここで気をつけることが1つあります。`angle_offset` の最初の値は 1.0 です。この状態で X を押して 1.1 にし、そのままハンドルを切ると、`angle` が 1.1 になり、範囲をはみ出してプログラムが止まります。**上限は 1.0、下限は 0.0 に押さえこむ**（クランプする）必要があります。

Python の `min`（小さいほう）と `max`（大きいほう）を使うと、次のように書けます。

```python
speed_offset = min(speed_offset + 0.1, 1.0)   # 足した結果が 1.0 を超えたら 1.0 にする
speed_offset = max(speed_offset - 0.1, 0.0)   # 引いた結果が 0.0 を下回ったら 0.0 にする
```

:::details 答えの例（Part 3・4）
```python
# Part 3：A で速さを上げ、B で下げる
if rc.controller.was_pressed(rc.controller.Button.A):
    speed_offset = min(speed_offset + 0.1, 1.0)
    print(f"Speed: {speed_offset:.1f}")
if rc.controller.was_pressed(rc.controller.Button.B):
    speed_offset = max(speed_offset - 0.1, 0.0)
    print(f"Speed: {speed_offset:.1f}")

# Part 4：X で角度を上げ、Y で下げる
if rc.controller.was_pressed(rc.controller.Button.X):
    angle_offset = min(angle_offset + 0.1, 1.0)
    print(f"Angle: {angle_offset:.1f}")
if rc.controller.was_pressed(rc.controller.Button.Y):
    angle_offset = max(angle_offset - 0.1, 0.0)
    print(f"Angle: {angle_offset:.1f}")
```
表示の `:.1f` は、小数第1位までそろえて表示する書き方です（2-2 のつまずきポイント）。
:::

`update()` の最後には、`rc.drive.set_speed_angle(speed, angle)` がすでに書いてあります。図1の「③ 送る」です。

#### 実行してみる

```bash
racecar cd
cd lab_c
racecar sim lab_c.py
```

User Program モードに入ったら、右 Shift で進み、D・A で曲がってみましょう。A を何回か押すと、次のように表示され、速さが 1.0 で止まります。

```text
Speed: 0.6
Speed: 0.7
Speed: 0.8
Speed: 0.9
Speed: 1.0
Speed: 1.0
```

最後の `1.0` は、上限に達したあとにもう一度押したときの表示です。クランプが効いているので、それ以上は上がりません。

## ④ 数式・コード

### 発展：スティックを倒した量に合わせて曲がる

Lab C のハンドルは、「倒した」か「倒していない」かの2段階です。コントローラのスティックは、倒した量を −1.0〜1.0 の細かい値で返すので、次のように書くと、**少し倒せば少し、大きく倒せば大きく**曲がるようになります。

```python
(x, y) = rc.controller.get_joystick(rc.controller.Joystick.LEFT)
angle = x * angle_offset
```

$$
\text{angle} = x \times \text{angle\_offset}
$$

入力に比例して出力を決めるこの考え方は、第6章で学ぶ**比例制御**の出発点です。キーボードではスティックの値が −1・0・1 のどれかにしかならないので、違いを確かめるには Xbox のコントローラが必要です。

## ⑤ つまずきポイント

### AssertionError で止まった

```text
AssertionError: angle [1.1] must be between -1.0 and 1.0 inclusive.
```

`set_speed_angle()` に、−1.0〜1.0 をはみ出した値を渡すと、このエラーで止まります。Part 3・4 でクランプを忘れると、`angle_offset` の最初の値が 1.0 なので、X を1回押しただけでこうなります。`min`・`max` で範囲に収めましょう。

### 0.1 ずつ足したのに、0.7999999999999999 のように表示された

コンピュータは 0.1 を2進数でぴったり表せないため、足し算をくり返すと小さな誤差がたまります。実際に 0.5 に 0.1 を5回足すと、1.0 ではなく `0.9999999999999999` になります。表示では `:.1f` を使って桁をそろえ、比べるときは `==` を使わないようにします（3-1 のつまずきポイントと同じです）。クランプに `min`・`max` を使っておけば、誤差があっても上限・下限は正しく守られます。

### A ボタンを押しても、速さが変わらない

`speed` を変えていないか確かめましょう。`speed` は Part 1 で毎コマ上書きされるので、変えるのは `speed_offset` です（Part 3・4 の訳注）。

### キーを押しても車が動かない

- シミュレータの画面をクリックしてから操作していますか（1-2）
- User Program モードに入っていますか。画面右下に `User Program` と表示されているか確かめましょう

## ⑥ 確認問題

**問1**　`rc.drive.set_speed_angle(0.5, -0.5)` を送ると、車はどう動きますか。

:::details 答え
前向きに半分の力で進みながら、前輪を左に半分切ります。つまり、ゆるやかに左に曲がりながら進みます。
:::

**問2**　`speed_offset` が 0.5 のとき、A ボタンを8回押しました。クランプしている場合としていない場合で、`speed_offset` はそれぞれいくつになりますか。クランプしていない場合、右トリガーを押したときに何が起きますか。

:::details 答え
クランプしている場合は 1.0 です。表示が 1.0 になったあとは、何回押してもそれ以上は上がりません。クランプしていない場合は約 1.3 です。この状態で右トリガーを押すと、`speed` が 1.3 になって範囲をはみ出し、`AssertionError` で止まります。
:::

**問3**　右トリガーと左トリガーの押し込み具合を使い、「右を押すほど前へ、左を押すほど後ろへ」進むように、`speed` を1行で計算しましょう。両方押したときはどうなりますか。

:::details 答えの例
```python
speed = (rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
         - rc.controller.get_trigger(rc.controller.Trigger.LEFT)) * speed_offset
```
右の値から左の値を引くので、両方を同じだけ押すと 0 になって止まります。シミュレータの手動運転モードも、この計算で速さを決めています。
:::

## ⑦ 原典

- **Lab C - RACECAR Controller**（`labs/lab_c/lab_c.py`）：[racecar-neo-prereq-labs](https://github.com/MITRacecarNeo/racecar-neo-prereq-labs)（MIT License。ライセンスの全文は 1-3 の最後に載せています）
- `set_speed_angle`・`set_max_speed` の定義と範囲の確認：[racecar-neo-library](https://github.com/MITRacecarNeo/racecar-neo-library) の `drive.py` と `simulation/drive_sim.py`（GPL-3.0）
- 最高速の上限（0.25）、前輪の最大角（20°）、手動運転モードの速さの計算：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator) の `Drive.cs` と `Racecar.cs`

実行結果は、トリガー・スティック・ボタンの押し方を決めて1コマずつ動かすプログラムで確かめたものです。
