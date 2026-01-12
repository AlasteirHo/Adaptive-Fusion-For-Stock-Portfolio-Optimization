# Meta Learning for Multi-Source Sentiment Analysis

A meta-learning approach to financial sentiment analysis that integrates multiple data sources (news articles and social media) to predict stock price movements and optimize investment portfolios.

**Author:** Alasteir Ho
**Institution:** University of Greenwich (Final Year Project)

## Overview

This system performs the following workflow:

1. **Data Collection** - Scrapes news articles from GDELT API and Twitter/X posts for 20 major stocks
2. **Sentiment Analysis** - Uses FinBERT to convert news headlines into sentiment scores
3. **Machine Learning** - Trains regression models to predict 14-day log returns using sentiment and price features
4. **Portfolio Optimization** - Implements Top-K and Markowitz mean-variance strategies with backtesting

## Supported Stocks

20 major S&P 500 stocks across multiple sectors:

| Sector | Tickers |
|--------|---------|
| Technology | NVDA, AAPL, MSFT, AVGO, ORCL, GOOGL, META, AMZN, TSLA |
| Finance | BRK.B, JPM, V, MA |
| Healthcare | LLY, JNJ, UNH |
| Energy & Staples | XOM, WMT, PG, HD |

## Technology Stack

- **Languages:** Python 3.8+
- **ML/NLP:** scikit-learn, PyTorch, Transformers (FinBERT)
- **Data:** Pandas, NumPy, yfinance
- **Web Scraping:** Selenium, undetected-chromedriver, GDELT API
- **Visualization:** Matplotlib, Jupyter Notebook

## Project Structure

```
FYP/
├── Pipeline/                          # Main analysis and modeling
│   ├── pipeline.ipynb                 # Full pipeline notebook
│   ├── sentiment_price_baseline.ipynb # Baseline model notebook
│   ├── news_sentiment_price_baseline.py
│   ├── PO_variant.py                  # Markowitz optimization
│   └── sentiment_price_markowitz_baseline.py
│
├── scrapers/                          # Data collection scripts
│   ├── GDELTscraper.py               # GDELT news scraper
│   ├── twitter_scraper.py
│   └── twitter_scraper2.py
│
├── preprocessing/                     # Data preprocessing
│   └── sentiment_analyzer_news.py     # FinBERT sentiment analysis
│
├── gdelt_news_data/                   # Raw news articles
├── processed_data/news_sentiment_daily/  # Daily sentiment scores
├── tweets/                            # Raw tweet data
├── outputs/                           # Backtest results
│
├── sp500_investment_analysis.py       # S&P 500 benchmark script
└── .env                               # Environment variables
```

## Installation

### Prerequisites

- Python 3.8+
- Chrome browser (for Twitter scraping)
- CUDA-capable GPU (optional, for faster inference)

### Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

2. **Install dependencies:**
   ```bash
   pip install pandas numpy scikit-learn torch transformers
   pip install matplotlib jupyter yfinance
   pip install selenium undetected-chromedriver
   pip install gdelt python-dotenv
   ```

3. **Configure environment variables:**

   Create a `.env` file with Twitter credentials:
   ```
   TWITTER_USERNAME=your_username
   TWITTER_PASSWORD=your_password
   ```

## Usage

### Step 1: Collect News Data
```bash
python scrapers/GDELTscraper.py
```
Outputs: `gdelt_news_data/{TICKER}_news.csv`

### Step 2: Collect Twitter Data (Optional)
```bash
python scrapers/twitter_scraper2.py
```
Outputs: `tweets/tweets_{TICKER}.csv`

### Step 3: Sentiment Analysis
```bash
python preprocessing/sentiment_analyzer_news.py
```
Outputs: `processed_data/news_sentiment_daily/{TICKER}_news_sentiment_daily.csv`

### Step 4: Train & Backtest Baseline Model
```bash
python Pipeline/news_sentiment_price_baseline.py
```
Outputs: `outputs/baseline_*.csv`

### Step 5: Markowitz Portfolio Optimization
```bash
python Pipeline/PO_variant.py
```
Outputs: `outputs/markowitz_*.csv`

### Interactive Analysis
```bash
jupyter notebook Pipeline/sentiment_price_baseline.ipynb
```

## Configuration

Key parameters in pipeline scripts:

```python
REBALANCE_N = 14              # Rebalance every 14 trading days
TOP_K = 5                     # Select top 5 stocks by predicted return
INITIAL_CAPITAL = 10_000      # Starting capital ($)

MODEL_NAME = "ridge"          # Model type: "ridge" or "elasticnet"
USE_TICKER_OHE = True         # Include ticker as one-hot feature

# Markowitz parameters
COV_LOOKBACK_DAYS = 126       # ~6 months for covariance estimation
MAX_WEIGHT = 0.25             # Max allocation per stock
```

## Output Files

| File | Description |
|------|-------------|
| `baseline_equity_daily.csv` | Daily portfolio value and benchmark equity |
| `baseline_trade_log.csv` | Rebalance dates with bought/held/sold tickers |
| `baseline_trades_detail.csv` | Individual trade execution details |
| `markowitz_equity_daily.csv` | Markowitz strategy equity curve |
| `markowitz_rebalance_log.csv` | Markowitz rebalance transactions |

## Features

- **Data Leakage Prevention:** Uses only t-1 data to predict t+14 returns
- **Multiple Data Sources:** Financial news (GDELT) and social media (Twitter)
- **FinBERT Sentiment Analysis:** Domain-specific NLP model for financial text
- **Backtesting Framework:** Daily mark-to-market with SPY benchmark comparison
- **Portfolio Strategies:** Top-K selection and Markowitz mean-variance optimization

## License

This project is part of a Final Year Project at the University of Greenwich.
