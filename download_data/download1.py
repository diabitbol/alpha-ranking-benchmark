import pandas as pd
import yfinance as yf
import requests

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

def get_sp500_tickers() -> list[str]:
    # 1) Essai: liste intégrée yfinance (souvent suffit)
    try:
        tickers = yf.tickers_sp500()
        if tickers:
            return [t.replace('.', '-') for t in tickers]
    except Exception:
        pass

    # 2) Fallback: Wikipédia avec User-Agent pour éviter 403
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    r = requests.get(WIKI_URL, headers=headers, timeout=20)
    r.raise_for_status()  # lèvera une erreur si 403/4xx/5xx
    # Pandas peut lire depuis la chaîne HTML directement
    tables = pd.read_html(r.text, header=0)  # nécessite lxml OU html5lib
    sp500 = tables[0]
    return sp500["Symbol"].str.replace('.', '-', regex=False).tolist()

def download_sp500_ohlcv_csv(start="2005-01-01", end="2025-01-01", out_csv="../sp500_ohlcv_2005_2025_1.csv"):
    tickers = get_sp500_tickers()
    print(f"{len(tickers)} tickers récupérés. Exemples: {tickers[:10]}")

    data = yf.download(
        tickers,
        start=start,
        end=end,
        interval="1d",
        group_by="ticker",
        auto_adjust=True,   # ajuste splits/dividendes
        threads=True,
        progress=True,
    )

    # Reformater en (Date, Ticker)
    frames = []
    for t in tickers:
        if isinstance(data.columns, pd.MultiIndex) and t in data.columns.get_level_values(0):
            df_t = data[t].copy()
        else:
            # cas rare: un seul ticker ou structure différente
            if t == tickers[0]:
                df_t = data.copy()
            else:
                continue
        df_t["Ticker"] = t
        df_t = df_t.reset_index()
        frames.append(df_t)

    df = pd.concat(frames, ignore_index=True)
    df = df.set_index(["Date", "Ticker"]).sort_index()

    # Garder colonnes standard si présentes
    keep = [c for c in ["Open","High","Low","Close","Volume","Adj Close"] if c in df.columns]
    df = df[keep]
    # Si auto_adjust=True, Adj Close == Close → on peut la supprimer
    if "Adj Close" in df.columns and "Close" in df.columns:
        if df["Adj Close"].equals(df["Close"]):
            df = df.drop(columns=["Adj Close"])

    df.to_csv(out_csv)
    print(f"✅ Sauvegardé : {out_csv}")
    return df

if __name__ == "__main__":
    download_sp500_ohlcv_csv()
