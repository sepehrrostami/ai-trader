import config, strategy

def analyze_symbol(df, bal, symbol):
    df = strategy.add_indicators(df)
    row = df.iloc[-1]
    
    score = 0
    if row['EMA_9'] > row['EMA_21']: score += 2
    elif row['EMA_9'] < row['EMA_21']: score -= 2
    
    if row['RSI'] > 55: score += 1
    elif row['RSI'] < 45: score -= 1
    
    if row['ADX'] < 20: score *= 0.5

    action = 'HOLD'
    if score >= 1.5: action = 'BUY'
    elif score <= -1.5: action = 'SELL'
    
    size = 0.0
    if action != 'HOLD':
        if bal < 1.0: size = 0.0
        elif bal < 10.0: size = bal * 0.98
        else: size = max(1.0, bal * 0.25)

    return {
        'action': action,
        'confidence': abs(score)/4,
        'amount': round(size, 2),
        'leverage': config.MAX_LEVERAGE if row['ADX']>30 else config.MIN_LEVERAGE,
        'reason': f"Score:{score} ADX:{int(row['ADX'])}"
    }