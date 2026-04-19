#!/usr/bin/env python3
"""
Backtesting script for 3 bot strategies on BTCUSDT and ETHUSDT
Last 100 days of data from OKX public API (Bybit is geo-blocked)
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import time
import os

# ─── CONFIG ────────────────────────────────────────────────────────────────────
SYMBOLS_OKX = ["BTC-USDT-SWAP", "ETH-USDT-SWAP"]
DAYS = 100
OUTPUT_DIR = "/home/marian_rachow/.openclaw/workspace/backtest"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "results.md")
BASE_URL = "https://www.okx.com/api/v5/market/history-candles"

FEE_PER_SIDE = 0.00055  # 0.055%
MAX_PER_REQUEST = 300   # OKX max

# ─── DATA FETCHING ─────────────────────────────────────────────────────────────

def fetch_klines_okx(symbol, bar, days, extra_days=0):
    """
    Fetch historical candles from OKX with pagination.
    bar: e.g. "15m", "1H", "1m"
    Returns DataFrame sorted ascending by datetime.
    """
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = end_ms - (days + extra_days) * 24 * 60 * 60 * 1000
    
    all_candles = []
    after_ms = end_ms + 1  # OKX: 'after' means return candles BEFORE this ts
    
    print(f"  Fetching {symbol} {bar} ({days}d)...")
    
    max_iterations = 500
    iterations = 0
    
    while iterations < max_iterations:
        iterations += 1
        try:
            params = {
                "instId": symbol,
                "bar": bar,
                "limit": MAX_PER_REQUEST,
                "after": str(after_ms),
                "before": str(start_ms)
            }
            resp = requests.get(BASE_URL, params=params, timeout=15)
            data = resp.json()
            
            if data.get("code") != "0":
                print(f"    OKX error: {data.get('msg')}")
                break
            
            candles = data["data"]
            if not candles:
                break
            
            all_candles.extend(candles)
            
            # OKX returns newest first; last entry is oldest in this batch
            oldest_ts = int(candles[-1][0])
            
            if oldest_ts <= start_ms:
                break
            
            after_ms = oldest_ts  # paginate backwards
            time.sleep(0.12)
            
        except Exception as e:
            print(f"    Error: {e}")
            break
    
    if not all_candles:
        return pd.DataFrame()
    
    # OKX columns: [ts, open, high, low, close, vol, volCcy, volCcyQuote, confirm]
    df = pd.DataFrame(all_candles, columns=[
        "timestamp", "open", "high", "low", "close",
        "volume", "volCcy", "volCcyQuote", "confirm"
    ])
    df = df.astype({
        "timestamp": int, "open": float, "high": float,
        "low": float, "close": float, "volume": float
    })
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.sort_values("datetime").drop_duplicates("timestamp").reset_index(drop=True)
    
    # Filter to requested range (only last `days`, not extra warmup)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    df_filtered = df[df["datetime"] >= cutoff].reset_index(drop=True)
    
    actual_count = len(df_filtered)
    if actual_count > 0:
        print(f"    {actual_count} candles | {df_filtered['datetime'].iloc[0].date()} → {df_filtered['datetime'].iloc[-1].date()}")
    else:
        print(f"    WARNING: 0 candles in target range (fetched {len(df)} total)")
    
    # Return full df for warmup calculations, but tag which portion is "live"
    df["in_range"] = df["datetime"] >= cutoff
    return df


def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def rsi_calc(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


# ─── TRADE SIMULATION ─────────────────────────────────────────────────────────

def simulate_trades(df, signals, tp_pct, sl_pct, position_size, leverage=10, lookahead=100):
    trades = []
    n = len(df)
    
    for sig_idx, direction in signals:
        entry_idx = sig_idx + 1
        if entry_idx >= n:
            continue
        
        entry_price = df["open"].iloc[entry_idx]
        if entry_price <= 0:
            continue
        
        notional = position_size * leverage
        
        if direction == "long":
            tp_price = entry_price * (1 + tp_pct)
            sl_price = entry_price * (1 - sl_pct)
        else:
            tp_price = entry_price * (1 - tp_pct)
            sl_price = entry_price * (1 + sl_pct)
        
        fee_entry = notional * FEE_PER_SIDE
        fee_exit = notional * FEE_PER_SIDE
        
        exit_price = None
        exit_idx = min(entry_idx + lookahead - 1, n - 1)
        outcome = "timeout"
        
        for j in range(entry_idx + 1, min(entry_idx + lookahead, n)):
            high = df["high"].iloc[j]
            low = df["low"].iloc[j]
            
            if direction == "long":
                # Check SL first (conservative)
                if low <= sl_price:
                    exit_price = sl_price
                    outcome = "sl"
                    exit_idx = j
                    break
                if high >= tp_price:
                    exit_price = tp_price
                    outcome = "tp"
                    exit_idx = j
                    break
            else:
                if high >= sl_price:
                    exit_price = sl_price
                    outcome = "sl"
                    exit_idx = j
                    break
                if low <= tp_price:
                    exit_price = tp_price
                    outcome = "tp"
                    exit_idx = j
                    break
        
        if exit_price is None:
            exit_price = df["close"].iloc[exit_idx]
        
        if direction == "long":
            raw_pnl = (exit_price - entry_price) / entry_price * notional
        else:
            raw_pnl = (entry_price - exit_price) / entry_price * notional
        
        pnl = raw_pnl - fee_entry - fee_exit
        
        entry_dt = df["datetime"].iloc[entry_idx]
        trades.append({
            "entry_idx": entry_idx,
            "exit_idx": exit_idx,
            "direction": direction,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "outcome": outcome,
            "pnl": pnl,
            "date": entry_dt.date(),
            "month": entry_dt.strftime("%Y-%m"),
        })
    
    return trades


def compute_stats(trades, bot_name):
    if not trades:
        return {
            "name": bot_name,
            "total_trades": 0,
            "win_rate": 0.0,
            "total_pnl": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "max_drawdown": 0.0,
            "best_month": 0.0,
            "worst_month": 0.0,
            "monthly": {}
        }
    
    pnls = [t["pnl"] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    
    total_pnl = sum(pnls)
    win_rate = len(wins) / len(pnls) * 100
    avg_win = np.mean(wins) if wins else 0.0
    avg_loss = np.mean(losses) if losses else 0.0
    
    cumulative = np.cumsum(pnls)
    peak = np.maximum.accumulate(cumulative)
    drawdown = peak - cumulative
    max_dd = float(np.max(drawdown)) if len(drawdown) > 0 else 0.0
    
    monthly = {}
    for t in trades:
        m = t["month"]
        monthly[m] = monthly.get(m, 0.0) + t["pnl"]
    
    best_month = max(monthly.values()) if monthly else 0.0
    worst_month = min(monthly.values()) if monthly else 0.0
    
    return {
        "name": bot_name,
        "total_trades": len(pnls),
        "win_rate": round(win_rate, 1),
        "total_pnl": round(total_pnl, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "max_drawdown": round(max_dd, 2),
        "best_month": round(best_month, 2),
        "worst_month": round(worst_month, 2),
        "monthly": {k: round(v, 2) for k, v in sorted(monthly.items())}
    }


# ─── BOT 1: EMA 9/21 + RSI, 15min ────────────────────────────────────────────

def run_bot1(symbol, df_15m_full, df_1h_full):
    """Bot 1 — Trend (EMA 9/21, 15min) with 1H EMA200 regime filter."""
    df = df_15m_full.copy()
    
    df["ema9"] = ema(df["close"], 9)
    df["ema21"] = ema(df["close"], 21)
    df["rsi"] = rsi_calc(df["close"], 14)
    
    # 1H EMA200
    df_1h = df_1h_full.copy()
    df_1h["ema200_1h"] = ema(df_1h["close"], 200)
    df_1h["datetime_h"] = df_1h["datetime"].dt.floor("h")
    df_1h_slim = df_1h[["datetime_h", "ema200_1h"]].drop_duplicates("datetime_h")
    
    df["datetime_h"] = df["datetime"].dt.floor("h")
    df = pd.merge_asof(
        df.sort_values("datetime_h"),
        df_1h_slim.sort_values("datetime_h"),
        on="datetime_h",
        direction="backward"
    ).sort_values("datetime").reset_index(drop=True)
    
    # Only trade in the 100-day window
    in_range_mask = df["in_range"]
    
    signals = []
    for i in range(1, len(df) - 1):
        if not in_range_mask.iloc[i]:
            continue
        
        ema9_prev = df["ema9"].iloc[i - 1]
        ema21_prev = df["ema21"].iloc[i - 1]
        ema9_curr = df["ema9"].iloc[i]
        ema21_curr = df["ema21"].iloc[i]
        rsi_curr = df["rsi"].iloc[i]
        close_curr = df["close"].iloc[i]
        ema200 = df["ema200_1h"].iloc[i]
        
        if pd.isna(ema200) or pd.isna(rsi_curr):
            continue
        
        regime_bull = close_curr > ema200
        regime_bear = close_curr < ema200
        
        cross_up = (ema9_prev <= ema21_prev) and (ema9_curr > ema21_curr)
        if cross_up and 40 <= rsi_curr <= 65 and regime_bull:
            signals.append((i, "long"))
        
        cross_down = (ema9_prev >= ema21_prev) and (ema9_curr < ema21_curr)
        if cross_down and 35 <= rsi_curr <= 60 and regime_bear:
            signals.append((i, "short"))
    
    trades = simulate_trades(df, signals, tp_pct=0.03, sl_pct=0.015,
                              position_size=200, leverage=10, lookahead=100)
    return trades


# ─── BOT 2: Mean Reversion (BB + RSI, 15min) ────────────────────────────────

def run_bot2(symbol, df_1m_full):
    """Bot 2 — Mean Reversion (BB lower/upper touch + RSI + SAR, 15min)."""
    import ta as _ta
    
    # Use 15min candles (resample from 1min)
    df_work = df_1m_full.copy().set_index("datetime")
    df_15m = df_work.resample("15min").agg({
        "open": "first", "high": "max", "low": "min",
        "close": "last", "volume": "sum", "in_range": "last"
    }).dropna(subset=["open"]).reset_index()
    
    df = df_15m.copy()
    
    # Bollinger Bands (20, 2)
    bb = _ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()
    df["bb_mid"] = bb.bollinger_mavg()
    
    # RSI
    df["rsi"] = rsi_calc(df["close"], 14)
    
    # Parabolic SAR
    psar = _ta.trend.PSARIndicator(df["high"], df["low"], df["close"], step=0.02, max_step=0.2)
    df["psar"] = psar.psar()
    df["psar_up"] = psar.psar_up()
    
    in_range_mask = df["in_range"].fillna(False)
    
    signals = []
    for i in range(22, len(df) - 1):
        if not in_range_mask.iloc[i]:
            continue
        
        price = df["close"].iloc[i]
        rsi_val = df["rsi"].iloc[i]
        bb_lower = df["bb_lower"].iloc[i]
        bb_upper = df["bb_upper"].iloc[i]
        psar_up = df["psar_up"].iloc[i]
        
        if pd.isna(rsi_val) or pd.isna(bb_lower):
            continue
        
        sar_uptrend = pd.notna(psar_up)
        
        # Check RSI direction (turning from oversold/overbought)
        rsi_prev = df["rsi"].iloc[i - 1] if i > 0 else rsi_val
        rsi_rising = rsi_val > rsi_prev
        rsi_falling = rsi_val < rsi_prev
        
        # Long: price near/below lower BB + RSI < 40 + RSI starting to turn up
        if price <= bb_lower * 1.005 and rsi_val < 40 and rsi_rising:
            signals.append((i, "long"))
        
        # Short: price near/above upper BB + RSI > 60 + RSI starting to turn down
        if price >= bb_upper * 0.995 and rsi_val > 60 and rsi_falling:
            signals.append((i, "short"))
    
    # TP = distance to BB midline (~1%), SL = 0.5%
    trades = simulate_trades(df, signals, tp_pct=0.01, sl_pct=0.005,
                              position_size=150, leverage=10, lookahead=50)
    return trades


# ─── BOT 3: Momentum 1min, 30min lookback ─────────────────────────────────────

def run_bot3(symbol, df_1m_full):
    """Bot 3 — Momentum (2% move in 30min + 2x avg volume)."""
    df = df_1m_full.copy()
    
    lookback = 30
    vol_window = 50
    
    df["price_30m_ago"] = df["close"].shift(lookback)
    df["move_30m"] = (df["close"] - df["price_30m_ago"]) / df["price_30m_ago"]
    df["vol_avg"] = df["volume"].rolling(vol_window).mean()
    
    in_range_mask = df["in_range"].fillna(False)
    
    signals = []
    for i in range(vol_window + lookback, len(df) - 1):
        if not in_range_mask.iloc[i]:
            continue
        
        move = df["move_30m"].iloc[i]
        vol = df["volume"].iloc[i]
        vol_avg = df["vol_avg"].iloc[i]
        
        if pd.isna(move) or pd.isna(vol_avg) or vol_avg == 0:
            continue
        
        vol_ratio = vol / vol_avg
        
        if move >= 0.02 and vol_ratio >= 2.0:
            signals.append((i, "long"))
        elif move <= -0.02 and vol_ratio >= 2.0:
            signals.append((i, "short"))
    
    trades = simulate_trades(df, signals, tp_pct=0.03, sl_pct=0.01,
                              position_size=300, leverage=10, lookahead=60)
    return trades


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("BACKTESTING ENGINE — Last 100 Days")
    print("Data source: OKX (Bybit geo-blocked)")
    print("=" * 60)
    
    all_bot1_trades = []
    all_bot2_trades = []
    all_bot3_trades = []
    
    period_starts = []
    period_ends = []
    
    for symbol in SYMBOLS_OKX:
        print(f"\n{'─'*40}")
        print(f"Processing {symbol}...")
        print(f"{'─'*40}")
        
        # Extra warmup for EMA200 (200 hours = ~8.3 days)
        warmup_days = 12
        
        print("\nFetching 15min candles...")
        df_15m = fetch_klines_okx(symbol, "15m", DAYS, extra_days=2)
        
        print("Fetching 1H candles (regime filter warmup)...")
        df_1h = fetch_klines_okx(symbol, "1H", DAYS, extra_days=warmup_days)
        
        print("Fetching 1min candles...")
        df_1m = fetch_klines_okx(symbol, "1m", DAYS, extra_days=1)
        
        if df_15m.empty or df_1h.empty or df_1m.empty:
            print(f"  ERROR: No data for {symbol}, skipping.")
            continue
        
        in_range_15m = df_15m[df_15m["in_range"]]
        if not in_range_15m.empty:
            period_starts.append(in_range_15m["datetime"].iloc[0])
            period_ends.append(in_range_15m["datetime"].iloc[-1])
        
        print(f"\nRunning Bot 1 on {symbol}...")
        b1 = run_bot1(symbol, df_15m, df_1h)
        all_bot1_trades.extend(b1)
        print(f"  → {len(b1)} trades")
        
        print(f"Running Bot 2 on {symbol}...")
        b2 = run_bot2(symbol, df_1m)
        all_bot2_trades.extend(b2)
        print(f"  → {len(b2)} trades")
        
        print(f"Running Bot 3 on {symbol}...")
        b3 = run_bot3(symbol, df_1m)
        all_bot3_trades.extend(b3)
        print(f"  → {len(b3)} trades")
    
    # Stats
    s1 = compute_stats(all_bot1_trades, "Bot 1")
    s2 = compute_stats(all_bot2_trades, "Bot 2")
    s3 = compute_stats(all_bot3_trades, "Bot 3")
    
    period_str_start = min(period_starts).strftime("%Y-%m-%d") if period_starts else "N/A"
    period_str_end = max(period_ends).strftime("%Y-%m-%d") if period_ends else "N/A"
    
    combined_pnl = s1["total_pnl"] + s2["total_pnl"] + s3["total_pnl"]
    best_bot = max([s1, s2, s3], key=lambda x: x["total_pnl"])
    
    def recommend(s1, s2, s3, best):
        parts = []
        
        for s, name, desc in [
            (s1, "Bot 1 (Trend EMA 9/21)", "trending markets"),
            (s2, "Bot 2 (Mean Reversion BB+RSI)", "oversold/overbought reversals"),
            (s3, "Bot 3 (Momentum)", "breakout conditions"),
        ]:
            sign = "+" if s["total_pnl"] >= 0 else ""
            if s["total_pnl"] > 0:
                parts.append(f"{name} profitable (${sign}{s['total_pnl']:.0f}) — good for {desc}.")
            else:
                parts.append(f"{name} loss (${sign}{s['total_pnl']:.0f}) in this period — avoid in {desc} without tuning.")
        
        parts.append(f"**Best: {best['name']}** with ${best['total_pnl']:+.2f} total P&L over 100 days.")
        return " ".join(parts)
    
    recommendation = recommend(s1, s2, s3, best_bot)
    
    def fmt_stats(s, emoji, title):
        lines = [
            f"## {emoji} {title}",
            f"- Total Trades: {s['total_trades']}",
            f"- Win Rate: {s['win_rate']}%",
            f"- Total P&L: ${s['total_pnl']:+.2f}",
            f"- Avg Win: ${s['avg_win']:.2f} | Avg Loss: ${s['avg_loss']:.2f}",
            f"- Max Drawdown: ${s['max_drawdown']:.2f}",
            f"- Best Month: +${s['best_month']:.2f} | Worst Month: ${s['worst_month']:+.2f}",
        ]
        if s["monthly"]:
            lines.append("- Monthly Breakdown:")
            for month, val in s["monthly"].items():
                lines.append(f"  - {month}: ${val:+.2f}")
        return "\n".join(lines)
    
    report = f"""# Backtesting Results — Last 100 Days (BTCUSDT + ETHUSDT)
Period: {period_str_start} to {period_str_end}
Data source: OKX (perpetual swaps, equivalent pricing to Bybit)
Leverage: 10x | Fees: 0.055% per side

{fmt_stats(s1, "🤖", "Bot 1 — Trend (EMA 9/21, 15min)")}

{fmt_stats(s2, "⚡", "Bot 2 — Mean Reversion (BB+RSI+SAR, 15min)")}

{fmt_stats(s3, "🚀", "Bot 3 — Momentum (2% move, 30min)")}

## Combined Portfolio
- Total P&L: ${combined_pnl:+.2f}
- Best Strategy: {best_bot['name']} (${best_bot['total_pnl']:+.2f})
- Recommendation: {recommendation}
"""
    
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(report)
    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
