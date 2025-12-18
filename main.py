import ccxt.pro as ccxt
import asyncio
import pandas as pd
import time, config, state, ai_engine
from datetime import datetime
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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
    
    if name == 'COINEX':
        return exchanges['coinex_spot'], exchanges['coinex_fut'], name, mode
    return exchanges['mexc_spot'], exchanges['mexc_fut'], name, mode

async def sync_wallet_positions(exchanges):
    while True:
        try:
            spot, fut, ex_name, mode = await get_active_exchanges(exchanges)
            ex = spot if mode == 'SPOT' else fut
            
            positions = state.get_positions()
            if positions:
                balance = await ex.fetch_balance()
                for sym, pos in list(positions.items()):
                    if pos.get('exchange') != ex_name or pos.get('mode') != mode: continue
                    coin = sym.split('/')[0]
                    actual = float(balance.get(coin, {'total':0})['total'])
                    recorded = float(pos['amount_coin'])
                    if actual < (recorded * 0.1):
                        log(f"⚠️ Manual Sell: {sym}. Closing in DB.")
                        state.close_position(sym, pos['entry_price'], "Manual Sell")
        except Exception as e:
            pass
        await asyncio.sleep(5)

async def analysis(exchanges):
    log("🚀 Bot Engine Started...")
    while True:
        try:
            spot, fut, ex_name, mode = await get_active_exchanges(exchanges)
            ex = spot if mode == 'SPOT' else fut
            
            try: 
                bal = await ex.fetch_balance()
                usdt = float(bal['total']['USDT'])
            except: usdt = 0.0
            
            if usdt > config.MIN_TRADE_AMOUNT:
                log(f"🔎 Scan {ex_name}-{mode} | Bal: {usdt:.2f}$")
                
                for sym in config.SYMBOLS:
                    if state.get_position(sym): continue
                    if usdt < config.MIN_TRADE_AMOUNT: break
                    
                    try:
                        ohlcv = await spot.fetch_ohlcv(sym, config.TIMEFRAME, limit=100)
                        df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
                        dec = ai_engine.analyze_symbol(df, usdt, sym)
                        
                        action = dec['action']
                        if action == 'BUY' or (action == 'SELL' and mode == 'FUTURE'):
                            amt = dec['amount']
                            lev = dec['leverage'] if mode=='FUTURE' else 1
                            side = 'LONG' if action == 'BUY' else 'SHORT'
                            
                            log(f"⚡ {side}: {sym} | {dec['reason']}")
                            
                            if mode=='FUTURE': await ex.set_leverage(lev, sym)
                            
                            price = df.iloc[-1]['close']
                            coin_amt = (amt * lev) / price
                            
                            if side == 'LONG': order = await ex.create_market_buy_order(sym, coin_amt)
                            else: order = await ex.create_market_sell_order(sym, coin_amt)
                            
                            state.update_position(sym, {
                                'entry_price': price, 'amount_coin': order['amount'],
                                'amount_margin': amt, 'leverage': lev,
                                'mode': mode, 'side': side, 'exchange': ex_name,
                                'timestamp': time.time()
                            })
                            usdt -= amt
                    except Exception as e:
                        # log(f"Err {sym}: {e}")
                        pass
            else:
                log(f"💤 Low Balance ({usdt:.2f}$)")
                
        except Exception as e:
            log(f"❌ Main Loop Error: {e}")
            
        await asyncio.sleep(15)

async def main():
    opts = {'enableRateLimit': True}
    
    exs = {
        'mexc_spot': ccxt.mexc({'apiKey': config.MEXC_API_KEY, 'secret': config.MEXC_SECRET_KEY, 'options':{'defaultType':'spot'}, **opts}),
        'mexc_fut': ccxt.mexc({'apiKey': config.MEXC_API_KEY, 'secret': config.MEXC_SECRET_KEY, 'options':{'defaultType':'swap'}, **opts}),
        'coinex_spot': ccxt.coinex({'apiKey': config.COINEX_API_KEY, 'secret': config.COINEX_SECRET_KEY, 'options':{'defaultType':'spot'}, **opts}),
        'coinex_fut': ccxt.coinex({'apiKey': config.COINEX_API_KEY, 'secret': config.COINEX_SECRET_KEY, 'options':{'defaultType':'swap'}, **opts}),
    }
    
    try:
        log("⏳ Loading Markets...")
        tasks = [e.load_markets() for e in exs.values()]
        await asyncio.gather(*tasks)
        log("✅ Markets Loaded Successfully.")
        
        await asyncio.gather(
            analysis(exs),
            sync_wallet_positions(exs)
        )
        
    except KeyboardInterrupt:
        log("👋 Bot Stopped by User.")
        
    except Exception as e:
        log(f"🔥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        log("🔌 Closing connections...")
        for name, ex in exs.items():
            try:
                await ex.close()
            except: pass
        
        await asyncio.sleep(0.25)
        log("👋 Bye.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass