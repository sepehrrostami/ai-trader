import config, strategy

def analyze_symbol(df, bal, symbol):
    df = strategy.add_indicators(df)
    row = df.iloc[-1]
    
    score = 0
    
    if row['RSI'] < 30: score += 4
    elif row['RSI'] < 40: score += 3
    elif row['RSI'] < 50: score += 1
    
    elif row['RSI'] > 70: score -= 4
    elif row['RSI'] > 60: score -= 3
    elif row['RSI'] > 50: score -= 1

    if row['EMA_9'] > row['EMA_21']: score += 1
    elif row['EMA_9'] < row['EMA_21']: score -= 1

    action = 'HOLD'
    if score >= 1: action = 'BUY'
    elif score <= -1: action = 'SELL'
    
    size = 0.0
    if action != 'HOLD':
        if bal < 1.0: 
            size = 0.0
        elif bal < 20.0: 
            size = bal * 0.99 
        else: 
            size = bal * 0.50

    lev = config.MAX_LEVERAGE if abs(score) >= 3 else config.MIN_LEVERAGE

    return {
        'action': action,
        'confidence': abs(score),
        'amount': round(size, 2),
        'leverage': lev,
        'reason': f"Score:{score} RSI:{int(row['RSI'])}"
    }