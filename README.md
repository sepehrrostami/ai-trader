# 🚀 Nimbaha: AI Crypto Trader Pro v3.0

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Framework](https://img.shields.io/badge/Frontend-Bootstrap%205%20%7C%20Glassmorphism-purple?style=for-the-badge)

**An advanced, hybrid high-frequency trading bot that combines Machine Learning (Random Forest) with Technical Analysis (RSI, ADX, EMA) to scalp the crypto market.**

Nimbaha is designed for speed and precision, utilizing an **Asynchronous** core to monitor markets in real-time. It features a modern, responsive web dashboard for monitoring performance, managing positions, and analyzing market data.

---

## ✨ Key Features

* **⚡ Multi-Exchange Support:** Seamlessly trade on **MEXC** and **CoinEx** with instant switching capabilities.
* **🧠 Hybrid Scalping Strategy:** Uses technical indicators (EMA Cross, RSI, ADX) for signal generation and AI (Random Forest) for trend confirmation.
* **🔄 Smart Wallet Sync:** Automatically detects manual trades made by the user on the exchange and updates the bot's internal database to prevent conflicts.
* **💎 Modern Dashboard:** A beautiful web interface featuring **Glassmorphism design**, real-time Dark/Light mode, live PnL charts, and an integrated terminal.
* **🚀 Async Core:** Built with `CCXT Pro` and `Asyncio` for millisecond-latency reaction times.
* **🛡️ Risk Management:** Dynamic Stop-Loss (SL), Take-Profit (TP), and auto-calculated position sizing based on account balance.
* **📈 Dual-Mode Trading:** Supports both **SPOT** and **FUTURES** (Long/Short) markets.

---

## 📸 Dashboard Preview

![Dashboard Screenshot](https://via.placeholder.com/1200x600?text=Dashboard+Screenshot+Placeholder)
*(Replace this image link with your actual dashboard screenshot)*

---

## 🛠️ Prerequisites

* **OS:** Ubuntu 20.04+ / Debian 11+ (Recommended for VPS)
* **Python:** Version 3.9 or higher
* **Hardware:** Minimum 1GB RAM, 1 CPU Core.

---

## 📥 Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/sepehrrostami/ai-trader.git](https://github.com/sepehrrostami/ai-trader.git)
cd ai-trader

2. Set Up Virtual Environment
It is recommended to use a virtual environment to manage dependencies:

Bash

python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
Bash

pip install ccxt pandas pandas_ta scikit-learn joblib numpy flask aiohttp requests
⚙️ Configuration
Open config.py and configure your API keys and trading preferences.

⚠️ Security Warning: Never commit your config.py file with real API keys to GitHub. Add it to your .gitignore file.

Python

# config.py

# Exchange Keys
MEXC_API_KEY = 'YOUR_MEXC_API_KEY'
MEXC_SECRET_KEY = 'YOUR_MEXC_SECRET_KEY'

COINEX_API_KEY = 'YOUR_COINEX_API_KEY'
COINEX_SECRET_KEY = 'YOUR_COINEX_SECRET_KEY'

# Trading Pairs
SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 
    'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT'
]

# Strategy Settings
TIMEFRAME = '5m'        # Scalping timeframe
MIN_TRADE_AMOUNT = 1.0  # Minimum USDT per trade

# Risk Management
MAX_LEVERAGE = 20
STOP_LOSS_PERCENT = 0.015   # 1.5%
TAKE_PROFIT_PERCENT = 0.025 # 2.5%
🚀 Usage
The system consists of three main components that need to run simultaneously (or as background services).

1. Train the AI Model
Before the first run, train the Random Forest model on historical data:

Bash

python3 train.py
Output: Generates a brain.pkl file.

2. Run the Trading Engine
This is the core logic that connects to exchanges and executes trades:

Bash

python3 main.py
3. Launch the Dashboard
Start the web server to monitor your bot:

Bash

python3 dashboard.py
Access the dashboard at: http://YOUR_SERVER_IP:5000

🌐 Production Deployment (SSL & Nginx)
To run the bot 24/7 with a secure domain (HTTPS):

1. Create Systemd Services
Create a service file at /etc/systemd/system/bot.service:

Ini, TOML

[Unit]
Description=Nimbaha Trading Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/nimbaha
ExecStart=/root/nimbaha/venv/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
(Repeat this step for dashboard.py naming it web.service).

Enable the services:

Bash

sudo systemctl enable bot web
sudo systemctl start bot web
2. Configure Nginx Reverse Proxy
Install Nginx and Certbot:

Bash

sudo apt install nginx certbot python3-certbot-nginx
Configure Nginx (/etc/nginx/sites-available/trader):

Nginx

server {
    server_name yourdomain.com;

    location / {
        proxy_pass [http://127.0.0.1:5000](http://127.0.0.1:5000);
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
Generate SSL Certificate:

Bash

sudo certbot --nginx -d yourdomain.com
📂 Project Structure
Plaintext

nimbaha/
├── ai_engine.py       # Decision logic (AI + Technical scoring)
├── config.py          # Configuration and API keys
├── dashboard.py       # Flask web server (Backend)
├── main.py            # Async trading engine & Wallet Sync
├── state.py           # Database management (JSON file handling)
├── strategy.py        # Indicator calculations (RSI, EMA, ADX)
├── train.py           # Machine Learning training script
├── templates/
│   └── index.html     # Modern UI Dashboard (Frontend)
├── *.json             # Data storage (Positions, History, Settings)
└── activity.log       # System logs
⚠️ Disclaimer
This software is for educational and research purposes only. Cryptocurrency trading involves significant risk and can result in the loss of your capital. The developer accepts no liability for any financial losses incurred while using this bot. Always test on paper trading or with insignificant amounts before using real capital.

👨‍💻 Author
Developed with ❤️ by Sepehr Rostami.
