import json, os
from datetime import datetime

FILES = {'pos': 'positions.json', 'hist': 'history.json', 'set': 'settings.json'}

def load(k):
    if not os.path.exists(FILES[k]):
        return {'mode':'SPOT', 'exchange':'MEXC'} if k=='set' else ({} if k=='pos' else [])
    try:
        with open(FILES[k], 'r') as f: return json.load(f)
    except: return {} if k=='pos' else []

def save(k, d):
    with open(FILES[k], 'w') as f: json.dump(d, f, indent=4)

def get_positions(): return load('pos')
def get_history(): return load('hist')
def get_settings(): return load('set')

def set_setting(key, val):
    s = get_settings()
    s[key] = val
    save('set', s)

def update_position(sym, data):
    p = get_positions()
    p[sym] = data
    save('pos', p)

def close_position(sym, price, reason, pnl=0):
    p = get_positions()
    if sym in p:
        pos = p[sym]
        if pnl == 0 and price > 0:
            entry = pos['entry_price']
            lev = pos.get('leverage', 1)
            pct = (price - entry) / entry
            if pos.get('side') == 'SHORT': pct *= -1
            pnl = pct * pos['amount_margin'] * lev

        rec = {
            'symbol': sym, 'profit_usdt': round(pnl, 4),
            'exit_price': price, 'reason': reason,
            'exit_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'exchange': pos.get('exchange', 'MEXC')
        }
        h = get_history()
        h.insert(0, rec)
        save('hist', h[:300])
        del p[sym]
        save('pos', p)