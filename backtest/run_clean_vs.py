import requests, time, os
import pandas as pd
import numpy as np
from datetime import datetime, timezone

FEE = 0.00055
OUTPUT_DIR = "/home/marian_rachow/.openclaw/workspace/backtest"

def fetch_klines(symbol, bar, days):
    base = "https://www.okx.com/api/v5/market/history-candles"
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = end_ms - days * 86400 * 1000
    all_candles = []
    before = None
    for _ in range(200):
        params = {"instId": symbol, "bar": bar, "limit": 300}
        if before: params["before"] = before
        try:
            r = requests.get(base, params=params, timeout=15)
            data = r.json()
        except: time.sleep(2); continue
        if data.get("code") != "0" or not data.get("data"): break
        candles = data["data"]
        filtered = [c for c in candles if int(c[0]) >= start_ms]
        all_candles.extend(filtered)
        if len(filtered) < len(candles): break
        oldest = min(int(c[0]) for c in candles)
        if oldest <= start_ms: break
        before = str(oldest)
        time.sleep(0.25)
    if not all_candles: return pd.DataFrame()
    df = pd.DataFrame(all_candles, columns=["ts","open","high","low","close","vol","a","b","c"])
    df = df.astype({"ts":int,"open":float,"high":float,"low":float,"close":float,"vol":float})
    df["datetime"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    return df.sort_values("datetime").reset_index(drop=True)

def ema(s,w): return s.ewm(span=w, adjust=False).mean()
def rsi(s,w=14):
    d=s.diff(); g=d.clip(lower=0).rolling(w).mean()
    l=(-d.clip(upper=0)).rolling(w).mean()
    return 100-(100/(1+g/l.replace(0,np.nan)))

def simulate_trades(df, signals, tp_pct, sl_pct, pos, lev=10, look=40):
    trades = []
    for idx, direction in signals:
        if idx+1 >= len(df): continue
        entry = df["close"].iloc[idx]
        entry_time = df["datetime"].iloc[idx]
        tp = entry*(1+tp_pct) if direction=="long" else entry*(1-tp_pct)
        sl = entry*(1-sl_pct) if direction=="long" else entry*(1+sl_pct)
        notional = pos * lev
        for j in range(idx+1, min(idx+look, len(df))):
            hi, lo = df["high"].iloc[j], df["low"].iloc[j]
            if direction=="long":
                if lo<=sl: trades.append({"entry_time":entry_time,"pnl":-notional*sl_pct-notional*FEE*2,"outcome":"sl"}); break
                if hi>=tp: trades.append({"entry_time":entry_time,"pnl":notional*tp_pct-notional*FEE*2,"outcome":"tp"}); break
            else:
                if hi>=sl: trades.append({"entry_time":entry_time,"pnl":-notional*sl_pct-notional*FEE*2,"outcome":"sl"}); break
                if lo<=tp: trades.append({"entry_time":entry_time,"pnl":notional*tp_pct-notional*FEE*2,"outcome":"tp"}); break
    return trades

def run_strategy(df, name):
    df = df.copy()
    df["vol_ma"] = df["vol"].rolling(20).mean()
    df["vol_ratio"] = df["vol"] / df["vol_ma"]
    df["ema20"] = ema(df["close"], 20)
    df["ema50"] = ema(df["close"], 50)
    df["rsi14"] = rsi(df["close"])
    df["bull"] = df["close"] > df["open"]
    df["hour"] = df["datetime"].dt.hour
    
    signals = []
    last_idx = -5
    
    for i in range(25, len(df)-1):
        h = df["hour"].iloc[i]
        # Session: EU Open 08-10, US Open 14-16
        if h not in [8,9,10,14,15,16]: continue
        if i - last_idx < 4: continue  # min 4 candles between trades
        
        vr = df["vol_ratio"].iloc[i]
        bull = df["bull"].iloc[i]
        rsi_val = df["rsi14"].iloc[i]
        price = df["close"].iloc[i]
        e20 = df["ema20"].iloc[i]
        
        if pd.isna(vr) or pd.isna(rsi_val) or pd.isna(e20): continue
        if vr < 1.3: continue  # Volume threshold
        
        direction = "long" if bull else "short"
        
        # Don't trade against strong trend
        if direction=="long" and rsi_val > 72: continue
        if direction=="short" and rsi_val < 28: continue
        
        # EMA filter: trade with local trend
        if direction=="long" and price < e20 * 0.992: continue
        if direction=="short" and price > e20 * 1.008: continue
        
        signals.append((i, direction))
        last_idx = i
    
    print(f"{name}: {len(signals)} signals generated")
    return simulate_trades(df, signals, tp_pct=0.015, sl_pct=0.008, pos=200)

def fmt(trades, name):
    if not trades: return f"## {name}\n- No trades\n"
    df_t = pd.DataFrame(trades)
    wins = df_t[df_t["pnl"]>0]
    total = df_t["pnl"].sum()
    wr = len(wins)/len(df_t)*100
    df_t["month"] = pd.to_datetime(df_t["entry_time"]).dt.to_period("M").astype(str)
    mb = df_t.groupby("month")["pnl"].sum()
    return f"""## {name}
- Trades: {len(df_t)} | Win Rate: {wr:.1f}% | P&L: ${total:+.2f}
- Avg Win: ${wins["pnl"].mean():.2f} | Avg Loss: ${df_t[df_t["pnl"]<=0]["pnl"].mean():.2f}
- Monthly: {dict(mb)}
"""

print("Fetching 100 days...")
df_btc = fetch_klines("BTC-USDT-SWAP", "15m", 100)
df_eth = fetch_klines("ETH-USDT-SWAP", "15m", 100)
print(f"BTC: {len(df_btc)} | ETH: {len(df_eth)}")

btc_trades = run_strategy(df_btc, "BTC")
eth_trades = run_strategy(df_eth, "ETH")
all_trades = btc_trades + eth_trades

result = f"""# Volume + Session Strategy v3
100 days | TP 1.5% | SL 0.8% | $200 pos | 10x | Sessions: EU+US Open

{fmt(btc_trades, "BTC")}
{fmt(eth_trades, "ETH")}
{fmt(all_trades, "Combined")}
"""
print(result)
with open(f"{OUTPUT_DIR}/results_clean.md","w") as f: f.write(result)
print("Done!")
