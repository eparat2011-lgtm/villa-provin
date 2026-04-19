#!/usr/bin/env python3
"""
Infinity Algo Trading Simulation
Signals extracted from TradingView screenshots
"""

from collections import defaultdict

# ── Signal Data ──────────────────────────────────────────────────────────────
signals_raw = [
    # February 2025 (bear market)
    {"date": "2025-02-10", "type": "normal_buy",  "price": 97000,  "direction": "long"},
    {"date": "2025-02-17", "type": "smart_sell",  "price": 97000,  "direction": "short"},
    {"date": "2025-02-18", "type": "tp",           "price": 95000,  "direction": "tp_short"},
    {"date": "2025-02-19", "type": "tp",           "price": 93000,  "direction": "tp_short"},
    {"date": "2025-02-22", "type": "tp",           "price": 90000,  "direction": "tp_short"},
    {"date": "2025-02-23", "type": "smart_buy",   "price": 85000,  "direction": "long"},
    {"date": "2025-02-25", "type": "smart_sell",  "price": 87000,  "direction": "short"},
    {"date": "2025-02-26", "type": "tp",           "price": 84000,  "direction": "tp_short"},
    {"date": "2025-02-27", "type": "tp",           "price": 80000,  "direction": "tp_short"},
    {"date": "2025-02-28", "type": "tp",           "price": 75000,  "direction": "tp_short"},
    # March 2025
    {"date": "2025-03-01", "type": "tp",           "price": 70000,  "direction": "tp_short"},
    {"date": "2025-03-03", "type": "tp",           "price": 66000,  "direction": "tp_short"},
    {"date": "2025-03-05", "type": "normal_buy",  "price": 62000,  "direction": "long"},
    {"date": "2025-03-07", "type": "smart_buy",   "price": 64000,  "direction": "long"},
    {"date": "2025-03-08", "type": "tp",           "price": 66000,  "direction": "tp_long"},
    {"date": "2025-03-09", "type": "tp",           "price": 68000,  "direction": "tp_long"},
    {"date": "2025-03-10", "type": "tp",           "price": 71000,  "direction": "tp_long"},
    # May 2025
    {"date": "2025-05-02", "type": "smart_sell",  "price": 113000, "direction": "short"},
    {"date": "2025-05-04", "type": "smart_buy",   "price": 110000, "direction": "long"},
    {"date": "2025-05-05", "type": "tp",           "price": 111000, "direction": "tp_long"},
    {"date": "2025-05-06", "type": "tp",           "price": 112000, "direction": "tp_long"},
    {"date": "2025-05-07", "type": "tp",           "price": 113000, "direction": "tp_long"},
    {"date": "2025-05-10", "type": "normal_sell", "price": 125000, "direction": "short"},
    {"date": "2025-05-11", "type": "tp",           "price": 123000, "direction": "tp_short"},
    {"date": "2025-05-12", "type": "tp",           "price": 122000, "direction": "tp_short"},
    {"date": "2025-05-13", "type": "smart_sell",  "price": 126000, "direction": "short"},
    {"date": "2025-05-16", "type": "smart_buy",   "price": 117000, "direction": "long"},
    {"date": "2025-05-17", "type": "smart_sell",  "price": 120000, "direction": "short"},
    {"date": "2025-05-18", "type": "tp",           "price": 119000, "direction": "tp_short"},
    {"date": "2025-05-22", "type": "smart_sell",  "price": 118000, "direction": "short"},
    {"date": "2025-05-23", "type": "tp",           "price": 110000, "direction": "tp_short"},
    {"date": "2025-05-23", "type": "smart_buy",   "price": 110000, "direction": "long"},
    {"date": "2025-05-24", "type": "smart_sell",  "price": 115000, "direction": "short"},
    # August 2025
    {"date": "2025-08-21", "type": "smart_buy",   "price": 107000, "direction": "long"},
    {"date": "2025-08-22", "type": "tp",           "price": 110000, "direction": "tp_long"},
    {"date": "2025-08-24", "type": "tp",           "price": 111000, "direction": "tp_long"},
    {"date": "2025-08-25", "type": "tp",           "price": 112000, "direction": "tp_long"},
    {"date": "2025-08-28", "type": "smart_sell",  "price": 113000, "direction": "short"},
    {"date": "2025-08-29", "type": "smart_buy",   "price": 108000, "direction": "long"},
    {"date": "2025-08-30", "type": "tp",           "price": 109000, "direction": "tp_long"},
    {"date": "2025-08-31", "type": "smart_sell",  "price": 112000, "direction": "short"},
    # September 2025
    {"date": "2025-09-01", "type": "normal_buy",  "price": 106000, "direction": "long"},
    {"date": "2025-09-02", "type": "smart_sell",  "price": 112000, "direction": "short"},
    {"date": "2025-09-04", "type": "smart_buy",   "price": 107000, "direction": "long"},
    {"date": "2025-09-07", "type": "smart_buy",   "price": 108000, "direction": "long"},
    {"date": "2025-09-10", "type": "tp",           "price": 113000, "direction": "tp_long"},
    {"date": "2025-09-10", "type": "smart_sell",  "price": 115000, "direction": "short"},
    {"date": "2025-09-11", "type": "smart_buy",   "price": 110000, "direction": "long"},
    {"date": "2025-09-13", "type": "normal_sell", "price": 115000, "direction": "short"},
    {"date": "2025-09-15", "type": "smart_buy",   "price": 112000, "direction": "long"},
    {"date": "2025-09-17", "type": "smart_sell",  "price": 115000, "direction": "short"},
    {"date": "2025-09-22", "type": "smart_sell",  "price": 115000, "direction": "short"},
    {"date": "2025-09-24", "type": "smart_buy",   "price": 109000, "direction": "long"},
    {"date": "2025-09-27", "type": "normal_buy",  "price": 105000, "direction": "long"},
    {"date": "2025-09-28", "type": "smart_buy",   "price": 109000, "direction": "long"},
    {"date": "2025-09-30", "type": "tp",           "price": 115000, "direction": "tp_long"},
    # October 2025
    {"date": "2025-10-01", "type": "smart_buy",   "price": 109000, "direction": "long"},
    {"date": "2025-10-02", "type": "tp",           "price": 112000, "direction": "tp_long"},
    {"date": "2025-10-03", "type": "tp",           "price": 116000, "direction": "tp_long"},
    {"date": "2025-10-04", "type": "tp",           "price": 120000, "direction": "tp_long"},
    {"date": "2025-10-05", "type": "tp",           "price": 124000, "direction": "tp_long"},
    {"date": "2025-10-05", "type": "smart_sell",  "price": 128000, "direction": "short"},
    {"date": "2025-10-06", "type": "tp",           "price": 124000, "direction": "tp_short"},
    {"date": "2025-10-07", "type": "tp",           "price": 120000, "direction": "tp_short"},
    {"date": "2025-10-08", "type": "smart_buy",   "price": 120000, "direction": "long"},
    {"date": "2025-10-10", "type": "smart_sell",  "price": 125000, "direction": "short"},
    {"date": "2025-10-10", "type": "tp",           "price": 122000, "direction": "tp_short"},
    {"date": "2025-10-11", "type": "tp",           "price": 118000, "direction": "tp_short"},
    {"date": "2025-10-11", "type": "tp",           "price": 116000, "direction": "tp_short"},
    {"date": "2025-10-19", "type": "smart_buy",   "price": 106000, "direction": "long"},
    {"date": "2025-10-20", "type": "tp",           "price": 112000, "direction": "tp_long"},
    {"date": "2025-10-21", "type": "smart_sell",  "price": 112000, "direction": "short"},
    # March 2026
    {"date": "2026-03-05", "type": "smart_sell",  "price": 74000,  "direction": "short"},
    {"date": "2026-03-06", "type": "tp",           "price": 72000,  "direction": "tp_short"},
    {"date": "2026-03-07", "type": "tp",           "price": 71000,  "direction": "tp_short"},
    {"date": "2026-03-09", "type": "smart_buy",   "price": 70000,  "direction": "long"},
    {"date": "2026-03-11", "type": "tp",           "price": 72000,  "direction": "tp_long"},
    {"date": "2026-03-17", "type": "smart_sell",  "price": 74500,  "direction": "short"},
    {"date": "2026-03-18", "type": "tp",           "price": 73000,  "direction": "tp_short"},
    {"date": "2026-03-19", "type": "tp",           "price": 71000,  "direction": "tp_short"},
    {"date": "2026-03-20", "type": "tp",           "price": 70000,  "direction": "tp_short"},
    {"date": "2026-03-22", "type": "tp",           "price": 68500,  "direction": "tp_short"},
]

