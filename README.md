# Statistical Analysis of S&P 500 Returns (2005–2025) — Applied Data/Finance Project

> Applied statistics/data science project in finance: **descriptive analysis** (stylized facts, volatility, volume, sector heterogeneity) followed by **predictive modeling** (direction classification and return regression) with **time-aware validation**.

## Table of Contents
- [Objectives](#objectives)
- [Data](#data)
- [Methodology](#methodology)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [Key Findings](#key-findings)
- [Limitations](#limitations)
- [References](#references)
- [License](#license)

---

## Objectives
1. **Statistically characterize** equity returns (heavy tails, volatility clustering, regimes, drawdowns).
2. Study the relationships between **volatility**, **trading volume**, and **price range** (High–Low), and quantify **sector-level heterogeneity**.
3. Evaluate **out-of-sample predictability** under realistic protocols:
   - **Classification**: predict whether the next return is positive.
   - **Regression**: predict the magnitude of the next return (or a multi-day horizon).

---

## Data
- **Universe**: S&P 500 constituents (based on the list available at data collection time).
- **Fields**: OHLCV (Open, High, Low, Close, Volume) + sector information (when available).
- **Frequency**: daily.
- **Period**: 2005–2025 (depending on availability).

---

## Methodology

### I. Descriptive analysis
- Log-return distributions: skewness, kurtosis, outliers.
- Rolling volatility (e.g., 5-day / 21-day), clustering, regime changes.
- Volume and High–Low range as proxies for market activity and price variability.
- Sector comparisons (volatility/volume/distribution differences).

### II. Predictive modeling
- Feature engineering (lags, rolling vol, volume/range features, sector variables).
- **Strictly time-ordered** train/validation/test splits.
- Models (examples): logistic regression, tree-based models, gradient boosting; analogous models for regression.
- Metrics: accuracy/AUC for classification, RMSE/MAE for regression.

**Key principle: prevent information leakage**
- All differencing/rolling operations must be **grouped by ticker**.
- Any scaling/encoding must be **fit on the training set only**, then applied to validation/test.

