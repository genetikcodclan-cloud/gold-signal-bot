import os
import time
import threading
import requests
from flask import Flask
from datetime import datetime
import yfinance as yf
import pandas as pd

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

app = Flask(__name__)

def send_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def get_signal():
    try:
        df = yf.download("GC=F", period="2d", interval="15m", progress=False)
        if len(df) < 100: return None
        df['EMA9'] = df['Close'].ewm(span=9).mean()
        df['EMA21'] = df['Close'].ewm(span=21).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['EMA200'] = df['Close'].ewm(span=200).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + gain/loss))
        df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()
        last = df.iloc[-1]; prev = df.iloc[-2]
        close = float(last['Close']); ema9 = float(last['EMA9']); ema21 = float(last['EMA21'])
        ema50 = float(last['EMA50']); ema200 = float(last['EMA200']); rsi = float(last['RSI'])
        if not (8 <= datetime.now().hour <= 19): return None
        cross_up = float(prev['EMA9']) <= float(prev['EMA21']) and ema9 > ema21
        trend_up = ema9 > ema50 and ema50 > ema200
        if cross_up and trend_up and 52 < rsi < 68:
            sl = close - float(last['ATR'])*1.8; tp = close + float(last['ATR'])*3.2
            return f"🟢 *GOLD SAFE BUY*\nXAU @ {close:.2f}\nSL {sl:.2f} TP {tp:.2f}"
        cross_down = float(prev['EMA9']) >= float(prev['EMA21']) and ema9 < ema21
        trend_down = ema9 < ema50 and ema50 < ema200
        if cross_down and trend_down and 32 < rsi < 48:
            sl = close + float(last['ATR'])*1.8; tp = close - float(last['ATR'])*3.2
            return f"🔴 *GOLD SAFE SELL*\nXAU @ {close:.2f}\nSL {sl:.2f} TP {tp:.2f}"
        return None
    except: return None

def bot_loop():
    send_telegram("✅ *Gold Bot Attivo su Koyeb!*")
    while True:
        try:
            sig = get_signal()
            if sig: send_telegram(sig)
            time.sleep(300)
        except: time.sleep(60)

@app.route('/')
def home(): return "Bot RUNNING", 200
@app.route('/health')
def health(): return "OK", 200

threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))
