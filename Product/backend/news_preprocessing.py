"""GDELT news headline preprocessing and FIN-RoBERTa classification.

Replicates the logic from preprocessing/news_preprocessing_labelling.ipynb.

Pipeline per ticker:
    1. Load raw CSV from Raw_Data/gdelt_news_data/
    2. Clean headlines (remove URLs, exchange prefixes, metadata suffixes)
    3. Score with FIN-RoBERTa  ->  P(positive) - P(negative)
    4. Assign each article to a NYSE session (16:00 ET cutoff)
    5. Aggregate to daily avg_sentiment
    6. Save to Processed_Data/news_sentiment_daily/
"""

import os
import re

import pandas as pd

from backend.config import RAW_NEWS_DIR, NEWS_SENTIMENT_DIR
from backend.sentiment import score_texts, assign_market_close_session


# ---------------------------------------------------------------------------
# Headline cleaning
# ---------------------------------------------------------------------------

def preprocess_headline(title):
    """Clean a single GDELT news headline for FIN-RoBERTa input.

    Removes:
      - URLs
      - Ticker symbols in (NASDAQ:XXX) or (NYSE:XXX) format
      - Exchange prefixes (e.g. leading ``NASDAQ:``)
      - Trailing news-source metadata (e.g. ``| Reuters``, ``- Wall Street``)
      - Non-alphanumeric characters (except basic punctuation)
    Returns None if the cleaned text is shorter than 15 characters.
    """
    if pd.isna(title) or not isinstance(title, str):
        return None

    title = re.sub(r"\s+", " ", title).strip()
    title = re.sub(r"http\S+|www\.\S+", "", title)
    title = re.sub(
        r"\(\s*(NASDAQ|NYSE)\s*:\s*\w+\s*\)", "", title, flags=re.IGNORECASE,
    )
    title = re.sub(r"\s*[-|]\s*[A-Z]{1,5}\s*$", "", title)
    title = re.sub(r"^\s*(NASDAQ|NYSE)\s*:\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s*\|\s*[A-Z][a-z]+\s*$", "", title)
    title = re.sub(r"\s*-\s*[A-Z][a-z]+\s+[A-Z][a-z]+\s*$", "", title)
    title = re.sub(r"[^\w\s\.,!?'\"\-]", " ", title)
    title = re.sub(r"\s+", " ", title).strip()

    if len(title) < 15:
        return None
    return title


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def classify_news(tickers, tokenizer, model, device, batch_size=16):
    """Classify GDELT news headlines and save daily sentiment CSVs.

    Parameters
    ----------
    tickers : list[str]
        Tickers to process (must match ``{TICKER}_news.csv`` in RAW_NEWS_DIR).
    tokenizer, model, device
        As returned by ``sentiment.load_model()``.
    batch_size : int
        Inference batch size (default 16).
    """
    os.makedirs(NEWS_SENTIMENT_DIR, exist_ok=True)

    for ticker in tickers:
        csv_path = RAW_NEWS_DIR / f"{ticker}_news.csv"
        if not csv_path.exists():
            print(f"[SKIP] {csv_path.name} not found")
            continue

        df = pd.read_csv(csv_path)
        if "headline" not in df.columns or "date" not in df.columns:
            print(f"[SKIP] {csv_path.name}: missing 'headline' or 'date' column")
            continue

        print(f"\n--- {ticker} news ---")

        # Clean
        df["clean_headline"] = df["headline"].apply(preprocess_headline)
        valid = df.dropna(subset=["clean_headline"]).copy()
        if valid.empty:
            print("  No valid headlines after cleaning")
            continue

        # Score
        print(f"  Scoring {len(valid)} headlines...")
        valid["sentiment_score"] = score_texts(
            valid["clean_headline"].tolist(), tokenizer, model, device, batch_size,
        )

        # Assign to NYSE session via 16:00 ET cutoff
        valid["datetime"] = pd.to_datetime(valid["date"], utc=True)
        valid["trade_date"] = assign_market_close_session(valid["datetime"])
        valid["sentiment_score"] = valid["sentiment_score"].astype(float).clip(-1, 1)

        # Aggregate to daily avg_sentiment
        daily = (
            valid.groupby("trade_date")["sentiment_score"]
            .mean()
            .reset_index()
            .rename(columns={"trade_date": "date", "sentiment_score": "avg_sentiment"})
        )
        daily["avg_sentiment"] = daily["avg_sentiment"].round(4)
        daily = daily.sort_values("date").reset_index(drop=True)

        out_path = NEWS_SENTIMENT_DIR / f"{ticker}_news_sentiment_daily.csv"
        daily.to_csv(out_path, index=False)
        print(f"  Saved {len(daily)} daily rows -> {out_path.name}")
