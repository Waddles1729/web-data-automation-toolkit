# 汎用スクリプト変換ハーネス

CSV / JSON / Excel / テキストの変換を、**変換ロジック1ファイルだけ書けば**回せる再利用テンプレ。
読み書き・形式判定・検証・ログはハーネス側が担当する。

## セットアップ（初回のみ）
```bash
pip install pandas openpyxl
```

## 1案件あたりの流れ
1. 入出力サンプルと変換ルールを整理し、`transform()` を実装（`PROMPT_TEMPLATE.md` に生成AI用のプロンプト雛形あり）
2. `transforms/案件名.py` に保存
3. プレビュー実行で先頭5件を確認：`python convert.py --in 元データ.csv --out 確認.xlsx --transform 案件名 --preview`
4. OKなら本実行 → 出力を検証 → 納品：`python convert.py --in 元データ.csv --out 納品.xlsx --transform 案件名`

## サンプルを動かす
```bash
python convert.py --in sample/input.csv --out sample/out.xlsx --transform example_job
```

## 対応形式
| 入力 | 出力 |
|---|---|
| .csv .tsv .json .jsonl .xlsx .txt | .csv .tsv .json .jsonl .xlsx |

## コツ
- CSV出力は `utf-8-sig`（BOM付き）なのでExcelで開いても文字化けしない
- 同じ形式の案件は同じ transform を使い回せる
- 大量データは `--preview` で先頭確認してから本実行
