import random
from datetime import datetime
import requests
import ccxt

# ==============================================================================
# KONFIGURASI API
# ==============================================================================

# Telegram
TELEGRAM_BOT_TOKEN = "8197419649:AAE6CuknsSScYGioyjGHDZeOsVdwQABHw9w"
TELEGRAM_CHAT_ID = "7937298725"

# Binance
BINANCE_API_KEY = "XzLFhVvfogvhCkV4CcC5ilQ2Wp64wdeWAR5dyEVV1BvzJadoCmx3gXCEgYv4WmGO"
BINANCE_API_SECRET = ""  # kosong jika cuma baca harga

# Inisialisasi Binance
exchange = ccxt.binance({
    "apiKey": BINANCE_API_KEY,
    "secret": BINANCE_API_SECRET,
    "enableRateLimit": True
})

# ==============================================================================
# PARAMETER LOGIKA
# ==============================================================================

MIN_CONFIDENCE_FOR_SIGNAL = 55
MIN_CONFIDENCE_FOR_STRONG_SIGNAL = 75

# ==============================================================================
# AMBIL HARGA REALTIME DARI BINANCE
# ==============================================================================

def get_binance_price(symbol="BTC/USDT"):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker["last"]
    except Exception as e:
        print(f"Error ambil harga Binance: {e}")
        return None

# ==============================================================================
# SIMULASI ANALISA KUANTITATIF
# ==============================================================================

def simulate_quant_analysis(ticker: str, timeframe: str) -> dict:
    current_price = get_binance_price(ticker)
    if current_price is None:
        current_price = 50000  # fallback jika gagal ambil harga

    confidence = random.randint(60, 95)
    trends = ["Bullish Kuat", "Bullish Moderat", "Bearish Kuat", "Bearish Moderat", "Sideways Konsolidasi"]
    trend_utama = random.choice(trends)

    # Analisa indikator
    if "Bullish" in trend_utama:
        indicator_summary = f"EMA(50) > EMA(200); RSI ({random.randint(55, 75)}) agak overbought. MACD positif."
        bias_score = random.randint(4, 10)
    elif "Bearish" in trend_utama:
        indicator_summary = f"EMA(50) < EMA(200); RSI ({random.randint(25, 45)}) agak oversold. MACD negatif."
        bias_score = random.randint(-10, -4)
    else:
        indicator_summary = f"EMA rapat; RSI ({random.randint(40, 60)}) netral. MACD datar."
        bias_score = random.randint(-3, 3)

    # Keputusan sinyal
    action = "HOLD"
    if confidence >= MIN_CONFIDENCE_FOR_SIGNAL:
        if bias_score >= 5:
            action = "BUY"
        elif bias_score <= -5:
            action = "SELL"
    if confidence < MIN_CONFIDENCE_FOR_SIGNAL:
        action = "⚠️ Data tidak cukup untuk sinyal valid"

    # Hitung TP/SL
    tp1, tp2, sl = 0, 0, 0
    if action == "BUY":
        sl = current_price * 0.985
        tp1 = current_price * 1.03
        tp2 = current_price * 1.05
    elif action == "SELL":
        sl = current_price * 1.015
        tp1 = current_price * 0.97
        tp2 = current_price * 0.95

    price_format = "{:,.2f}"
    volume_analysis = f"Volume {timeframe} {price_format.format(random.uniform(15000, 35000))} {ticker.split('/')[0]} {'naik' if confidence > 70 else 'normal'}."

    return {
        "ticker": ticker,
        "timeframe": timeframe,
        "current_time": datetime.utcnow().strftime("%d %B %Y, %H:%M:%S UTC"),
        "confidence": confidence,
        "trend_utama": trend_utama,
        "indicator_summary": indicator_summary,
        "volume_analysis": volume_analysis,
        "action": action,
        "tp1": price_format.format(tp1) if tp1 else "N/A",
        "tp2": price_format.format(tp2) if tp2 else "N/A",
        "sl": price_format.format(sl) if sl else "N/A",
        "support": price_format.format(current_price * 0.98),
        "resistance": price_format.format(current_price * 1.02),
        "price_now": price_format.format(current_price)
    }

# ==============================================================================
# GENERATE PESAN
# ==============================================================================

def generate_signal_message(ticker: str = "BTC/USDT", timeframe: str = "1H") -> str:
    analysis = simulate_quant_analysis(ticker, timeframe)

    if analysis["action"] == "⚠️ Data tidak cukup untuk sinyal valid":
        return f"""
========================
📌 Sinyal {analysis['ticker']} [{analysis['timeframe']}]
⏰ {analysis['current_time']}

⚠️ Data tidak cukup untuk sinyal valid
Confidence: {analysis['confidence']}%
========================
"""

    return f"""
========================
📌 Sinyal {analysis['ticker']} [{analysis['timeframe']}]
⏰ {analysis['current_time']}

💵 Harga Sekarang: {analysis['price_now']}
📈 Trend: {analysis['trend_utama']}
📊 Indikator: {analysis['indicator_summary']}
🤖 Confidence AI: {analysis['confidence']}%

🎯 Rekomendasi: {analysis['action']}
TP1: {analysis['tp1']} | TP2: {analysis['tp2']}
SL: {analysis['sl']}

Support: {analysis['support']} | Resistance: {analysis['resistance']}
Volume: {analysis['volume_analysis']}
========================
"""

# ==============================================================================
# KIRIM KE TELEGRAM
# ==============================================================================

def send_to_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
        print("✅ Pesan terkirim ke Telegram")
    except Exception as e:
        print(f"❌ Gagal kirim Telegram: {e}")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    signal_msg = generate_signal_message("BTC/USDT", "1H")
    print(signal_msg)
    send_to_telegram(signal_msg)