# Sort chronologically
signals_raw.sort(key=lambda x: x["date"])

# ── Parameters ───────────────────────────────────────────────────────────────
INITIAL_CAPITAL = 2000.0
LEVERAGE = 10
FEE_RATE = 0.00055  # per side → 0.0011 round-trip

def get_position_size(signal_type):
    if signal_type in ["smart_buy", "smart_sell"]:
        return 250
    elif signal_type in ["normal_buy", "normal_sell"]:
        return 200
    return 200

# ── Simulation State ─────────────────────────────────────────────────────────
capital = INITIAL_CAPITAL
trade_log = []          # list of closed trade dicts
monthly_pnl = defaultdict(float)

# Active position
pos = None  # dict: direction, entry_price, size_usd, tp_count, remaining_fraction, breakeven_set

def month_key(date_str):
    return date_str[:7]  # "YYYY-MM"

def calc_pnl(direction, entry, exit_price, notional):
    """Notional = position_size_usd * leverage"""
    if direction == "long":
        return (exit_price - entry) / entry * notional
    else:  # short
        return (entry - exit_price) / entry * notional

def fees(notional):
    return notional * 0.0011  # open + close

def close_position(pos, exit_price, fraction, reason, date):
    """Close `fraction` of remaining position. Returns realised PnL."""
    closed_size = pos["size_usd"] * pos["remaining_fraction"] * fraction
    notional = closed_size * LEVERAGE
    pnl = calc_pnl(pos["direction"], pos["entry_price"], exit_price, notional)
    f = fees(notional)
    net = pnl - f
    pos["remaining_fraction"] *= (1 - fraction)

    win = net > 0
    trade_log.append({
        "date": date,
        "action": reason,
        "direction": pos["direction"],
        "entry": pos["entry_price"],
        "exit": exit_price,
        "size_usd": round(closed_size, 2),
        "notional": round(notional, 2),
        "gross_pnl": round(pnl, 2),
        "fees": round(f, 2),
        "net_pnl": round(net, 2),
        "win": win,
    })
    return net

