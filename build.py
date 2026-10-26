#!/usr/bin/env python3
"""Sonic Desk: собирает data.json из истории сделок (trades_raw.txt: открытие в минутах от эпохи, длительность в минутах,
сторона, лоты, цена входа, цена выхода, прибыль в $ при множителе x1). Множитель x24 применяет страница."""
import json
from pathlib import Path
HERE = Path(__file__).parent
rows = [l.split(',') for l in (HERE / 'trades_raw.txt').read_text().strip().splitlines()]
T = sorted([[int(float(r[0])) * 60, int(float(r[1])), 1 if r[2] == 'B' else -1, float(r[3]), float(r[4]), float(r[5]), float(r[6])] for r in rows])
from datetime import datetime, timezone
have = {t[0] for t in T}
for l in (HERE / 'trades_new.csv').read_text().strip().splitlines()[1:]:
    o, c, s, lots, po, pc, p = l.split(',')
    to = int(datetime.strptime(o, '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc).timestamp())
    tc = int(datetime.strptime(c, '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc).timestamp())
    if to not in have:
        T.append([to, (tc - to) // 60, 1 if s == 'B' else -1, float(lots), float(po), float(pc), float(p)])
T.sort()
last = max(t[0] + t[1] * 60 for t in T)
json.dump({'symbol': 'XAUUSD', 'source': 'Myfxbook · Sonic AI · публичная история мастера (x1)', 'asof': last,
           'launch': 1758153600, 'trades': T}, open(HERE / 'data.json', 'w'), separators=(',', ':'))
print(len(T), 'trades, last close', last)
