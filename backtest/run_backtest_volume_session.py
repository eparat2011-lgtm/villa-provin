#!/usr/bin/env python3
"""
Smart Volume + Session Strategy
- Whale detection via volume clustering (3x+ average = institutional move)
- Session timing: EU Open (08-09:30) + US Open (14-15:30) only
- BTC as leader: ETH follows BTC signal with 1-3 candle lag
"""
import requests, time, os
import pandas as pd
import numpy as np
from datetime import datetime, timezone

OUTPUT_DIR = "/home/marian_rachow/.openclaw/workspace/backtest"
FEE = 0.00055
DAYS = 100

def fetch_klines(symbol, bar, days):
    base = "https://www.okx.com/api/v5/market/history-candles"
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = end_ms - days * 86400 * 1000
    all_candles = []
    before = None
    for _ in range(200):
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
        oldest = min(int(c[0]) for c in candles)
        if oldest <= start_ms:
            break
        before = str(oldest)
        time.sleep(0.25)
    if not all_candles:
        return pd.DataFrame()
    df = pd.DataFrame(all_candles, columns=["ts","open","high","low","close","vol","volCcy","volQuote","confirm"])
    df = df.astype({"ts":int,"open":float,"high":float,"low":float,"close":float,"vol":float})
    df["datetime"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df = df.sort_values("datetime").reset_index(drop=True)
    return df

def ema(s, w): return s.ewm(span=w, adjust=False).mean()
def rsi(s, w=14):
    d = s.diff(); g = d.clip(lower=0).rolling(w).mean()
    l = (-d.clip(upper=0)).rolling(w).mean()
    return 100 - (100/(1+g/l.replace(0,np.nan)))

def is_session(dt):
    """Returns True if within EU Open (08-09:30) or US Open (14-15:30) UTC"""
    h, m = dt.hour, dt.minute
    eu = (h == 8) or (h == 9 and m <= 30)
    us = (h == 14) or (h == 15 and m <= 30)
    return eu or us

def simulate_trades(df, signals, tp_pct, sl_pct, position_size, leverage=10, lookahead=50):
    trades = []
    used = set()
    for idx, direction in signals:
        if idx in used: continue
        if idx + 1 >= len(df): continue
        entry = df["close"].iloc[idx]
        entry_time = df["datetime"].iloc[idx]
        tp = entry*(1+tp_pct) if direction=="long" else entry*(1-tp_pct)
        sl = entry*(1-sl_pct) if direction=="long" else entry*(1+sl_pct)
        notional = position_size * leverage
        for j in range(idx+1, min(idx+lookahead, len(df))):
            hi, lo = df["high"].iloc[j], df["low"].iloc[j]
            if direction=="long":
                if lo<=sl:
                    trades.append({"entry_time":entry_time,"exit_time":df["datetime"].iloc[j],"direction":direction,"outcome":"sl","pnl":-notional*sl_pct - notional*FEE*2})
                    break
                if hi>=tp:
                    trades.append({"entry_time":entry_time,"exit_time":df["datetime"].iloc[j],"direction":direction,"outcome":"tp","pnl":notional*tp_pct - notional*FEE*2})
                    break
            else:
                if hi>=sl:
                    trades.append({"entry_time":entry_time,"exit_time":df["datetime"].iloc[j],"direction":direction,"outcome":"sl","pnl":-notional*sl_pct - notional*FEE*2})
                    break
                if lo<=tp:
                    trades.append({"entry_time":entry_time,"exit_time":df["datetime"].iloc[j],"direction":direction,"outcome":"tp","pnl":notional*tp_pct - notional*FEE*2})
                    break
    return trades

def run_volume_session(df_15m, df_btc_15m=None):
    """
    Strategy:
    1. Session filter: only EU Open + US Open
    2. Volume spike: current candle volume > 3x 20-period average
    3. Direction: candle is bullish/bearish + EMA confirmation
    4. BTC leader (optional): if BTC already moved same direction in last 2 candles → confirm
    """
    df = df_15m.copy()
    df["vol_ma20"] = df["vol"].rolling(20).mean()
    df["vol_ratio"] = df["vol"] / df["vol_ma20"]
    df["ema20"] = ema(df["close"], 20)
    df["ema50"] = ema(df["close"], 50)
    df["rsi14"] = rsi(df["close"], 14)
    df["candle_bull"] = df["close"] > df["open"]
    df["candle_size"] = (df["close"] - df["open"]).abs() / df["open"]
    
    # BTC leader signal
    btc_signal = {}
    if df_btc_15m is not None:
        df_btc = df_btc_15m.copy()
        df_btc["ema9"] = ema(df_btc["close"], 9)
        df_btc["ema21"] = ema(df_btc["close"], 21)
        for i in range(2, len(df_btc)):
            dt = df_btc["datetime"].iloc[i]
            # BTC crossover signal
            if df_btc["ema9"].iloc[i] > df_btc["ema21"].iloc[i] and df_btc["ema9"].iloc[i-1] <= df_btc["ema21"].iloc[i-1]:
                btc_signal[dt] = "long"
            elif df_btc["ema9"].iloc[i] < df_btc["ema21"].iloc[i] and df_btc["ema9"].iloc[i-1] >= df_btc["ema21"].iloc[i-1]:
                btc_signal[dt] = "short"
    
    signals = []
    last_signal_time = None
    
    for i in range(25, len(df)-1):
        dt = df["datetime"].iloc[i]
        
        # Session filter
        if not is_session(dt):
            continue
        
        # Min 2 candles between signals (30min spacing)
        if last_signal_time and (dt - last_signal_time).total_seconds() < 1800:
            continue
        
        vol_ratio = df["vol_ratio"].iloc[i]
        is_bull = df["candle_bull"].iloc[i]
        rsi_val = df["rsi14"].iloc[i]
        ema20_val = df["ema20"].iloc[i]
        price = df["close"].iloc[i]
        
        if pd.isna(vol_ratio) or pd.isna(rsi_val):
            continue
        
        # Volume whale threshold: 2.5x average
        if vol_ratio < 2.5:
            continue
        
        # Determine direction
        direction = "long" if is_bull else "short"
        
        # EMA filter: trade with trend
        if direction == "long" and price < ema20_val * 0.995:
            continue
        if direction == "short" and price > ema20_val * 1.005:
            continue
        
        # RSI filter: not in extreme zone going wrong way
        if direction == "long" and rsi_val > 70:
            continue
        if direction == "short" and rsi_val < 30:
            continue
        
        # BTC leader confirmation (if available)
        if btc_signal:
            # Look for BTC signal in last 3 candles
            btc_confirm = False
            for lag in range(0, 4):
                check_dt = dt - pd.Timedelta(minutes=15*lag)
                if btc_signal.get(check_dt) == direction:
                    btc_confirm = True
                    break
            if not btc_confirm:
                continue
        
        signals.append((i, direction))
        last_signal_time = dt
    
    return simulate_trades(df, signals, tp_pct=0.015, sl_pct=0.008,
                           position_size=200, leverage=10, lookahead=30)

def fmt_stats(trades, emoji, name):
    if not trades:
        return f"## {emoji} {name}\n- No trades generated\n"
    df_t = pd.DataFrame(trades)
    wins = df_t[df_t["pnl"]>0]
    losses = df_t[df_t["pnl"]<=0]
    total = df_t["pnl"].sum()
    wr = len(wins)/len(df_t)*100
    avg_win = wins["pnl"].mean() if len(wins) else 0
    avg_loss = losses["pnl"].mean() if len(losses) else 0
    df_t["month"] = df_t["entry_time"].dt.to_period("M").astype(str)
    monthly = df_t.groupby("month")["pnl"].sum()
    monthly_str = "\n".join(f"  - {m}: ${v:+.2f}" for m,v in monthly.items())
    return f"""## {emoji} {name}
- Total Trades: {len(df_t)}
- Win Rate: {wr:.1f}%
- Total P&L: ${total:+.2f}
- Avg Win: ${avg_win:.2f} | Avg Loss: ${avg_loss:.2f}
- Monthly Breakdown:
{monthly_str}
"""

print("Fetching data...")
df_btc = fetch_klines("BTC-USDT-SWAP", "15m", DAYS)
print(f"BTC: {len(df_btc)} candles")
df_eth = fetch_klines("ETH-USDT-SWAP", "15m", DAYS)
print(f"ETH: {len(df_eth)} candles")

print("\nRunning Volume+Session strategy on BTC...")
btc_trades = run_volume_session(df_btc)

print("Running Volume+Session+BTC Leader on ETH...")
eth_trades = run_volume_session(df_eth, df_btc)

all_trades = btc_trades + eth_trades

result = f"""# Volume Clustering + Session Timing Backtest
Period: Last 100 days (BTC + ETH)
Strategy: Volume spike (2.5x avg) + Session timing (EU/US Open) + BTC leader
Leverage: 10x | Position: $200 | TP: 1.5% | SL: 0.8% | Fees: 0.055%

{fmt_stats(btc_trades, "₿", "BTC — Volume+Session")}
{fmt_stats(eth_trades, "Ξ", "ETH — Volume+Session+BTC Leader")}
{fmt_stats(all_trades, "📊", "Combined")}
"""

print(result)
out = os.path.join(OUTPUT_DIR, "results_volume_session.md")
with open(out,"w") as f:
    f.write(result)
print(f"Saved: {out}")
