import config, strategy

def analyze_symbol(df, bal, symbol):
    df = strategy.add_indicators(df)
    row = df.iloc[-1]
    
    score = 0
    
    if row['EMA_9'] > row['EMA_21']: score += 2
    elif row['EMA_9'] < row['EMA_21']: score -= 2
    
    if row['RSI'] < 35: score += 3
    elif row['RSI'] > 65: score -= 3
    
    elif row['RSI'] > 50 and score > 0: score += 1
    elif row['RSI'] < 50 and score < 0: score -= 1

    action = 'HOLD'
    if score >= 1.0: action = 'BUY'
    elif score <= -1.0: action = 'SELL'
    
    size = 0.0
    if action != 'HOLD':
        if bal < 5.0: size = 0.0
        elif bal < 20.0: size = bal * 0.98
        else: size = bal * 0.40

    lev = config.MAX_LEVERAGE if abs(score) >= 3 else config.MIN_LEVERAGE

    return {
        'action': action,
        'confidence': abs(score),
        'amount': round(size, 2),
        'leverage': lev,
        'reason': f"Sc:{score} RSI:{int(row['RSI'])}"
    }