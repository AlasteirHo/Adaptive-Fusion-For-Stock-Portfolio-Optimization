"""About / Home page for the Adaptive Fusion POC demo app."""

import pandas as pd
import streamlit as st

from backend.config import (
    METRICS_PATH,
    NEWS_SENTIMENT_DIR,
    RAW_NEWS_DIR,
    RAW_TWEETS_DIR,
    SOCIAL_SENTIMENT_DIR,
    TICKERS,
    TRADE_LOG_PATH,
)

st.title("Adaptive Fusion POC")
st.markdown(
    "A real-time demonstration of the adaptive sentiment fusion portfolio strategy. "
    "Use the pages in the sidebar to run data collection and simulate the portfolio."
)
st.divider()

# ---------------------------------------------------------------------------
# System status
# ---------------------------------------------------------------------------
st.subheader("System Status")


def count_files(directory, pattern="*.csv"):
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Raw News Files", f"{count_files(RAW_NEWS_DIR)} / {len(TICKERS)}")
    st.metric("Raw Tweet Files", f"{count_files(RAW_TWEETS_DIR)} / {len(TICKERS)}")

with col2:
    st.metric("News Sentiment Files", f"{count_files(NEWS_SENTIMENT_DIR)} / {len(TICKERS)}")
    st.metric("Tweet Sentiment Files", f"{count_files(SOCIAL_SENTIMENT_DIR)} / {len(TICKERS)}")

with col3:
    st.metric("Trade Log", "Ready" if TRADE_LOG_PATH.exists() else "Missing")
    st.metric("Metrics Summary", "Ready" if METRICS_PATH.exists() else "Missing")

with col4:
    if TRADE_LOG_PATH.exists():
        try:
            df_tl = pd.read_csv(TRADE_LOG_PATH)
            dates = pd.to_datetime(df_tl["date"])
            st.metric("Total Trades Logged", len(df_tl))
            st.metric("Simulation Period", f"{dates.min().date()} to {dates.max().date()}")
        except Exception:
            st.metric("Trade Log", "Error reading")
    else:
        st.metric("Total Trades Logged", "--")
        st.metric("Simulation Period", "--")

st.divider()

# ---------------------------------------------------------------------------
# Performance snapshot
# ---------------------------------------------------------------------------
st.subheader("Strategy Performance Snapshot")

if METRICS_PATH.exists():
    metrics_df = pd.read_csv(METRICS_PATH)
    fmt = {
        "Sharpe Ratio":      "{:.4f}",
        "Annualised Return": "{:.2%}",
        "Annualised Vol":    "{:.2%}",
        "Max Drawdown":      "{:.2%}",
        "Calmar Ratio":      "{:.4f}",
        "Total Return":      "{:.2%}",
    }
    display_df = metrics_df.copy()
    for col, f in fmt.items():
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f.format(x))
    st.dataframe(display_df.set_index("Strategy"), width="stretch")
else:
    st.info("Metrics summary not found. Run the portfolio simulation first.")

st.divider()

# ---------------------------------------------------------------------------
# Navigation guide
# ---------------------------------------------------------------------------
st.subheader("Navigation Guide")
c1, c2 = st.columns(2)
with c1:
    st.markdown(
        "**Data Collection**\n"
        "- Launch GDELT news scraper for any date range and ticker subset\n"
        "- Launch Twitter/X scraper in a controlled browser session\n"
        "- Monitor live stdout logs as scraping progresses"
    )
with c2:
    st.markdown(
        "**Portfolio Simulation**\n"
        "- Select strategy (Price-Only, Static-Fusion, Adaptive Fixed, Adaptive WF)\n"
        "- Train the Adaptive Fusion neural network live\n"
        "- Run backtest and view NAV, drawdown, weights, attention, and trade log\n"
        "- Compare all strategies side-by-side against SPY and Equal-Weight benchmarks"
    )
