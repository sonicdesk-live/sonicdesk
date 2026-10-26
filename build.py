#!/usr/bin/env python3
"""Sonic Desk: собирает data.json из истории сделок (trades_raw.txt: открытие в минутах от эпохи, длительность в минутах,
сторона, лоты, цена входа, цена выхода, прибыль в $ при множителе x1). Множитель x24 применяет страница."""
import json
from pathlib import Path
HERE = Path(__file__).parent
rows = [l.split(',') for l in (HERE / 'trades_raw.txt').read_text().strip().splitlines()]
T = sorted([[int(float(r[0])) * 60, int(float(r[1])), 1 if r[2] == 'B' else -1, float(r[3]), float(r[4]), float(r[5]), float(r[6])] for r in rows])
last = max(t[0] + t[1] * 60 for t in T)
json.dump({'symbol': 'XAUUSD', 'source': 'Myfxbook · Sonic AI · публичная история мастера (x1)', 'asof': last,
           'launch': 1758153600, 'trades': T}, open(HERE / 'data.json', 'w'), separators=(',', ':'))
print(len(T), 'trades, last close', last)
