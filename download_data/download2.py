# pip install yfinance pandas requests

import os, time, math
from typing import List, Tuple
import pandas as pd
import yfinance as yf
import requests

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
START = "2005-01-01"     # <- mets "2005-01-01" si tu veux plus long
END   = "2025-01-01"
CSV_OUT = "../sp500_ohlcv_2005_2025_2.csv"
BATCH = 40               # taille des lots (30–60 recommandé)
MAX_RETRIES = 3
TIMEOUT = 30

def get_sp500_tickers() -> list[str]:
    # 1) yfinance a une liste intégrée
    try:
        tickers = yf.tickers_sp500()
        if tickers:
            return [t.replace('.', '-') for t in tickers]
    except Exception:
        pass
    # 2) fallback: Wikipédia avec User-Agent
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(WIKI_URL, headers=headers, timeout=20).text
    sp500 = pd.read_html(html, header=0)[0]
    return sp500["Symbol"].str.replace('.', '-', regex=False).tolist()

def chunked(lst: List[str], n: int):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def download_batch(tickers: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    """Télécharge un lot avec retries/backoff. Retourne (df_long, failed)."""
    failed = list(tickers)
    out_frames = []
    for attempt in range(1, MAX_RETRIES+1):
        if not failed:
            break
        try:
            data = yf.download(
                failed, start=START, end=END, interval="1d",
                group_by="ticker", auto_adjust=True,
                threads=False, progress=False, timeout=TIMEOUT
            )
        except Exception:
            data = pd.DataFrame()

        next_failed = []
        for t in failed:
            try:
                # MultiIndex columns: niveau 0 = ticker
                df_t = data[t].copy() if isinstance(data.columns, pd.MultiIndex) else data.copy()
                if df_t.empty:
                    next_failed.append(t)
                    continue
                df_t["Ticker"] = t
                out_frames.append(df_t.reset_index())
            except Exception:
                next_failed.append(t)

        failed = next_failed
        if failed and attempt < MAX_RETRIES:
            time.sleep(3 * (2 ** (attempt-1)))  # backoff
    df = pd.concat(out_frames, ignore_index=True) if out_frames else pd.DataFrame()
    return df, failed

def append_to_csv(df: pd.DataFrame, path: str):
    # uniformise colonnes
    keep = [c for c in ["Date","Ticker","Open","High","Low","Close","Volume","Adj Close"] if c in df.columns]
    df = df[keep]
    # si Adj Close == Close (auto_adjust=True), on peut drop
    if "Adj Close" in df.columns and "Close" in df.columns and df["Adj Close"].equals(df["Close"]):
        df = df.drop(columns=["Adj Close"])
    # écriture en mode append (header seulement si fichier absent)
    header = not os.path.exists(path)
    df.to_csv(path, mode="a", index=False, header=header)

def main():
    tickers = get_sp500_tickers()
    print(f"{len(tickers)} tickers S&P 500 chargés. Exemples: {tickers[:10]}")

    if os.path.exists(CSV_OUT):
        os.remove(CSV_OUT)

    all_failed = []
    total_batches = math.ceil(len(tickers)/BATCH)

    for i, batch in enumerate(chunked(tickers, BATCH), 1):
        print(f"[Batch {i}/{total_batches}] {len(batch)} tickers…")
        df_batch, failed = download_batch(batch)
        if not df_batch.empty:
            append_to_csv(df_batch, CSV_OUT)
            print(f"  -> {len(df_batch):,} lignes ajoutées")
        if failed:
            print(f"  !! Échecs (tentatives groupées épuisées): {failed}")
            all_failed.extend(failed)

    # Dernière chance: retenter 1 par 1 les échecs persistants
    really_failed = []
    if all_failed:
        print(f"Tentatives individuelles pour {len(all_failed)} tickers…")
        for t in all_failed:
            df1, rem = download_batch([t])
            if not df1.empty and not rem:
                append_to_csv(df1, CSV_OUT)
                print(f"  -> récupéré {t}")
            else:
                really_failed.append(t)

    print("\n✅ Fichier CSV :", os.path.abspath(CSV_OUT))
    if really_failed:
        print(f"⚠️ Impossible de télécharger après retries: {len(really_failed)} tickers")
        print(really_failed)

if __name__ == "__main__":
    main()
