# web-data-automation-toolkit

Web スクレイピングとデータ整形を、設定ファイルだけで回すための再利用ツール群。
案件・業務ごとにコードを書き直さず、config / 変換ロジックを差し替えるだけで使い回せる。

## 構成
- `scraper_kit/` — URL と CSS セレクタを JSON に書くだけで収集 → Excel/CSV 出力する config 駆動スクレイパー
- `script_harness/` — CSV/JSON/Excel/テキストの相互変換を、変換関数 1 ファイルで回す汎用ハーネス

各ディレクトリの README を参照。

## セットアップ
```bash
pip install requests beautifulsoup4 lxml pandas openpyxl
```
