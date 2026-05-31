#!/usr/bin/env python3
"""
config駆動スクレイピングキット
================================
config.json に「URL」と「取りたい項目（CSSセレクタ）」を書くだけで、
収集 → Excel/CSV 出力まで自動。コードは触らない。

使い方:
    python scrape.py --config config.json
    python scrape.py --config config.json --limit 3   # 先頭3ページだけ試す

依存: requests, beautifulsoup4, lxml, pandas, openpyxl
    pip install requests beautifulsoup4 lxml pandas openpyxl

マナー（地雷を踏まないため）:
    - robots.txt と各サイトの利用規約を必ず確認してから使う
    - delay を入れて相手サーバに負荷をかけない（デフォルト1.5秒）
    - ログイン必須/会員専用ページや、明示的に禁止されたサイトはスクレイピングしない
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
except ImportError:
    sys.exit("依存が不足:  pip install requests beautifulsoup4 lxml pandas openpyxl")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DataCollector/1.0)"}


def extract_one(soup: BeautifulSoup, field: dict, base_url: str):
    """1項目を抽出。field = {selector, attr?, all?}"""
    sel = field["selector"]
    attr = field.get("attr")          # None なら textContent
    take_all = field.get("all", False)
    nodes = soup.select(sel)
    if not nodes:
        return [] if take_all else ""

    def val(node):
        if attr == "text" or attr is None:
            return node.get_text(strip=True)
        raw = node.get(attr, "")
        if attr in ("href", "src") and raw:
            return urljoin(base_url, raw)   # 相対URLを絶対に
        return raw

    return [val(n) for n in nodes] if take_all else val(nodes[0])


def scrape_page(url: str, fields: dict, session: requests.Session) -> dict:
    resp = session.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.text, "lxml")
    row = {"_url": url}
    for name, field in fields.items():
        row[name] = extract_one(soup, field, url)
    return row


def main() -> None:
    ap = argparse.ArgumentParser(description="config駆動スクレイパー")
    ap.add_argument("--config", required=True)
    ap.add_argument("--limit", type=int, default=0, help="先頭Nページだけ（0=全部）")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    urls = cfg["urls"]
    if args.limit:
        urls = urls[: args.limit]
    fields = cfg["fields"]
    delay = cfg.get("delay_sec", 1.5)
    out_path = Path(cfg.get("output", "result.xlsx"))

    session = requests.Session()
    rows, errors = [], []
    for i, url in enumerate(urls, 1):
        try:
            rows.append(scrape_page(url, fields, session))
            print(f"[{i}/{len(urls)}] OK  {url}")
        except Exception as e:  # noqa: BLE001
            errors.append({"url": url, "error": str(e)})
            print(f"[{i}/{len(urls)}] NG  {url}  ({e})")
        if i < len(urls):
            time.sleep(delay)

    for r in rows:
        for k, v in r.items():
            if isinstance(v, list):
                r[k] = "\n".join(map(str, v))

    df = pd.DataFrame(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() == ".csv":
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
    else:
        df.to_excel(out_path, index=False)
    print(f"\n[完了] {len(rows)} 件を {out_path} に出力" + (f" / 失敗 {len(errors)} 件" if errors else ""))
    if errors:
        Path("errors.json").write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8")
        print("失敗URLは errors.json を参照")


if __name__ == "__main__":
    main()
