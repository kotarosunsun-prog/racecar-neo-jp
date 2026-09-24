---
title: "1-2 シミュレータを準備する"
free: true
---

この回では、自分のパソコンに RACECAR のシミュレータとプログラムの実行環境を入れて、サンプルのプログラムで車を動かすところまで進めます。インストールは、MIT が公開している公式のインストーラを使います。

## ① この回でできるようになること

1. 公式のインストーラで、シミュレータ・ライブラリ・課題のプログラム一式をインストールできる
2. `racecar` コマンドで、プログラムをシミュレータにつないで動かせる
3. キーボードで車を操作し、手動運転と User Program モードを切り替えられる

## ② 使う用語

| 英語 | 日本語 | ひとことで言うと |
|---|---|---|
| Terminal | ターミナル | 文字でコマンドを打ってパソコンを操作する画面 |
| Command | コマンド | ターミナルに打つ命令 |
| Repository | リポジトリ | GitHub 上のプログラムの置き場所 |
| Clone | クローン | リポジトリを自分のパソコンに丸ごとコピーすること |
| WSL | WSL | Windows の中で Linux を動かすしくみ |
| Virtual environment | 仮想環境 | このコース専用に分けた Python の環境 |
| Level | レベル | シミュレータの中のコースや課題の場面 |
| Default Drive mode | 手動運転モード | キーボードやコントローラで直接運転するモード |
| User Program mode | ユーザープログラム・モード | 自分のプログラムが車を動かすモード |

## ③ 本文

### インストーラがしてくれること

公式のインストーラ（[racecar-neo-installer](https://github.com/MITRacecarNeo/racecar-neo-installer)）は、コマンドを1つ実行するだけで次のことをまとめて行います。

- シミュレータ（RacecarSim）、ライブラリ、課題のプログラムを GitHub から取ってくる
- Python 3.9 と、このコース専用の仮想環境（`racecar-venv`）を用意する
- `racecar` という便利なコマンドを使えるようにする

全部で15分ほどかかります。インターネットにつながった状態で行ってください。

### 手順1：OS ごとの下準備

| OS | 下準備 |
|---|---|
| Windows 10/11 | WSL2 と Ubuntu を入れます。以下のコマンドはすべて、Ubuntu のターミナルで打ちます |
| macOS 10.15 以降 | 「ターミナル」アプリを開くだけで大丈夫です。途中で Homebrew と Python 3.9 が自動で入ります |
| Linux（Ubuntu 20 以降など） | ターミナルを開くだけで大丈夫です |

**Windows の場合**は、次の手順で WSL2 と Ubuntu を入れます。

1. スタートメニューで「PowerShell」を右クリックして、「管理者として実行」を選ぶ
2. `wsl --install` と打って Enter を押し、終わったらパソコンを再起動する
3. 再起動後に開く Ubuntu の画面で、ユーザー名とパスワードを決める。ユーザー名には**空白を入れない**でください

:::message alert
**訳注：古い手順書に注意**
インストーラの説明からリンクされている Google ドキュメントの手順書には、「Xming（XLaunch）を入れる」「WSL1 に戻す」という手順が書かれています。これは古い版の手順で、2026年5月時点のインストーラは WSL2 を前提にしており、どちらも不要です。代わりに、インストールの最後に「Windows ファイアウォールの設定」が求められます（手順3）。
:::

### 手順2：インストーラを実行する

ターミナルで、インストールしたい場所に移動してから、次の2行を順に打ちます。

```bash
git clone https://github.com/MITRacecarNeo/racecar-neo-installer.git
bash racecar-neo-installer/racecar-student/scripts/setup.sh
```

途中で2つ質問されるので、番号を打って Enter を押します。

```text
[1/4] Select your operating system: [windows, mac, linux]
1) windows
2) mac
3) linux
#?
```

自分の OS の番号を選びます。

```text
[2/4] Select your course curriculum: [oneshot, outreach, prereq, mites]
1) oneshot
2) outreach
3) prereq
4) mites
#?
```

**`3`（prereq）を選びます。** prereq は、この本が沿っているオンライン事前コース（prerequisite course）の課題のプログラムです。

あとは待つだけです。途中でパスワードを聞かれたら、パソコン（Windows なら Ubuntu）のパスワードを入れます。打っても画面には何も表示されませんが、そのまま入力して Enter を押せば大丈夫です。

終わったら、**ターミナルをいったん閉じて、開き直します。** そのあと、公式の説明のとおり次のコマンドも実行しておきます。

```bash
pip3 install -r racecar-neo-installer/racecar-student/scripts/requirements.txt
```

### 手順3（Windows だけ）：ファイアウォールの設定

Windows では、シミュレータと Ubuntu の中のプログラムが通信できるように、ファイアウォールに通り道を1つ開けます。インストールの最後に、オレンジ色の文字でこの案内が出ます。

PowerShell を「管理者として実行」で開き、次の1行をそのまま貼り付けて Enter を押します。1回だけで大丈夫です。

```powershell
New-NetFirewallRule -DisplayName "WSL2 RacecarNeo Simulator" -Direction Inbound -InterfaceAlias (Get-NetAdapter -IncludeHidden | Where-Object { $_.Name -like '*WSL*' } | Select-Object -First 1 -ExpandProperty Name) -Action Allow -Protocol UDP -LocalPort 5064-5065
```

### 手順4：インストールを確かめる

開き直したターミナルで、次のコマンドを打ちます。

```bash
racecar test
```

`racecar tool set up successfully!` と表示されれば成功です。`racecar` コマンドでできることの一覧は `racecar help` で見られます。この本でよく使うのは次の4つです。

| コマンド | すること |
|---|---|
| `racecar cd` | 課題のプログラムが入ったフォルダ（labs）に移動する |
| `racecar open_sim` | シミュレータを起動する |
| `racecar sim ファイル名.py` | そのプログラムを、シミュレータにつないで実行する |
| `racecar help` | 使えるコマンドの一覧を表示する |

### 手順5：サンプルのプログラムで車を動かす

いよいよ車を動かします。プログラムとシミュレータは、図1の順番でつながります。

![ターミナルとシミュレータがつながる順番。1 シミュレータを起動、2 ターミナルで racecar sim を実行すると接続待ちになる、3 シミュレータでレベルを開くと Connection established と出る、4 Enter で User Program モードに入ると start が1回動く、5 そのあと update が1コマごとに動く](/images/racecar-neo-jp/1-2/fig1-connection.png)
*図1　プログラムとシミュレータがつながる順番*

1. `racecar open_sim` でシミュレータを起動します
2. もう一つターミナルを開き、`racecar cd` で labs フォルダに移動してから、`racecar sim demo.py` を実行します。`>> Python script loaded, awaiting connection from RacecarSim.` と表示され、つながるのを待つ状態になります
3. シミュレータで、好きなレベル（コース）を選んで開きます。ターミナルに緑の文字で `>> Connection established with RacecarSim` と出れば、つながりました
4. シミュレータの画面をクリックしてから **Enter** を押すと、画面右下の表示が **User Program** に変わります。ここから先は、`demo.py` が車を動かしています
5. キーボードの **1** を押すと、ターミナルに `The A button was pressed` と表示されます。**2** を押すと、車が1秒まっすぐ進み、次の1秒で右に曲がって止まります

終わるときは、シミュレータで **Esc** を押してメニューに戻り、ターミナルで **Ctrl＋C** を押してプログラムを止めます。

### キーボードでの操作

シミュレータは、Xbox のコントローラでもキーボードでも操作できます。この本では、ボタンを「A ボタン」のようにコントローラの名前で呼びます。キーボードでは次のキーにあたります。

| コントローラ | キーボード | 手動運転モードでの働き |
|---|---|---|
| A / B / X / Y ボタン | 1 / 2 / 3 / 4 | ― |
| 左バンパー（LB） / 右バンパー（RB） | Z / /（スラッシュ） | 最高速度を下げる／上げる |
| 左トリガー（LT） / 右トリガー（RT） | 左 Shift / 右 Shift | 後退／前進 |
| 左スティック | W・A・S・D | 左右でハンドルを切る |
| 右スティック | 矢印キー | ― |
| 左スティック押し込み / 右スティック押し込み | 5 / 6 | ― |
| START ボタン | Enter | User Program モードに入る |
| BACK ボタン | Backspace | 手動運転モードに戻る |

シミュレータにだけある操作もあります。

| キー | 働き |
|---|---|
| Enter と Backspace を同時押し | レベルを最初からやり直す |
| Space | カメラの視点を切り替える |
| 左 Alt／右 Alt | シミュレータの時間の進み方を半分／2倍にする |
| Esc | レベルを終えてメニューに戻る |

:::message
User Program モードでは、キーボードの押した・離したの情報はすべてあなたのプログラムに届きます。どのキーで何が起きるかは、プログラムの書き方しだいです。第2章で、ボタンの状態をプログラムで読み取る方法を学びます。
:::

## ⑤ つまずきポイント

### Enter を押しても User Program モードにならない

画面に `You must connect a Python program before entering User Program mode.` と出る場合は、プログラムがまだつながっていません。ターミナルで `racecar sim` を実行したか、緑の `Connection established` が出ているかを確かめてください。Windows では、手順3のファイアウォールの設定を忘れていると、ここでつながりません。

### キーを押しても何も起きない

キーボードの入力は、**いま選ばれているウィンドウ**に届きます。ターミナルを触ったあとは、シミュレータの画面を一度クリックしてからキーを押してください。

### インストールを2回実行したらエラーが出た

インストーラは、すでにインストールされているのを見つけると、フォルダが二重にならないように止まります。やり直したいときは、エラーの文面の指示どおりに `racecar-neo-installer` フォルダを消してから、手順2を最初から行ってください。ライブラリや課題を最新にしたいだけなら、エラーの文面に表示される `update.sh` を使います。

### Python のバージョンが違うと言われる

RACECAR のライブラリは **Python 3.9** で動かす前提です。インストーラが作る仮想環境（`racecar-venv`）には 3.9 が入っています。自分で別のバージョンの Python を使うと動かないことがあるので、`racecar` コマンドを使って実行するようにしてください。

## ⑥ 確認問題

**問1**　`racecar sim demo.py` を実行したあと、ターミナルに `awaiting connection from RacecarSim` と出たまま止まっています。次に何をすればよいですか。

:::details 答え
シミュレータを起動して、レベルを選んで開きます。つながると、ターミナルに緑の `Connection established` が出ます。
:::

**問2**　キーボードで次の操作をするには、どのキーを押せばよいですか。
(1) 手動運転で前に進む　(2) 自分のプログラムに車を任せる　(3) 手動運転に戻る　(4) コースを最初からやり直す

:::details 答え
(1) 右 Shift　(2) Enter　(3) Backspace　(4) Enter と Backspace を同時に押す
:::

**問3**　`demo.py` を動かして、2（B ボタン）を押したとき、車は何秒間まっすぐ進みましたか。実際に試して、図を見ながら確かめましょう。

:::details 答え
1秒間まっすぐ進み、次の1秒間で右に曲がって止まります。`demo.py` の中の `counter < 1` と `counter < 2` という部分が、この秒数を決めています。このしくみは 1-3 と第4章で詳しく学びます。
:::

## ⑦ 原典

- インストーラ：[racecar-neo-installer](https://github.com/MITRacecarNeo/racecar-neo-installer)（README、`setup.sh`、`racecar_tool.sh`）
- シミュレータ：[RacecarNeo-Simulator](https://github.com/MITRacecarNeo/RacecarNeo-Simulator)（キーボードの割り当ては `Controller.cs`、モードの切り替えは `LevelManager.cs` による）
- サンプルのプログラム：`demo.py`（[racecar-neo-prereq-labs](https://github.com/MITRacecarNeo/racecar-neo-prereq-labs)、MIT License）

インストール手順は、2026年5月時点のインストーラをもとにしています。インストーラが更新されたときは、画面に出る案内を優先してください。
