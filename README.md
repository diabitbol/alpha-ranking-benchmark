# Alpha Ranking Benchmark

**Goal.** Rank financial alphas (signals) from most to least predictive using machine learning on S&P 500 daily OHLCV (2005–2025).

**Why.** Hedge funds face a library of hundreds of alphas; most are weak or redundant. We provide a **reproducible benchmark** to compare ranking methods and select robust signals.

## Data
- Source: Yahoo Finance (daily OHLCV) using `yfinance`
- Universe: S&P 500 (current constituents; note survivorship bias)
- Period: 2005–2025

## Methods
- **Baselines:** random, EWMA-IC, Elastic Net
- **ML:** XGBoost (reg), LambdaMART (ranking)
- **Sequential:** GRU/LSTM, Transformer encoder

## Target & Metrics
- Targets: monthly **IC** (Information Coefficient) or L/S **Sharpe** of each alpha
- Metrics: **Spearman ρ**, **NDCG@k**, top-k portfolio **Sharpe/Drawdown/Turnover**, stability (overlap)

## Reproducibility
- Rolling time splits (train/val/test)
- Cross-sectional z-score & cap/sector neutralization
- Costs & slippage sensitivity
