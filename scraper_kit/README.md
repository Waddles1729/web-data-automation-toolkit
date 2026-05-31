# config駆動スクレイピングキット

URLと「取りたい項目のCSSセレクタ」を `config.json` に書くだけで、収集 → Excel/CSV 出力まで自動。
Pythonコード（`scrape.py`）は触らない。

## セットアップ（初回のみ）
```bash
pip install requests beautifulsoup4 lxml pandas openpyxl
```

## 1案件あたりの流れ
1. `config.example.json` をコピーして `config.json` を作る
2. `urls` に対象ページ、`fields` に取りたい項目とCSSセレクタを書く
3. まず少数で試す：`python scrape.py --config config.json --limit 3`
4. 出力を確認 → 全件実行：`python scrape.py --config config.json`

## セレクタの調べ方
ブラウザで対象ページを開き、取りたい要素を右クリック→「検証」→要素を右クリック→「Copy → Copy selector」。
それを `selector` に貼る。複雑な構造は検証ツールでDOMを見ながら調整する。

## fields の書き方
| 書き方 | 意味 |
|---|---|
| `{ "selector": "h1" }` | その要素のテキストを取得 |
| `{ "selector": "img", "attr": "src" }` | 属性値を取得（src/hrefは絶対URLに自動変換） |
| `{ "selector": "a.item", "attr": "href", "all": true }` | 該当する全要素を取得（複数） |

## マナー（重要）
- robots.txt と利用規約を必ず確認してから実行する
- `delay_sec` で相手サーバに負荷をかけない
- ログイン必須/会員専用、明示的に禁止されたサイトはやらない

## 出力
- `.xlsx`（デフォルト）または `.csv`（`output` の拡張子で切替）
- 複数値の項目は1セル内に改行で連結
- 失敗したURLは `errors.json` に記録され、成功分はそのまま出力される

## 動的サイト（JavaScriptで描画）の場合
`scrape.py` は静的HTML用。SPA等でデータが取れない場合は Playwright ベースに差し替える。
