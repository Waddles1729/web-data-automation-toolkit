#!/usr/bin/env python3
"""
汎用スクリプト変換ハーネス
===========================
案件ごとに「変換ロジック」だけを transforms/ に1ファイル書けば、
入出力の読み書き・形式判定・ログ・検証は全部このハーネスが面倒を見る。

使い方:
    python convert.py --in input.csv --out output.xlsx --transform my_job
    python convert.py --in data.json --out result.csv --transform my_job --preview

対応フォーマット: .csv / .tsv / .json / .jsonl / .xlsx / .txt
変換ロジックの追加: transforms/<name>.py に `def transform(rows: list[dict]) -> list[dict]` を書くだけ。

依存: pandas, openpyxl  (pip install pandas openpyxl)
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("pandas が必要です:  pip install pandas openpyxl")


def load(path: Path) -> list[dict]:
    ext = path.suffix.lower()
    if ext in (".csv", ".tsv"):
        sep = "\t" if ext == ".tsv" else ","
        return pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False).to_dict("records")
    if ext == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("data") or data.get("items") or [data]
        return [dict(r) for r in data]
    if ext == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if ext == ".xlsx":
        return pd.read_excel(path, dtype=str).fillna("").to_dict("records")
    if ext == ".txt":
        return [{"line": ln} for ln in path.read_text(encoding="utf-8").splitlines()]
    sys.exit(f"未対応の入力形式: {ext}")


def save(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ext = path.suffix.lower()
    df = pd.DataFrame(rows)
    if ext == ".csv":
        df.to_csv(path, index=False, encoding="utf-8-sig")
    elif ext == ".tsv":
        df.to_csv(path, index=False, sep="\t", encoding="utf-8-sig")
    elif ext == ".xlsx":
        df.to_excel(path, index=False)
    elif ext == ".json":
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    elif ext == ".jsonl":
        path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    else:
        sys.exit(f"未対応の出力形式: {ext}")


def load_transform(name: str):
    p = Path(__file__).parent / "transforms" / f"{name}.py"
    if not p.exists():
        sys.exit(f"変換ファイルが見つかりません: {p}")
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "transform"):
        sys.exit(f"{p} に transform(rows) 関数がありません。")
    return mod.transform


def main() -> None:
    ap = argparse.ArgumentParser(description="汎用変換ハーネス")
    ap.add_argument("--in", dest="inp", required=True, help="入力ファイル")
    ap.add_argument("--out", dest="out", required=True, help="出力ファイル")
    ap.add_argument("--transform", required=True, help="transforms/<name>.py の <name>")
    ap.add_argument("--preview", action="store_true", help="先頭5件だけ表示して書き込まない")
    args = ap.parse_args()

    src = load(Path(args.inp))
    print(f"[読込] {len(src)} 行  ({args.inp})")

    transform = load_transform(args.transform)
    out_rows = transform(src)
    if not isinstance(out_rows, list):
        sys.exit("transform() は list[dict] を返してください。")
    print(f"[変換] {len(out_rows)} 行  (ロジック: {args.transform})")

    if args.preview:
        for r in out_rows[:5]:
            print("  ", r)
        print("[preview] 書き込みはしていません。")
        return

    save(out_rows, Path(args.out))
    print(f"[出力] {args.out} に書き込み完了")


if __name__ == "__main__":
    main()
