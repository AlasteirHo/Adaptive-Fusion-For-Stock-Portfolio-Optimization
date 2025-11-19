#!/usr/bin/env python3
import csv, re, sys, time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from dateutil import parser as dateparser
import newspaper
from newspaper import Article, Config

# ---- Config ----
DAYS_BACK = 365
REQUEST_DELAY = 0.5
OUTPUT = "nvda_news_last_year.csv"
KEYWORD_RE = re.compile(r"\b(nvidia|nvda)\b", re.IGNORECASE)

# High-signal seeds (Reuters NVDA company page is best-in-class)
SEEDS = {
    "Reuters": [
        "https://www.reuters.com/markets/companies/NVDA.O",  # NVDA company hub
        "https://www.reuters.com/technology/",
        "https://www.reuters.com/markets/companies/",
    ],
    "Yahoo Finance": ["https://finance.yahoo.com/quote/NVDA/news/"],
    "CNBC": ["https://www.cnbc.com/nvidia/", "https://www.cnbc.com/technology/"],
    "MarketWatch": ["https://www.marketwatch.com/investing/stock/nvda"],
    "The Verge": ["https://www.theverge.com/tech"],
    "Tom's Hardware": ["https://www.tomshardware.com/news"],
}

def as_utc(dt):
    if not dt: return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

def in_window(dt, now):
    return dt and (now - timedelta(days=DAYS_BACK) <= dt <= now + timedelta(days=1))

def guess_publish_date(a: Article):
    # 1) library’s parsed date if present
    if a.publish_date: 
        return as_utc(a.publish_date)
    # 2) common meta tags
    md = a.meta_data or {}
    candidates = []
    keys = ["article:published_time","og:published_time","og:updated_time",
            "pubdate","publish_date","datePublished","date"]
    for k in keys:
        if k in md: candidates.append(md[k])
        for sub in ("article","og"):
            if isinstance(md.get(sub), dict) and k in md[sub]:
                candidates.append(md[sub][k])
    for v in candidates:
        try: return as_utc(dateparser.parse(str(v)))
        except: pass
    # 3) URL fallback
    try:
        m = re.search(r"(20\d{2}[/-]\d{1,2}[/-]\d{1,2})", a.url or "")
        if m: return as_utc(dateparser.parse(m.group(1)))
    except: pass
    return None

def looks_like_article(url: str):
    if not url: return False
    path = urlparse(url).path.lower()
    if path.endswith((".pdf",".jpg",".jpeg",".png",".gif",".mp4",".webp",".zip")):
        return False
    return True

def write_header_if_needed(path):
    try:
        open(path, "r", encoding="utf-8").close()
    except FileNotFoundError:
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                ["source","title","publisher","authors","published_utc","url","summary"]
            )

def main():
    now = datetime.now(timezone.utc)
    write_header_if_needed(OUTPUT)

    # Build config per docs
    cfg = Config()
    cfg.browser_user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36")
    cfg.request_timeout = 15
    cfg.fetch_images = False
    cfg.memoize_articles = False
    cfg.language = "en"

    # Build Sources (no parsing yet per API) and walk their discovered articles
    sources = []
    for brand, urls in SEEDS.items():
        for u in urls:
            try:
                src = newspaper.build(u, config=cfg, memoize_articles=False, number_threads=4)
                sources.append((brand, src))
            except Exception as e:
                print(f"[warn] build failed: {u} ({e})", file=sys.stderr)

    seen = set()
    with open(OUTPUT, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for brand, src in sources:
            for art in src.articles:
                url = getattr(art, "url", None)
                if not looks_like_article(url) or url in seen: 
                    continue
                seen.add(url)

                a = Article(url, config=cfg)
                try:
                    a.download(); a.parse()
                except Exception:
                    continue

                # quick keyword filter
                if not (KEYWORD_RE.search(a.title or "") or KEYWORD_RE.search(a.text or "")):
                    continue

                pub = guess_publish_date(a)
                if not in_window(pub, now):
                    continue

                # try NLP summary (best-effort)
                summary = ""
                try:
                    a.nlp()
                    summary = (a.summary or "").replace("\n"," ").strip()
                except Exception:
                    summary = (a.text or "")[:400].replace("\n"," ").strip()

                w.writerow([
                    brand,
                    (a.title or "").strip(),
                    brand,
                    "; ".join(a.authors or []),
                    pub.isoformat() if pub else "",
                    url,
                    summary
                ])
                print(f"[saved] {brand} | {a.title[:90] if a.title else url}")
                time.sleep(REQUEST_DELAY)

    print(f"[done] wrote -> {OUTPUT} | rows: {len(seen)}")

if __name__ == "__main__":
    main()
