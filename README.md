# web-data-automation-toolkit

Two small, **config-driven** tools for the work that quietly eats time in any data job: **collecting** data from the web, and **reshaping** data between formats. You write a short config or a single function — the toolkit handles the I/O, retries, encoding, and output.

The goal is reusability: stop rewriting a one-off scraper or converter for every task, and instead swap a config / a transform.

```
  scraper_kit   : URLs + CSS selectors (JSON)  ─▶ collect ─▶ Excel / CSV
  script_harness: one transform(rows) function  ─▶ convert ─▶ CSV / JSON / Excel / text
```

## What's inside

### 🕸️ `scraper_kit` — config-driven scraping

Put the target URLs and the fields you want (as CSS selectors) in a JSON file; get a clean spreadsheet out. No code changes per site.

```json
{
  "urls": ["https://example.com/p1", "https://example.com/p2"],
  "delay_sec": 1.5,
  "output": "result.xlsx",
  "fields": {
    "タイトル": { "selector": "h1" },
    "価格":   { "selector": ".price" },
    "画像URL": { "selector": "img.main", "attr": "src" },
    "リンク": { "selector": "a.item", "attr": "href", "all": true }
  }
}
```

- Text or attribute extraction; relative `href`/`src` are resolved to absolute URLs.
- Polite by default (per-request delay, user-agent); failures are logged to `errors.json` and the successful rows are still written.
- For JavaScript-rendered pages, the static fetch is swapped for a Playwright path.

### 🔁 `script_harness` — universal data conversion

Write one `transform(rows: list[dict]) -> list[dict]` function; the harness reads/writes **CSV / TSV / JSON / JSONL / Excel / text**, previews the first rows, and logs counts.

```bash
python convert.py --in data.csv --out result.xlsx --transform my_job --preview
```

The transform is the only thing you write per task; everything around it (format detection, encoding, Excel-safe BOM, validation) is handled.

## Why config-driven

Most scraping/conversion work is 90% the same plumbing and 10% “what to grab” / “how to reshape.” These tools isolate that 10% into a JSON config or a single function, so the same code is reused across jobs and the per-task surface stays tiny and reviewable.

## Quickstart

```bash
pip install requests beautifulsoup4 lxml pandas openpyxl

# scraping
cd scraper_kit && python scrape.py --config config.json --limit 3

# conversion
cd script_harness && python convert.py --in sample/input.csv --out out.xlsx --transform example_job
```

## Layout

| Path | What |
|------|------|
| `scraper_kit/scrape.py` | The scraper (don't edit — drive it with `config.json`). |
| `scraper_kit/config.example.json` | Copy to `config.json` and fill in. |
| `script_harness/convert.py` | The conversion harness. |
| `script_harness/transforms/` | One file per job, each exposing `transform(rows)`. |

## Manners

Scraping responsibly is part of the tool: check `robots.txt` and each site's terms first, keep the request delay, and don't target login-only or explicitly disallowed pages. Both tools default to conservative behavior.

## Requirements

Python 3.10+. See the per-directory READMEs for details.
