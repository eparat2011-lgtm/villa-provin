#!/usr/bin/env python3
"""
Market Regime Detector v2
Improvements over v1:
- EMA50 + EMA200 dual confirmation
- ADX threshold raised to 30 for crypto
- Confidence scoring (0-100)
- Regime change detection
- Cleaner direction logic
"""

import pandas as pd
import ta
from datetime import datetime


def detect_regime(df: pd.DataFrame) -> dict:
    """
    Detect market regime from 1H OHLCV dataframe.

    Returns:
        regime: 'uptrend' | 'downtrend' | 'sideways' | 'volatile'
        direction: 'long' | 'short' | 'neutral'
        confidence: 0-100 (how strong the signal is)
        allow_long: bool
        allow_short: bool
        reason: human-readable explanation
    """
    if len(df) < 210:
        return {
            "regime": "unknown",
            "direction": "neutral",
            "confidence": 0,
            "allow_long": False,
            "allow_short": False,
            "reason": "Not enough data (need 210+ candles)"
        }

    close = df["close"]
    high = df["high"]
    low = df["low"]
    current_price = float(close.iloc[-1])

    # ── EMAs ─────────────────────────────────────────────────────────────
    ema50  = float(ta.trend.ema_indicator(close, window=50).iloc[-1])
    ema200 = float(ta.trend.ema_indicator(close, window=200).iloc[-1])

    # ── ADX (trend strength, raised to 30 for crypto) ────────────────────
    adx_ind  = ta.trend.ADXIndicator(high, low, close, window=14)
    adx_val  = float(adx_ind.adx().iloc[-1])
    di_plus  = float(adx_ind.adx_pos().iloc[-1])
    di_minus = float(adx_ind.adx_neg().iloc[-1])

    # ── ATR (volatility) ─────────────────────────────────────────────────
    atr_val  = float(ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range().iloc[-1])
    atr_avg  = float(ta.volatility.AverageTrueRange(high, low, close, window=50).average_true_range().iloc[-1])
    atr_ratio = atr_val / atr_avg if atr_avg > 0 else 1.0

    # ── Regime classification ─────────────────────────────────────────────

    # 1. Volatile market — trade with extreme caution
    if atr_ratio > 2.0:
        return {
            "regime": "volatile",
            "direction": "neutral",
            "confidence": 20,
            "allow_long": False,
            "allow_short": False,
            "adx": round(adx_val, 1),
            "atr_ratio": round(atr_ratio, 2),
            "ema50": round(ema50, 2),
            "ema200": round(ema200, 2),
            "reason": f"⚡ High volatility (ATR {atr_ratio:.1f}x avg) — all trades paused"
        }

    # 2. Strong trend (ADX > 30, raised from 25 for crypto)
    if adx_val >= 30:
        # Strong uptrend: price > EMA50 > EMA200 AND DI+ > DI-
        if current_price > ema50 > ema200 and di_plus > di_minus:
            confidence = min(100, int(30 + (adx_val - 30) * 2 + (di_plus - di_minus)))
            return {
                "regime": "uptrend",
                "direction": "long",
                "confidence": confidence,
                "allow_long": True,
                "allow_short": False,  # No shorts against uptrend
                "adx": round(adx_val, 1),
                "atr_ratio": round(atr_ratio, 2),
                "ema50": round(ema50, 2),
                "ema200": round(ema200, 2),
                "reason": f"📈 Uptrend: price > EMA50 > EMA200, ADX={adx_val:.1f}, DI+={di_plus:.1f} > DI-={di_minus:.1f}"
            }

        # Strong downtrend: price < EMA50 < EMA200 AND DI- > DI+
        elif current_price < ema50 < ema200 and di_minus > di_plus:
            confidence = min(100, int(30 + (adx_val - 30) * 2 + (di_minus - di_plus)))
            return {
                "regime": "downtrend",
                "direction": "short",
                "confidence": confidence,
                "allow_long": False,  # No longs against downtrend
                "allow_short": True,
                "adx": round(adx_val, 1),
                "atr_ratio": round(atr_ratio, 2),
                "ema50": round(ema50, 2),
                "ema200": round(ema200, 2),
                "reason": f"📉 Downtrend: price < EMA50 < EMA200, ADX={adx_val:.1f}, DI-={di_minus:.1f} > DI+={di_plus:.1f}"
            }

    # 3. Weak trend / Sideways (ADX < 30 or EMAs not aligned)
    # Allow both directions but with lower confidence
    confidence = max(10, int(50 - (30 - min(adx_val, 30)) * 1.5))
    return {
        "regime": "sideways",
        "direction": "neutral",
        "confidence": confidence,
        "allow_long": True,
        "allow_short": True,
        "adx": round(adx_val, 1),
        "atr_ratio": round(atr_ratio, 2),
        "ema50": round(ema50, 2),
        "ema200": round(ema200, 2),
        "reason": f"↔️ Sideways: ADX={adx_val:.1f} (weak), EMA50={ema50:.0f}, EMA200={ema200:.0f}"
    }


def should_close_position(position_direction: str, regime: dict) -> bool:
    """
    Returns True if an open position should be closed due to regime change.
    
    Args:
        position_direction: 'long' or 'short'
        regime: output of detect_regime()
    """
    if position_direction == "long" and not regime.get("allow_long", True):
        return True
    if position_direction == "short" and not regime.get("allow_short", True):
        return True
    return False


def get_position_size(base_size: float, regime: dict) -> float:
    """
    Adjust position size based on regime confidence.
    
    High confidence (>70): full size
    Medium confidence (40-70): 75% size
    Low confidence (<40): 50% size
    """
    confidence = regime.get("confidence", 50)

    if confidence >= 70:
        multiplier = 1.0
    elif confidence >= 40:
        multiplier = 0.75
    else:
        multiplier = 0.5

    size = base_size * multiplier
    return round(size / 25) * 25  # Round to nearest $25


if __name__ == "__main__":
    # Quick test with Bybit data
    from pybit.unified_trading import HTTP
    import os
    from dotenv import load_dotenv

    load_dotenv("/home/marian_rachow/btc-bot/.env")
    c = HTTP(api_key=os.getenv("BYBIT_API_KEY"), api_secret=os.getenv("BYBIT_API_SECRET"))

    r = c.get_kline(category="linear", symbol="BTCUSDT", interval="60", limit=250)
    candles = r["result"]["list"]
    df = pd.DataFrame(candles, columns=["ts","open","high","low","close","vol","turnover"])
    df = df.astype({"close": float, "open": float, "high": float, "low": float})
    df = df.iloc[::-1].reset_index(drop=True)

    result = detect_regime(df)
    print(f"\n{'='*50}")
    print(f"BTCUSDT Regime: {result['regime'].upper()}")
    print(f"Direction: {result['direction']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"Allow Long: {result['allow_long']}")
    print(f"Allow Short: {result['allow_short']}")
    print(f"ADX: {result['adx']}")
    print(f"EMA50: ${result['ema50']:,.0f} | EMA200: ${result['ema200']:,.0f}")
    print(f"Reason: {result['reason']}")
    print(f"\nPosition size ($200 base): ${get_position_size(200, result)}")
    print(f"{'='*50}\n")
