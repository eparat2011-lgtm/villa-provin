#!/usr/bin/env python3
"""
Smart Money Backtesting
Uses: Funding Rate + Open Interest + Orderbook Imbalance
"""
import requests, json, time, os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

OUTPUT_DIR = "/home/marian_rachow/.openclaw/workspace/backtest"
FEE = 0.00055  # 0.055% per side

def fetch_klines_okx(symbol, bar, days):
    """Fetch historical candles from OKX."""
    base = "https://www.okx.com/api/v5/market/history-candles"
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = end_ms - days * 86400 * 1000
    
    all_candles = []
    before = None
    
    while True:
        params = {"instId": symbol, "bar": bar, "limit": 300}
        if before:
            params["before"] = before
        
        try:
            r = requests.get(base, params=params, timeout=15)
            data = r.json()
        except:
            time.sleep(2)
            continue
        
        if data.get("code") != "0" or not data.get("data"):
            break
        
        candles = data["data"]
        filtered = [c for c in candles if int(c[0]) >= start_ms]
        all_candles.extend(filtered)
        
        if len(filtered) < len(candles):
            break
        
        oldest_ts = min(int(c[0]) for c in candles)
        if oldest_ts <= start_ms:
            break
        
        before = str(oldest_ts)
        time.sleep(0.3)
    
    if not all_candles:
        return pd.DataFrame()
    
    df = pd.DataFrame(all_candles, columns=["ts","o","h","l","c","vol","volCcy","volCcyQuote","confirm"])
    df = df.astype({"ts": int, "o": float, "h": float, "l": float, "c": float, "vol": float})
    df["datetime"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df = df.rename(columns={"o":"open","h":"high","l":"low","c":"close","vol":"volume"})
    df = df.sort_values("datetime").reset_index(drop=True)
    return df

def fetch_funding_history_okx(symbol, days):
    """Fetch historical funding rates from OKX."""
    base = "https://www.okx.com/api/v5/public/funding-rate-history"
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = end_ms - days * 86400 * 1000
    
    all_rates = []
    after = None
    
    for _ in range(20):
        params = {"instId": symbol, "limit": 100}
        if after:
            params["after"] = after
        
        try:
            r = requests.get(base, params=params, timeout=15)
            data = r.json()
        except:
            break
        
        if data.get("code") != "0" or not data.get("data"):
            break
        
        rates = data["data"]
        filtered = [x for x in rates if int(x["fundingTime"]) >= start_ms]
        all_rates.extend(filtered)
        
        if len(filtered) < len(rates):
            break
        
        oldest = min(int(x["fundingTime"]) for x in rates)
        if oldest <= start_ms:
            break
        after = str(oldest)
        time.sleep(0.3)
    
    if not all_rates:
        return pd.DataFrame()
    
    df = pd.DataFrame(all_rates)
    df["datetime"] = pd.to_datetime(df["fundingTime"].astype(int), unit="ms", utc=True)
    df["funding_rate"] = df["fundingRate"].astype(float)
    df = df.sort_values("datetime").reset_index(drop=True)
    return df[["datetime", "funding_rate"]]

def ema(series, window):
    return series.ewm(span=window, adjust=False).mean()

def rsi(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def simulate_trades(df, signals, tp_pct, sl_pct, position_size, leverage=10, lookahead=200):
    """Simulate trades from signals list."""
    trades = []
    in_trade = False
    
    for idx, direction in signals:
        if in_trade:
            continue
        if idx + 1 >= len(df):
            continue
        
        entry_price = df["close"].iloc[idx]
        entry_time = df["datetime"].iloc[idx]
        
        if direction == "long":
            tp_price = entry_price * (1 + tp_pct)
            sl_price = entry_price * (1 - sl_pct)
        else:
            tp_price = entry_price * (1 - tp_pct)
            sl_price = entry_price * (1 + sl_pct)
        
        notional = position_size * leverage
        
        outcome = None
        for j in range(idx + 1, min(idx + lookahead, len(df))):
            high = df["high"].iloc[j]
            low = df["low"].iloc[j]
            
            if direction == "long":
                if low <= sl_price:
                    pnl = -notional * sl_pct - notional * FEE * 2
                    outcome = ("sl", pnl, df["datetime"].iloc[j])
                    break
                if high >= tp_price:
                    pnl = notional * tp_pct - notional * FEE * 2
                    outcome = ("tp", pnl, df["datetime"].iloc[j])
                    break
            else:
                if high >= sl_price:
                    pnl = -notional * sl_pct - notional * FEE * 2
                    outcome = ("sl", pnl, df["datetime"].iloc[j])
                    break
                if low <= tp_price:
                    pnl = notional * tp_pct - notional * FEE * 2
                    outcome = ("tp", pnl, df["datetime"].iloc[j])
                    break
        
        if outcome:
            trades.append({
                "entry_time": entry_time,
                "exit_time": outcome[2],
                "direction": direction,
                "outcome": outcome[0],
                "pnl": outcome[1]
            })
    
    return trades

def run_smart_money(symbol_okx, df_1h, df_funding):
    """
    Smart Money Strategy:
    Signal = Funding Rate extremes + OI change + Price momentum aligned
    
    LONG when:
    - Funding Rate < -0.03% (everyone short = short squeeze coming)
    - Price above 4h EMA (upward momentum)
    
    SHORT when:
    - Funding Rate > +0.08% (everyone long = long liquidation coming)
    - Price below 4h EMA (downward momentum)
    """
    df = df_1h.copy()
    
    # EMA indicators
    df["ema20"] = ema(df["close"], 20)
    df["ema50"] = ema(df["close"], 50)
    df["rsi14"] = rsi(df["close"], 14)
    
    # Merge funding rate (occurs every 8h)
    if not df_funding.empty:
        df_funding_indexed = df_funding.set_index("datetime")
        df = df.set_index("datetime")
        df["funding_rate"] = df_funding_indexed["funding_rate"].reindex(df.index, method="ffill")
        df = df.reset_index()
    else:
        df["funding_rate"] = 0.0
    
    # OI proxy: use volume spike as OI indicator
    df["vol_ma20"] = df["volume"].rolling(20).mean()
    df["vol_ratio"] = df["volume"] / df["vol_ma20"]
    
    signals = []
    
    for i in range(55, len(df) - 1):
        fr = df["funding_rate"].iloc[i] if pd.notna(df["funding_rate"].iloc[i]) else 0
        price = df["close"].iloc[i]
        ema20_val = df["ema20"].iloc[i]
        ema50_val = df["ema50"].iloc[i]
        rsi_val = df["rsi14"].iloc[i]
        vol_ratio = df["vol_ratio"].iloc[i]
        
        if pd.isna(ema20_val) or pd.isna(rsi_val):
            continue
        
        # Trend direction
        uptrend = price > ema20_val > ema50_val
        downtrend = price < ema20_val < ema50_val
        
        # Volume confirmation
        vol_confirm = vol_ratio > 1.3
        
        # LONG: Funding very negative (shorts will be squeezed) + uptrend forming
        if fr < -0.03/100 and (uptrend or rsi_val < 40) and vol_confirm:
            signals.append((i, "long"))
        
        # SHORT: Funding very positive (longs will be liquidated) + downtrend
        elif fr > 0.08/100 and (downtrend or rsi_val > 60) and vol_confirm:
            signals.append((i, "short"))
    
    return simulate_trades(df, signals, tp_pct=0.02, sl_pct=0.01,
                           position_size=300, leverage=10, lookahead=100)

def fmt_stats(trades, emoji, name):
    if not trades:
        return f"## {emoji} {name}\n- No trades\n"
    
    df_t = pd.DataFrame(trades)
    wins = df_t[df_t["pnl"] > 0]
    losses = df_t[df_t["pnl"] <= 0]
    total = df_t["pnl"].sum()
    wr = len(wins)/len(df_t)*100
    avg_win = wins["pnl"].mean() if len(wins) else 0
    avg_loss = losses["pnl"].mean() if len(losses) else 0
    
    # Monthly breakdown
    df_t["month"] = df_t["entry_time"].dt.to_period("M").astype(str)
    monthly = df_t.groupby("month")["pnl"].sum()
    monthly_str = "\n".join(f"  - {m}: ${v:+.2f}" for m, v in monthly.items())
    
    return f"""## {emoji} {name}
- Total Trades: {len(df_t)}
- Win Rate: {wr:.1f}%
- Total P&L: ${total:+.2f}
- Avg Win: ${avg_win:.2f} | Avg Loss: ${avg_loss:.2f}
- Monthly Breakdown:
{monthly_str}
"""

print("Fetching 100 days of 1H data...")
DAYS = 100
symbols = [("BTC-USDT-SWAP", "BTC"), ("ETH-USDT-SWAP", "ETH")]

all_sm_trades = []

for sym_okx, sym_label in symbols:
    print(f"  Fetching {sym_label} 1H candles...")
    df_1h = fetch_klines_okx(sym_okx, "1H", DAYS)
    print(f"  Fetching {sym_label} Funding Rates...")
    df_fr = fetch_funding_history_okx(sym_okx, DAYS)
    
    if df_1h.empty:
        print(f"  No data for {sym_label}")
        continue
    
    print(f"  Running Smart Money on {sym_label} ({len(df_1h)} candles, {len(df_fr)} funding rates)...")
    trades = run_smart_money(sym_okx, df_1h, df_fr)
    all_sm_trades.extend(trades)
    print(f"  {sym_label}: {len(trades)} trades")

# Results
period_start = "2025-12-08"
period_end = "2026-03-18"

result = f"""# Smart Money Backtesting — Last 100 Days
Period: {period_start} to {period_end}
Strategy: Funding Rate extremes + Volume confirmation + EMA trend
Leverage: 10x | Position: $300 | TP: 2% | SL: 1% | Fees: 0.055%/side

{fmt_stats(all_sm_trades, "🧠", "Smart Money Bot (Funding Rate + Volume)")}

## Interpretation
- Negative Funding (<-0.03%) = shorts squeezed = Long opportunity
- Positive Funding (>0.08%) = longs liquidated = Short opportunity
- Volume confirmation required (1.3x average)
"""

print(result)

out_file = os.path.join(OUTPUT_DIR, "results_smart_money.md")
with open(out_file, "w") as f:
    f.write(result)
print(f"Saved: {out_file}")
