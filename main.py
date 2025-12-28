import ccxt.pro as ccxt
import asyncio
import pandas as pd
import time, config, state, ai_engine
from datetime import datetime
import sys

if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def log(msg):
    m = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(m)
    try:
        with open("activity.log", "a", encoding="utf-8") as f: f.write(m + "\n")
        with open("activity.log", "r", encoding="utf-8") as f: l = f.readlines()
        if len(l) > 200:
            with open("activity.log", "w", encoding="utf-8") as f: f.writelines(l[-200:])
    except: pass

async def get_active_exchanges(exchanges):
    s = state.get_settings()
    name = s.get('exchange', 'MEXC')
    mode = s.get('mode', 'SPOT')
    if name == 'COINEX': return exchanges['coinex_spot'], exchanges['coinex_fut'], name, mode
    return exchanges['mexc_spot'], exchanges['mexc_fut'], name, mode

async def do_exit(ex, sym, pos, current_price, reason):
    side = pos.get('side', 'LONG')
    amount = float(pos['amount_coin'])
    log(f"⚠️ Closing {sym} ({reason})...")
    try:
        if side == 'LONG': await ex.create_market_sell_order(sym, amount, params={'reduceOnly': True} if pos.get('mode')=='FUTURE' else {})
        else: await ex.create_market_buy_order(sym, amount, params={'reduceOnly': True} if pos.get('mode')=='FUTURE' else {})
        state.close_position(sym, current_price, reason)
        log(f"✅ Closed {sym}")
    except Exception as e:
        log(f"❌ Exit Fail {sym}: {e}")

async def analysis_loop(exchanges):
    log("🚀 Aggressive Engine V3 Started...")
    while True:
        try:
            spot, fut, ex_name, mode = await get_active_exchanges(exchanges)
            ex = spot if mode == 'SPOT' else fut
            
            positions = state.get_positions()
            if positions:
                for sym, pos in list(positions.items()):
                    if pos.get('exchange') != ex_name or pos.get('mode') != mode: continue
                    try:
                        tk = await ex.fetch_ticker(sym)
                        cp = tk['last']
                        entry = float(pos['entry_price'])
                        side = pos.get('side', 'LONG')
                        
                        sl_p = config.STOP_LOSS_PERCENT
                        tp_p = config.TAKE_PROFIT_PERCENT
                        
                        exit_flag = False
                        reason = ""
                        
                        if side == 'LONG':
                            if cp <= entry*(1-sl_p): exit_flag=True; reason="⛔ SL"
                            elif cp >= entry*(1+tp_p): exit_flag=True; reason="💰 TP"
                        else:
                            if cp >= entry*(1+sl_p): exit_flag=True; reason="⛔ SL"
                            elif cp <= entry*(1-tp_p): exit_flag=True; reason="💰 TP"
                            
                        if exit_flag: await do_exit(ex, sym, pos, cp, reason)
                    except: pass

            try: 
                bal = await ex.fetch_balance()
                usdt = float(bal['total']['USDT'])
            except: usdt = 0.0


            if usdt >= 1.0:
                for sym in config.SYMBOLS:
                    if state.get_position(sym): continue
                    
                    try:
                        ohlcv = await spot.fetch_ohlcv(sym, config.TIMEFRAME, limit=50)
                        df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
                        dec = ai_engine.analyze_symbol(df, usdt, sym)
                        
                        action = dec['action']
                        
                        if (action == 'BUY') or (action == 'SELL' and mode == 'FUTURE'):
                            
                            amt_usdt = dec['amount']
                            
                            if amt_usdt < 1.0:
                                continue

                            log(f"⚡ SIGNAL: {action} {sym} | Score:{dec['confidence']} | Amt:{amt_usdt}$")
                            
                            lev = dec['leverage'] if mode=='FUTURE' else 1
                            if mode=='FUTURE': await ex.set_leverage(lev, sym)
                            
                            price = df.iloc[-1]['close']
                            coin_amt = (amt_usdt * lev) / price
                            
                            if action == 'BUY': 
                                order = await ex.create_market_buy_order(sym, coin_amt)
                                side = 'LONG'
                            else: 
                                order = await ex.create_market_sell_order(sym, coin_amt)
                                side = 'SHORT'
                            
                            state.update_position(sym, {
                                'entry_price': price, 'amount_coin': order['amount'],
                                'amount_margin': amt_usdt, 'leverage': lev,
                                'mode': mode, 'side': side, 'exchange': ex_name,
                                'timestamp': time.time()
                            })
                            usdt -= amt_usdt
                            log(f"✅ Executed {side} {sym}")
                            
                    except Exception as e: 
                        pass
            
        except Exception as e:
            log(f"Main Loop Err: {e}")
            await asyncio.sleep(5)
            
        await asyncio.sleep(3)

async def main():
    opts = {'enableRateLimit': True, 'timeout': 10000}
    exs = {
        'mexc_spot': ccxt.mexc({'apiKey': config.MEXC_API_KEY, 'secret': config.MEXC_SECRET_KEY, 'options':{'defaultType':'spot'}, **opts}),
        'mexc_fut': ccxt.mexc({'apiKey': config.MEXC_API_KEY, 'secret': config.MEXC_SECRET_KEY, 'options':{'defaultType':'swap'}, **opts}),
        'coinex_spot': ccxt.coinex({'apiKey': config.COINEX_API_KEY, 'secret': config.COINEX_SECRET_KEY, 'options':{'defaultType':'spot'}, **opts}),
        'coinex_fut': ccxt.coinex({'apiKey': config.COINEX_API_KEY, 'secret': config.COINEX_SECRET_KEY, 'options':{'defaultType':'swap'}, **opts}),
    }
    try:
        log("Loading...")
        await asyncio.gather(*[e.load_markets() for e in exs.values()])
        log("Ready.")
        await analysis_loop(exs)
    except KeyboardInterrupt: pass
    finally:
        for e in exs.values(): await e.close()

if __name__ == "__main__":
    try: asyncio.run(main())
    except: pass