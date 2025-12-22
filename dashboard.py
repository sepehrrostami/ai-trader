from flask import Flask, render_template, jsonify, request
import state, config, ccxt, os, time, requests

app = Flask(__name__)

PING_TARGETS = {
    'MEXC': 'https://api.mexc.com/api/v3/ping',
    'COINEX': 'https://api.coinex.com/v1/common/maintain',
    'GOOGLE': 'https://google.com'
}

exchanges = {
    'MEXC': ccxt.mexc({'apiKey': config.MEXC_API_KEY, 'secret': config.MEXC_SECRET_KEY}),
    'COINEX': ccxt.coinex({'apiKey': config.COINEX_API_KEY, 'secret': config.COINEX_SECRET_KEY})
}

def measure_ping(url):
    try:
        t1 = time.time()
        requests.get(url, timeout=0.8)
        return int((time.time() - t1) * 1000)
    except:
        return 999

@app.route('/api/data')
def get_data():
    s = state.get_settings()
    ex_name = s.get('exchange', 'MEXC')
    ex_obj = exchanges.get(ex_name)
    
    try: bal = ex_obj.fetch_balance()['total']['USDT']
    except: bal = 0
    
    ping_net = measure_ping(PING_TARGETS['GOOGLE'])
    ping_ex = measure_ping(PING_TARGETS.get(ex_name, PING_TARGETS['MEXC']))

    logs = []
    if os.path.exists("activity.log"):
        with open("activity.log") as f: logs = [l.strip() for l in reversed(f.readlines())][:50]

    return jsonify({
        'balance': round(float(bal), 2),
        'positions': state.get_positions(),
        'history': state.get_history(),
        'logs': logs,
        'pings': {
            'net': ping_net,
            'exchange': ping_ex
        },
        'settings': s
    })

@app.route('/api/set', methods=['POST'])
def update_settings():
    data = request.json
    if 'mode' in data: state.set_setting('mode', data['mode'])
    if 'exchange' in data: state.set_setting('exchange', data['exchange'])
    return jsonify({'ok': True})

@app.route('/')
def index(): return render_template('index.html')

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000)
