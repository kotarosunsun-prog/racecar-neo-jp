
# racecar-neo-jp（Zenn 原稿リポジトリ）

- `books/racecar-neo-jp/` … 本の設定（config.yaml）と各章の原稿
- `images/racecar-neo-jp/<章番号>/` … 各章の図（PNG）
- `figsrc/` … 図の元データ（SVG と matplotlib スクリプト）。図を直すときはここを編集して PNG を書き出し直す

## プレビュー

    npm install
    npx zenn preview

ブラウザで http://localhost:8000 を開く。

## 公開前にやること

- `books/racecar-neo-jp/cover.png`（500×700px 推奨）を置く
- `config.yaml` の `published: false` を `true` にする