# ── Main Loop ─────────────────────────────────────────────────────────────────
for sig in signals_raw:
    date  = sig["date"]
    stype = sig["type"]
    price = sig["price"]
    dirn  = sig["direction"]
    mo    = month_key(date)

    is_entry = stype in ["smart_buy", "smart_sell", "normal_buy", "normal_sell"]
    is_tp    = stype == "tp"

    if is_entry:
        new_direction = "long" if dirn == "long" else "short"

        # If open position in opposite direction → force-close 100%
        if pos is not None:
            existing = pos["direction"]
            if existing != new_direction:
                # Close entire remaining position at this signal's price
                net = close_position(pos, price, 1.0, "direction_change_close", date)
                capital += net
                monthly_pnl[mo] += net
                trade_log[-1]["note"] = f"Closed {existing} @ {price} on {new_direction} signal"
                pos = None

            else:
                # Same direction — add-on entry; close old first conservatively (no action, skip new)
                # In real algo, overlapping same-dir entries just add; here we skip to avoid double-counting
                # Log as "skipped - same direction already open"
                trade_log.append({
                    "date": date,
                    "action": "skipped_entry",
                    "direction": new_direction,
                    "entry": price,
                    "note": f"Already in {existing} position — skipped duplicate entry",
                    "net_pnl": 0,
                    "win": None,
                })
                continue

        # Open new position
        size_usd = get_position_size(stype)
        pos = {
            "direction": new_direction,
            "entry_price": price,
            "size_usd": size_usd,
            "tp_count": 0,
            "remaining_fraction": 1.0,
            "breakeven_set": False,
        }
        trade_log.append({
            "date": date,
            "action": "open",
            "direction": new_direction,
            "entry": price,
            "size_usd": size_usd,
            "net_pnl": 0,
            "win": None,
            "note": f"Open {new_direction} @ {price}, size=${size_usd}",
        })

    elif is_tp:
        if pos is None:
            # No open position — orphan TP, skip
            continue

        # Check TP direction matches open position
        tp_dir = "long" if dirn == "tp_long" else "short"
        if tp_dir != pos["direction"]:
            continue  # stale TP for old direction

        pos["tp_count"] += 1

        if pos["tp_count"] == 1:
            # TP1 → set breakeven, no close
            pos["breakeven_set"] = True
            trade_log.append({
                "date": date,
                "action": "tp1_breakeven",
                "direction": pos["direction"],
                "entry": pos["entry_price"],
                "exit": price,
                "note": f"TP1 hit @ {price} — SL moved to breakeven",
                "net_pnl": 0,
                "win": None,
            })
        else:
            # TP2+ → close 25% of remaining
            net = close_position(pos, price, 0.25, f"tp{pos['tp_count']}_partial_close", date)
            capital += net
            monthly_pnl[mo] += net
            trade_log[-1]["note"] = f"TP{pos['tp_count']} @ {price} — closed 25% of remaining"

            # If remaining is negligible, close it out
            if pos["remaining_fraction"] < 0.05:
                pos = None

