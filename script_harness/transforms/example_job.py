"""
変換ロジックのサンプル（案件ごとにこのファイルをコピーして中身を書き換える）

ルール:
  - transform(rows) は list[dict] を受け取り list[dict] を返す
  - rows の各要素は入力1行（キー=列名）
  - 列の追加・削除・整形・フィルタ・集計など何でもできる

この例がやっていること:
  - 氏名を「姓 名」に結合
  - 価格カンマ・円記号を除去して数値化
  - メールを小文字化
  - 価格が空の行は除外
"""
from __future__ import annotations


def clean_price(v: str) -> str:
    if not v:
        return ""
    return v.replace(",", "").replace("¥", "").replace("円", "").strip()


def transform(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        price = clean_price(r.get("price", ""))
        if not price:
            continue
        out.append({
            "氏名": f"{r.get('last_name', '').strip()} {r.get('first_name', '').strip()}".strip(),
            "メール": r.get("email", "").strip().lower(),
            "価格": price,
        })
    return out
