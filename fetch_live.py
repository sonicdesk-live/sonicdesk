#!/usr/bin/env python3
"""Забирает историю сделок собственного счёта через официальный API Myfxbook и пишет live.json.
Логин и пароль берутся из переменных окружения (секреты репозитория), в файлы они не попадают."""
import json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = 'https://www.myfxbook.com/api/'
HERE = Path(__file__).parent


def call(name, **q):
    url = API + name + '.json?' + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={'User-Agent': 'sonicdesk/1.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    if d.get('error'):
        sys.exit(f"{name}: {d.get('message')}")
    return d


def ts(s):
    return int(datetime.strptime(s, '%m/%d/%Y %H:%M').replace(tzinfo=timezone.utc).timestamp())


email, pw = os.environ.get('MYFXBOOK_EMAIL'), os.environ.get('MYFXBOOK_PASSWORD')
if not email or not pw:
    sys.exit('нет MYFXBOOK_EMAIL / MYFXBOOK_PASSWORD')
sess = call('login', email=email, password=pw)['session']
try:
    accs = call('get-my-accounts', session=sess)['accounts']
    want = os.environ.get('MYFXBOOK_ACCOUNT', '').strip().lower()
    pick = [a for a in accs if want and want in (str(a['id']), a['name'].lower())] or \
           [a for a in accs if 'sonic' in a['name'].lower()] or accs
    acc = pick[0]
    hist = call('get-history', session=sess, id=acc['id'])['history']
finally:
    try:
        call('logout', session=sess)
    except SystemExit:
        pass

T = []
for h in hist:
    if h.get('action') not in ('Buy', 'Sell'):
        continue
    o, c = ts(h['openTime']), ts(h['closeTime'])
    T.append([o, (c - o) // 60, 1 if h['action'] == 'Buy' else -1, float(h['sizing']['value']) if isinstance(h.get('sizing'), dict) else float(h.get('lots', 0)),
              float(h['openPrice']), float(h['closePrice']), float(h['profit'])])
T.sort()
json.dump({'account': acc['name'], 'asof': int(datetime.now(timezone.utc).timestamp()), 'trades': T},
          open(HERE / 'live.json', 'w'), separators=(',', ':'))
print(len(T), 'сделок со счёта', acc['name'])
