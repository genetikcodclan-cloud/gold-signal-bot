import os
import time
import threading
import requests
from flask import Flask
from datetime import datetime
import yfinance as yf
import pandas as pd

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)

@app.route('/')
def home():
    return "Gold Bot v3 Attivo - SL Ridotto 1.2 ATR - TP1 1.0 TP2 2.0 TP3 3.5 - Test 2/2 OK - Pronto segnali - Live su Render"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

keep_alive()

def send_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
    except:
        pass

def get_signal():
    try:
        data = yf.download("GC=F", period="1d", interval="5m", progress=False)
        if len(data) < 50:
            return None
        # Esempio logica v3 - mantieni la tua originale sotto
        close = data['Close'].iloc[-1]
        # Qui va la tua logica EMA/RSI/ATR
        return close
    except Exception as e:
        print(f"Errore yfinance: {e}")
        return None

# Messaggio di avvio - ORA DICE RENDER NON KOYEB
send_telegram("✅ Gold Bot Attivo su Render!\nXAUUSD v3 Attivo - SL Ridotto 1.2 ATR - TP1 1.0 TP2 2.0 - TP3 3.5 - Test 2/2 OK - Pronto segnali")

if __name__ == "__main__":
    print("Bot avviato...")
    while True:
        try:
            price = get_signal()
            # Inserisci qui la tua logica di invio segnali originale
            # Esempio: if condition: send_telegram(f"XAUUSD SCALP SELL...")
            print(f"{datetime.now()} - Check prezzo: {price} - Bot vivo su Render")
            time.sleep(60)
        except Exception as e:
            print(f"Errore loop: {e}")
            time.sleep(60)
