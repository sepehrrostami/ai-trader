import json, os
from datetime import datetime

FILES = {'pos': 'positions.json', 'hist': 'history.json', 'set': 'settings.json'}

def load(k):
    if not os.path.exists(FILES[k]):
        return {'mode':'SPOT', 'exchange':'MEXC'} if k=='set' else ({} if k=='pos' else [])
    try:
        with open(FILES[k], 'r') as f: return json.load(f)
    except: return {'mode':'SPOT', 'exchange':'MEXC'} if k=='set' else ({} if k=='pos' else [])

def save(k, d):
    try:
        with open(FILES[k], 'w') as f: json.dump(d, f, indent=4)
    except: pass

def get_positions(): return load('pos')
def get_history(): return load('hist')
def get_settings(): return load('set')
def get_position(sym): return get_positions().get(sym, None)

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
            try:
                entry = float(pos['entry_price'])
                lev = int(pos.get('leverage', 1))
                amt = float(pos['amount_margin'])
                
                pct = (price - entry) / entry
                if pos.get('side') == 'SHORT': pct *= -1
                
                pnl = pct * amt * lev
            except: pnl = 0

        rec = {
            'symbol': sym,
            'side': pos.get('side', 'LONG'),
            'leverage': pos.get('leverage', 1),
            'amount_margin': pos.get('amount_margin', 0),
            'entry_price': pos.get('entry_price', 0),
            'exit_price': price,
            'profit_usdt': round(pnl, 4),
            'reason': reason,
            'exit_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'exchange': pos.get('exchange', 'MEXC')
        }
        
        h = get_history()
        h.insert(0, rec)
        save('hist', h[:500])
        
        del p[sym]
        save('pos', p)