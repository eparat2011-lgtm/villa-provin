# Infinity Algo Simulation — 12 Months

**Period:** Feb 2025 — March 2026  
**Initial Capital:** $2,000  
**Parameters:** 10× leverage | TP1 = breakeven | TP2+ = 25% partial close | Fee: 0.055%/side

---

## Summary

| Metric | Value |
|--------|-------|
| Total Trades (closed) | 57 |
| Winning Trades | 56 (98.2%) |
| Losing Trades | 1 |
| Total P&L | **$+6,210.07** |
| Final Capital | **$8,210.07** |
| Return on Capital | **+310.5%** |
| Best Month | May 2025  $+1,684.57 |
| Worst Month | Feb 2025  $+398.43 |

---

## Monthly Breakdown

| Month | P&L |
|-------|-----|
| Feb 2025 | $+398.43 |
| Mar 2025 | $+459.96 |
| May 2025 | $+1,684.57 |
| Aug 2025 | $+490.25 |
| Sep 2025 | $+993.91 |
| Oct 2025 | $+927.63 |
| Mar 2026 | $+1,255.32 |

---

## Trade List

| # | Date | Action | Dir | Entry | Exit | Size $ | Notional | Gross P&L | Fees | Net P&L | Note |
|---|------|--------|-----|-------|------|--------|----------|-----------|------|---------|------|
| — | 2025-02-10 | open | long | $97,000 | - | $200 | — | — | — | — | Open long @ 97000, size=$200 |
| 1 | 2025-02-17 | direction_change_close ❌ | long | $97,000 | $97,000 | $200 | $2,000 | $+0.00 | $2.20 | $-2.20 | Closed long @ 97000 on short signal |
| — | 2025-02-17 | open | short | $97,000 | - | $250 | — | — | — | — | Open short @ 97000, size=$250 |
| — | 2025-02-18 | tp1_breakeven | short | $97,000 | $95,000 | - | — | — | — | — | TP1 hit @ 95000 — SL moved to breakeven |
| 2 | 2025-02-19 | tp2_partial_close ✅ | short | $97,000 | $93,000 | $62 | $625 | $+25.77 | $0.69 | $+25.09 | TP2 @ 93000 — closed 25% of remaining |
| 3 | 2025-02-22 | tp3_partial_close ✅ | short | $97,000 | $90,000 | $47 | $469 | $+33.83 | $0.52 | $+33.31 | TP3 @ 90000 — closed 25% of remaining |
| 4 | 2025-02-23 | direction_change_close ✅ | short | $97,000 | $85,000 | $141 | $1,406 | $+173.97 | $1.55 | $+172.42 | Closed short @ 85000 on long signal |
| — | 2025-02-23 | open | long | $85,000 | - | $250 | — | — | — | — | Open long @ 85000, size=$250 |
| 5 | 2025-02-25 | direction_change_close ✅ | long | $85,000 | $87,000 | $250 | $2,500 | $+58.82 | $2.75 | $+56.07 | Closed long @ 87000 on short signal |
| — | 2025-02-25 | open | short | $87,000 | - | $250 | — | — | — | — | Open short @ 87000, size=$250 |
| — | 2025-02-26 | tp1_breakeven | short | $87,000 | $84,000 | - | — | — | — | — | TP1 hit @ 84000 — SL moved to breakeven |
| 6 | 2025-02-27 | tp2_partial_close ✅ | short | $87,000 | $80,000 | $62 | $625 | $+50.29 | $0.69 | $+49.60 | TP2 @ 80000 — closed 25% of remaining |
| 7 | 2025-02-28 | tp3_partial_close ✅ | short | $87,000 | $75,000 | $47 | $469 | $+64.66 | $0.52 | $+64.14 | TP3 @ 75000 — closed 25% of remaining |
| 8 | 2025-03-01 | tp4_partial_close ✅ | short | $87,000 | $70,000 | $35 | $352 | $+68.70 | $0.39 | $+68.31 | TP4 @ 70000 — closed 25% of remaining |
| 9 | 2025-03-03 | tp5_partial_close ✅ | short | $87,000 | $66,000 | $26 | $264 | $+63.64 | $0.29 | $+63.35 | TP5 @ 66000 — closed 25% of remaining |
| 10 | 2025-03-05 | direction_change_close ✅ | short | $87,000 | $62,000 | $79 | $791 | $+227.30 | $0.87 | $+226.43 | Closed short @ 62000 on long signal |
| — | 2025-03-05 | open | long | $62,000 | - | $200 | — | — | — | — | Open long @ 62000, size=$200 |
| — | 2025-03-07 | skipped_entry | long | $64,000 | - | - | — | — | — | — | Already in long position — skipped duplicate entry |
| — | 2025-03-08 | tp1_breakeven | long | $62,000 | $66,000 | - | — | — | — | — | TP1 hit @ 66000 — SL moved to breakeven |
| 11 | 2025-03-09 | tp2_partial_close ✅ | long | $62,000 | $68,000 | $50 | $500 | $+48.39 | $0.55 | $+47.84 | TP2 @ 68000 — closed 25% of remaining |
| 12 | 2025-03-10 | tp3_partial_close ✅ | long | $62,000 | $71,000 | $38 | $375 | $+54.44 | $0.41 | $+54.02 | TP3 @ 71000 — closed 25% of remaining |
| 13 | 2025-05-02 | direction_change_close ✅ | long | $62,000 | $113,000 | $112 | $1,125 | $+925.40 | $1.24 | $+924.17 | Closed long @ 113000 on short signal |
| — | 2025-05-02 | open | short | $113,000 | - | $250 | — | — | — | — | Open short @ 113000, size=$250 |
| 14 | 2025-05-04 | direction_change_close ✅ | short | $113,000 | $110,000 | $250 | $2,500 | $+66.37 | $2.75 | $+63.62 | Closed short @ 110000 on long signal |
| — | 2025-05-04 | open | long | $110,000 | - | $250 | — | — | — | — | Open long @ 110000, size=$250 |
| — | 2025-05-05 | tp1_breakeven | long | $110,000 | $111,000 | - | — | — | — | — | TP1 hit @ 111000 — SL moved to breakeven |
| 15 | 2025-05-06 | tp2_partial_close ✅ | long | $110,000 | $112,000 | $62 | $625 | $+11.36 | $0.69 | $+10.68 | TP2 @ 112000 — closed 25% of remaining |
| 16 | 2025-05-07 | tp3_partial_close ✅ | long | $110,000 | $113,000 | $47 | $469 | $+12.78 | $0.52 | $+12.27 | TP3 @ 113000 — closed 25% of remaining |
| 17 | 2025-05-10 | direction_change_close ✅ | long | $110,000 | $125,000 | $141 | $1,406 | $+191.76 | $1.55 | $+190.21 | Closed long @ 125000 on short signal |
| — | 2025-05-10 | open | short | $125,000 | - | $200 | — | — | — | — | Open short @ 125000, size=$200 |
| — | 2025-05-11 | tp1_breakeven | short | $125,000 | $123,000 | - | — | — | — | — | TP1 hit @ 123000 — SL moved to breakeven |
| 18 | 2025-05-12 | tp2_partial_close ✅ | short | $125,000 | $122,000 | $50 | $500 | $+12.00 | $0.55 | $+11.45 | TP2 @ 122000 — closed 25% of remaining |
| — | 2025-05-13 | skipped_entry | short | $126,000 | - | - | — | — | — | — | Already in short position — skipped duplicate entry |
| 19 | 2025-05-16 | direction_change_close ✅ | short | $125,000 | $117,000 | $150 | $1,500 | $+96.00 | $1.65 | $+94.35 | Closed short @ 117000 on long signal |
| — | 2025-05-16 | open | long | $117,000 | - | $250 | — | — | — | — | Open long @ 117000, size=$250 |
| 20 | 2025-05-17 | direction_change_close ✅ | long | $117,000 | $120,000 | $250 | $2,500 | $+64.10 | $2.75 | $+61.35 | Closed long @ 120000 on short signal |
| — | 2025-05-17 | open | short | $120,000 | - | $250 | — | — | — | — | Open short @ 120000, size=$250 |
| — | 2025-05-18 | tp1_breakeven | short | $120,000 | $119,000 | - | — | — | — | — | TP1 hit @ 119000 — SL moved to breakeven |
| — | 2025-05-22 | skipped_entry | short | $118,000 | - | - | — | — | — | — | Already in short position — skipped duplicate entry |
| 21 | 2025-05-23 | tp2_partial_close ✅ | short | $120,000 | $110,000 | $62 | $625 | $+52.08 | $0.69 | $+51.40 | TP2 @ 110000 — closed 25% of remaining |
| 22 | 2025-05-23 | direction_change_close ✅ | short | $120,000 | $110,000 | $188 | $1,875 | $+156.25 | $2.06 | $+154.19 | Closed short @ 110000 on long signal |
| — | 2025-05-23 | open | long | $110,000 | - | $250 | — | — | — | — | Open long @ 110000, size=$250 |
| 23 | 2025-05-24 | direction_change_close ✅ | long | $110,000 | $115,000 | $250 | $2,500 | $+113.64 | $2.75 | $+110.89 | Closed long @ 115000 on short signal |
| — | 2025-05-24 | open | short | $115,000 | - | $250 | — | — | — | — | Open short @ 115000, size=$250 |
| 24 | 2025-08-21 | direction_change_close ✅ | short | $115,000 | $107,000 | $250 | $2,500 | $+173.91 | $2.75 | $+171.16 | Closed short @ 107000 on long signal |
| — | 2025-08-21 | open | long | $107,000 | - | $250 | — | — | — | — | Open long @ 107000, size=$250 |
| — | 2025-08-22 | tp1_breakeven | long | $107,000 | $110,000 | - | — | — | — | — | TP1 hit @ 110000 — SL moved to breakeven |
| 25 | 2025-08-24 | tp2_partial_close ✅ | long | $107,000 | $111,000 | $62 | $625 | $+23.36 | $0.69 | $+22.68 | TP2 @ 111000 — closed 25% of remaining |
| 26 | 2025-08-25 | tp3_partial_close ✅ | long | $107,000 | $112,000 | $47 | $469 | $+21.90 | $0.52 | $+21.39 | TP3 @ 112000 — closed 25% of remaining |
| 27 | 2025-08-28 | direction_change_close ✅ | long | $107,000 | $113,000 | $141 | $1,406 | $+78.86 | $1.55 | $+77.31 | Closed long @ 113000 on short signal |
| — | 2025-08-28 | open | short | $113,000 | - | $250 | — | — | — | — | Open short @ 113000, size=$250 |
| 28 | 2025-08-29 | direction_change_close ✅ | short | $113,000 | $108,000 | $250 | $2,500 | $+110.62 | $2.75 | $+107.87 | Closed short @ 108000 on long signal |
| — | 2025-08-29 | open | long | $108,000 | - | $250 | — | — | — | — | Open long @ 108000, size=$250 |
| — | 2025-08-30 | tp1_breakeven | long | $108,000 | $109,000 | - | — | — | — | — | TP1 hit @ 109000 — SL moved to breakeven |
| 29 | 2025-08-31 | direction_change_close ✅ | long | $108,000 | $112,000 | $250 | $2,500 | $+92.59 | $2.75 | $+89.84 | Closed long @ 112000 on short signal |
| — | 2025-08-31 | open | short | $112,000 | - | $250 | — | — | — | — | Open short @ 112000, size=$250 |
| 30 | 2025-09-01 | direction_change_close ✅ | short | $112,000 | $106,000 | $250 | $2,500 | $+133.93 | $2.75 | $+131.18 | Closed short @ 106000 on long signal |
| — | 2025-09-01 | open | long | $106,000 | - | $200 | — | — | — | — | Open long @ 106000, size=$200 |
| 31 | 2025-09-02 | direction_change_close ✅ | long | $106,000 | $112,000 | $200 | $2,000 | $+113.21 | $2.20 | $+111.01 | Closed long @ 112000 on short signal |
| — | 2025-09-02 | open | short | $112,000 | - | $250 | — | — | — | — | Open short @ 112000, size=$250 |
| 32 | 2025-09-04 | direction_change_close ✅ | short | $112,000 | $107,000 | $250 | $2,500 | $+111.61 | $2.75 | $+108.86 | Closed short @ 107000 on long signal |
| — | 2025-09-04 | open | long | $107,000 | - | $250 | — | — | — | — | Open long @ 107000, size=$250 |
| — | 2025-09-07 | skipped_entry | long | $108,000 | - | - | — | — | — | — | Already in long position — skipped duplicate entry |
| — | 2025-09-10 | tp1_breakeven | long | $107,000 | $113,000 | - | — | — | — | — | TP1 hit @ 113000 — SL moved to breakeven |
| 33 | 2025-09-10 | direction_change_close ✅ | long | $107,000 | $115,000 | $250 | $2,500 | $+186.92 | $2.75 | $+184.17 | Closed long @ 115000 on short signal |
| — | 2025-09-10 | open | short | $115,000 | - | $250 | — | — | — | — | Open short @ 115000, size=$250 |
| 34 | 2025-09-11 | direction_change_close ✅ | short | $115,000 | $110,000 | $250 | $2,500 | $+108.70 | $2.75 | $+105.95 | Closed short @ 110000 on long signal |
| — | 2025-09-11 | open | long | $110,000 | - | $250 | — | — | — | — | Open long @ 110000, size=$250 |
| 35 | 2025-09-13 | direction_change_close ✅ | long | $110,000 | $115,000 | $250 | $2,500 | $+113.64 | $2.75 | $+110.89 | Closed long @ 115000 on short signal |
| — | 2025-09-13 | open | short | $115,000 | - | $200 | — | — | — | — | Open short @ 115000, size=$200 |
| 36 | 2025-09-15 | direction_change_close ✅ | short | $115,000 | $112,000 | $200 | $2,000 | $+52.17 | $2.20 | $+49.97 | Closed short @ 112000 on long signal |
| — | 2025-09-15 | open | long | $112,000 | - | $250 | — | — | — | — | Open long @ 112000, size=$250 |
| 37 | 2025-09-17 | direction_change_close ✅ | long | $112,000 | $115,000 | $250 | $2,500 | $+66.96 | $2.75 | $+64.21 | Closed long @ 115000 on short signal |
| — | 2025-09-17 | open | short | $115,000 | - | $250 | — | — | — | — | Open short @ 115000, size=$250 |
| — | 2025-09-22 | skipped_entry | short | $115,000 | - | - | — | — | — | — | Already in short position — skipped duplicate entry |
| 38 | 2025-09-24 | direction_change_close ✅ | short | $115,000 | $109,000 | $250 | $2,500 | $+130.43 | $2.75 | $+127.68 | Closed short @ 109000 on long signal |
| — | 2025-09-24 | open | long | $109,000 | - | $250 | — | — | — | — | Open long @ 109000, size=$250 |
| — | 2025-09-27 | skipped_entry | long | $105,000 | - | - | — | — | — | — | Already in long position — skipped duplicate entry |
| — | 2025-09-28 | skipped_entry | long | $109,000 | - | - | — | — | — | — | Already in long position — skipped duplicate entry |
| — | 2025-09-30 | tp1_breakeven | long | $109,000 | $115,000 | - | — | — | — | — | TP1 hit @ 115000 — SL moved to breakeven |
| — | 2025-10-01 | skipped_entry | long | $109,000 | - | - | — | — | — | — | Already in long position — skipped duplicate entry |
| 39 | 2025-10-02 | tp2_partial_close ✅ | long | $109,000 | $112,000 | $62 | $625 | $+17.20 | $0.69 | $+16.51 | TP2 @ 112000 — closed 25% of remaining |
| 40 | 2025-10-03 | tp3_partial_close ✅ | long | $109,000 | $116,000 | $47 | $469 | $+30.10 | $0.52 | $+29.59 | TP3 @ 116000 — closed 25% of remaining |
| 41 | 2025-10-04 | tp4_partial_close ✅ | long | $109,000 | $120,000 | $35 | $352 | $+35.48 | $0.39 | $+35.09 | TP4 @ 120000 — closed 25% of remaining |
| 42 | 2025-10-05 | tp5_partial_close ✅ | long | $109,000 | $124,000 | $26 | $264 | $+36.29 | $0.29 | $+36.00 | TP5 @ 124000 — closed 25% of remaining |
| 43 | 2025-10-05 | direction_change_close ✅ | long | $109,000 | $128,000 | $79 | $791 | $+137.88 | $0.87 | $+137.01 | Closed long @ 128000 on short signal |
| — | 2025-10-05 | open | short | $128,000 | - | $250 | — | — | — | — | Open short @ 128000, size=$250 |
| — | 2025-10-06 | tp1_breakeven | short | $128,000 | $124,000 | - | — | — | — | — | TP1 hit @ 124000 — SL moved to breakeven |
| 44 | 2025-10-07 | tp2_partial_close ✅ | short | $128,000 | $120,000 | $62 | $625 | $+39.06 | $0.69 | $+38.38 | TP2 @ 120000 — closed 25% of remaining |
| 45 | 2025-10-08 | direction_change_close ✅ | short | $128,000 | $120,000 | $188 | $1,875 | $+117.19 | $2.06 | $+115.12 | Closed short @ 120000 on long signal |
| — | 2025-10-08 | open | long | $120,000 | - | $250 | — | — | — | — | Open long @ 120000, size=$250 |
| 46 | 2025-10-10 | direction_change_close ✅ | long | $120,000 | $125,000 | $250 | $2,500 | $+104.17 | $2.75 | $+101.42 | Closed long @ 125000 on short signal |
| — | 2025-10-10 | open | short | $125,000 | - | $250 | — | — | — | — | Open short @ 125000, size=$250 |
| — | 2025-10-10 | tp1_breakeven | short | $125,000 | $122,000 | - | — | — | — | — | TP1 hit @ 122000 — SL moved to breakeven |
| 47 | 2025-10-11 | tp2_partial_close ✅ | short | $125,000 | $118,000 | $62 | $625 | $+35.00 | $0.69 | $+34.31 | TP2 @ 118000 — closed 25% of remaining |
| 48 | 2025-10-11 | tp3_partial_close ✅ | short | $125,000 | $116,000 | $47 | $469 | $+33.75 | $0.52 | $+33.23 | TP3 @ 116000 — closed 25% of remaining |
| 49 | 2025-10-19 | direction_change_close ✅ | short | $125,000 | $106,000 | $141 | $1,406 | $+213.75 | $1.55 | $+212.20 | Closed short @ 106000 on long signal |
| — | 2025-10-19 | open | long | $106,000 | - | $250 | — | — | — | — | Open long @ 106000, size=$250 |
| — | 2025-10-20 | tp1_breakeven | long | $106,000 | $112,000 | - | — | — | — | — | TP1 hit @ 112000 — SL moved to breakeven |
| 50 | 2025-10-21 | direction_change_close ✅ | long | $106,000 | $112,000 | $250 | $2,500 | $+141.51 | $2.75 | $+138.76 | Closed long @ 112000 on short signal |
| — | 2025-10-21 | open | short | $112,000 | - | $250 | — | — | — | — | Open short @ 112000, size=$250 |
| — | 2026-03-05 | skipped_entry | short | $74,000 | - | - | — | — | — | — | Already in short position — skipped duplicate entry |
| — | 2026-03-06 | tp1_breakeven | short | $112,000 | $72,000 | - | — | — | — | — | TP1 hit @ 72000 — SL moved to breakeven |
| 51 | 2026-03-07 | tp2_partial_close ✅ | short | $112,000 | $71,000 | $62 | $625 | $+228.79 | $0.69 | $+228.11 | TP2 @ 71000 — closed 25% of remaining |
| 52 | 2026-03-09 | direction_change_close ✅ | short | $112,000 | $70,000 | $188 | $1,875 | $+703.12 | $2.06 | $+701.06 | Closed short @ 70000 on long signal |
| — | 2026-03-09 | open | long | $70,000 | - | $250 | — | — | — | — | Open long @ 70000, size=$250 |
| — | 2026-03-11 | tp1_breakeven | long | $70,000 | $72,000 | - | — | — | — | — | TP1 hit @ 72000 — SL moved to breakeven |
| 53 | 2026-03-17 | direction_change_close ✅ | long | $70,000 | $74,500 | $250 | $2,500 | $+160.71 | $2.75 | $+157.96 | Closed long @ 74500 on short signal |
| — | 2026-03-17 | open | short | $74,500 | - | $250 | — | — | — | — | Open short @ 74500, size=$250 |
| — | 2026-03-18 | tp1_breakeven | short | $74,500 | $73,000 | - | — | — | — | — | TP1 hit @ 73000 — SL moved to breakeven |
| 54 | 2026-03-19 | tp2_partial_close ✅ | short | $74,500 | $71,000 | $62 | $625 | $+29.36 | $0.69 | $+28.67 | TP2 @ 71000 — closed 25% of remaining |
| 55 | 2026-03-20 | tp3_partial_close ✅ | short | $74,500 | $70,000 | $47 | $469 | $+28.31 | $0.52 | $+27.80 | TP3 @ 70000 — closed 25% of remaining |
| 56 | 2026-03-22 | tp4_partial_close ✅ | short | $74,500 | $68,500 | $35 | $352 | $+28.31 | $0.39 | $+27.93 | TP4 @ 68500 — closed 25% of remaining |
| 57 | 2026-03-22 | end_of_period_close ✅ | short | $74,500 | $68,500 | $105 | $1,055 | $+84.94 | $1.16 | $+83.78 | Closed at end of simulation period |

---

## Notes & Methodology

- **TP1** = SL moved to breakeven, no capital realised
- **TP2+** = 25% of remaining position closed each hit
- **Direction change** = 100% position closed at new signal's price
- **Duplicate same-direction entries** = skipped (conservative — no averaging up)
- **Fees** = 0.055% × 2 (open + close) applied to notional
- **Position sizing**: Smart signals = $250, Normal signals = $200 (collateral)
- Notional = collateral × 10× leverage
- Simulation generated from 82 raw signal events