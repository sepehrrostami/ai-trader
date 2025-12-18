import pandas_ta as ta

def add_indicators(df):
    df = df.copy()
    df['RSI'] = df.ta.rsi(length=14)
    df['EMA_9'] = df.ta.ema(length=9)
    df['EMA_21'] = df.ta.ema(length=21)
    
    adx = df.ta.adx(length=14)
    df['ADX'] = adx['ADX_14'] if adx is not None and 'ADX_14' in adx.columns else 0
    
    return df