# ── Close any open position at last signal price ──────────────────────────────
if pos is not None:
    last = signals_raw[-1]
    net = close_position(pos, last["price"], 1.0, "end_of_period_close", last["date"])
    capital += net
    monthly_pnl[month_key(last["date"])] += net
    trade_log[-1]["note"] = "Closed at end of simulation period"
    pos = None

# ── Build Report ──────────────────────────────────────────────────────────────
total_pnl = capital - INITIAL_CAPITAL

closed_trades = [t for t in trade_log if t.get("win") is not None and t["win"] is not None]
winning_trades = [t for t in closed_trades if t["win"]]
losing_trades  = [t for t in closed_trades if not t["win"]]

win_rate = len(winning_trades) / len(closed_trades) * 100 if closed_trades else 0

# Best / worst month
if monthly_pnl:
    best_mo  = max(monthly_pnl, key=monthly_pnl.get)
    worst_mo = min(monthly_pnl, key=monthly_pnl.get)
else:
    best_mo = worst_mo = "N/A"

MONTH_NAMES = {
    "2025-02": "Feb 2025", "2025-03": "Mar 2025", "2025-04": "Apr 2025",
    "2025-05": "May 2025", "2025-06": "Jun 2025", "2025-07": "Jul 2025",
    "2025-08": "Aug 2025", "2025-09": "Sep 2025", "2025-10": "Oct 2025",
    "2025-11": "Nov 2025", "2025-12": "Dec 2025", "2026-01": "Jan 2026",
    "2026-02": "Feb 2026", "2026-03": "Mar 2026",
}

def mn(k):
    return MONTH_NAMES.get(k, k)

# ── Console summary ───────────────────────────────────────────────────────────
print("=" * 60)
print("INFINITY ALGO SIMULATION — 12 MONTHS")
print("=" * 60)
print(f"Period:          Feb 2025 — Mar 2026")
print(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
print(f"Final Capital:   ${capital:,.2f}")
print(f"Total P&L:       ${total_pnl:+,.2f}  ({total_pnl/INITIAL_CAPITAL*100:+.1f}%)")
print(f"Total Trades:    {len(closed_trades)}")
print(f"Winning Trades:  {len(winning_trades)} ({win_rate:.1f}%)")
print(f"Losing Trades:   {len(losing_trades)}")
print(f"Best Month:      {mn(best_mo)}  ${monthly_pnl[best_mo]:+,.2f}")
print(f"Worst Month:     {mn(worst_mo)}  ${monthly_pnl[worst_mo]:+,.2f}")
print()
print("Monthly Breakdown:")
for mo in sorted(monthly_pnl):
    print(f"  {mn(mo):12s}  ${monthly_pnl[mo]:+,.2f}")
print("=" * 60)

# ── Write Markdown Report ─────────────────────────────────────────────────────
lines = []
lines.append("# Infinity Algo Simulation — 12 Months")
lines.append("")
lines.append("**Period:** Feb 2025 — March 2026  ")
lines.append("**Initial Capital:** $2,000  ")
lines.append("**Parameters:** 10× leverage | TP1 = breakeven | TP2+ = 25% partial close | Fee: 0.055%/side")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## Summary")
lines.append("")
lines.append(f"| Metric | Value |")
lines.append(f"|--------|-------|")
lines.append(f"| Total Trades (closed) | {len(closed_trades)} |")
lines.append(f"| Winning Trades | {len(winning_trades)} ({win_rate:.1f}%) |")
lines.append(f"| Losing Trades | {len(losing_trades)} |")
lines.append(f"| Total P&L | **${total_pnl:+,.2f}** |")
lines.append(f"| Final Capital | **${capital:,.2f}** |")
lines.append(f"| Return on Capital | **{total_pnl/INITIAL_CAPITAL*100:+.1f}%** |")
lines.append(f"| Best Month | {mn(best_mo)}  ${monthly_pnl[best_mo]:+,.2f} |")
lines.append(f"| Worst Month | {mn(worst_mo)}  ${monthly_pnl[worst_mo]:+,.2f} |")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## Monthly Breakdown")
lines.append("")
lines.append("| Month | P&L |")
lines.append("|-------|-----|")
running = INITIAL_CAPITAL
for mo in sorted(monthly_pnl):
    pnl_mo = monthly_pnl[mo]
    running += pnl_mo
    lines.append(f"| {mn(mo)} | ${pnl_mo:+,.2f} |")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## Trade List")
lines.append("")
lines.append("| # | Date | Action | Dir | Entry | Exit | Size $ | Notional | Gross P&L | Fees | Net P&L | Note |")
lines.append("|---|------|--------|-----|-------|------|--------|----------|-----------|------|---------|------|")

counter = 0
for t in trade_log:
    if t["action"] in ("open", "tp1_breakeven", "skipped_entry"):
        entry_str = f"${t.get('entry', '-'):,}" if t.get('entry') else "-"
        exit_str  = f"${t.get('exit', '-'):,}"  if t.get('exit')  else "-"
        size_str  = f"${t.get('size_usd', '-')}" if t.get('size_usd') else "-"
        note = t.get("note", "")
        lines.append(f"| — | {t['date']} | {t['action']} | {t.get('direction','-')} | {entry_str} | {exit_str} | {size_str} | — | — | — | — | {note} |")
    elif t.get("net_pnl") is not None and t["action"] not in ("open",):
        counter += 1
        sign = "✅" if t.get("win") else ("❌" if t.get("win") is False else "ℹ️")
        lines.append(
            f"| {counter} | {t['date']} | {t['action']} {sign} | {t.get('direction','-')} "
            f"| ${t.get('entry',0):,} | ${t.get('exit',0):,} "
            f"| ${t.get('size_usd',0):,.0f} | ${t.get('notional',0):,.0f} "
            f"| ${t.get('gross_pnl',0):+,.2f} | ${t.get('fees',0):,.2f} "
            f"| ${t.get('net_pnl',0):+,.2f} | {t.get('note','')} |"
        )

lines.append("")
lines.append("---")
lines.append("")
lines.append("## Notes & Methodology")
lines.append("")
lines.append("- **TP1** = SL moved to breakeven, no capital realised")
lines.append("- **TP2+** = 25% of remaining position closed each hit")
lines.append("- **Direction change** = 100% position closed at new signal's price")
lines.append("- **Duplicate same-direction entries** = skipped (conservative — no averaging up)")
lines.append("- **Fees** = 0.055% × 2 (open + close) applied to notional")
lines.append("- **Position sizing**: Smart signals = $250, Normal signals = $200 (collateral)")
lines.append("- Notional = collateral × 10× leverage")
lines.append(f"- Simulation generated from {len(signals_raw)} raw signal events")

output = "\n".join(lines)

with open("/home/marian_rachow/.openclaw/workspace/simulation_results.md", "w") as f:
    f.write(output)

print("\n✅ Results saved to simulation_results.md")
