from binance.client import Client
from telegram_bot import warn, send_message_to_telegram, channel_00, channel_04
import pandas as pd
import time
import datetime

"""
    KLINE_INTERVAL_1MINUTE = '1m'
    KLINE_INTERVAL_3MINUTE = '3m'
    KLINE_INTERVAL_5MINUTE = '5m'
    KLINE_INTERVAL_15MINUTE = '15m'
    KLINE_INTERVAL_30MINUTE = '30m'
    KLINE_INTERVAL_1HOUR = '1h'
    KLINE_INTERVAL_2HOUR = '2h'
    KLINE_INTERVAL_4HOUR = '4h'
    KLINE_INTERVAL_6HOUR = '6h'
    KLINE_INTERVAL_8HOUR = '8h'
    KLINE_INTERVAL_12HOUR = '12h'
    KLINE_INTERVAL_1DAY = '1d'
    KLINE_INTERVAL_3DAY = '3d'
    KLINE_INTERVAL_1WEEK = '1w'
    KLINE_INTERVAL_1MONTH = '1M'
"""

# Binance API Anahtarları
API_KEY = ""  # API anahtarınızı buraya yazın
API_SECRET = ""  # Secret anahtarınızı buraya yazın
EXCHANGE = "BINANCE"

VOLUME_RATIO = 1.1

TIME_FRAME = Client.KLINE_INTERVAL_4HOUR
CANDLE_COUNT = 3

IS_TELEGRAM_MSG_ACTIVE = True

# Binance Client'ını başlat
client = Client(API_KEY, API_SECRET)

# 1. Binance Futures Sembollerini Çek (Sadece USDT Çiftlerini Filtrele)
def get_usdt_symbols():
    exchange_info = client.futures_exchange_info()  # Futures bilgilerini al
    usdt_symbols = [
        symbol["symbol"]
        for symbol in exchange_info["symbols"]
        if symbol["quoteAsset"] == "USDT" and symbol["status"] == "TRADING"
    ]
    print(f"Toplam {len(usdt_symbols)} USDT paritesinde çift bulundu.")
    return usdt_symbols

# 2. Belirtilen Sembol İçin 1 Günlük Son 3 Mum Verisini Çek
def get_last_ohlcv(symbol):
    try:
        # 1 günlük K-line (mum) verisini çek
        klines = client.futures_klines(symbol=symbol, interval=TIME_FRAME, limit=CANDLE_COUNT)
        df = pd.DataFrame(
            klines, columns=["timestamp", "open", "high", "low", "close", "volume", "_", "_", "_", "_", "_", "_"]
        )
        df = df[["timestamp", "open", "high", "low", "close", "volume"]].astype(float)
        return df
    except Exception as e:
        print(f"Veri alınırken hata oluştu: {symbol}, Hata: {e}")
        return None

# 3. Hacmi Artan ve Yüzde Kuralını Sağlayan Çiftleri Kontrol Et
def is_volume_increasing_by_percent(df):
    if len(df) < 3:
        return False
    # Hacimlerin %40 artıp artmadığını kontrol et
    vol_1 = df["volume"].iloc[0]
    close_1 = df["close"].iloc[0]
    vol_2 = df["volume"].iloc[1]
    close_2 = df["close"].iloc[1]
    vol_3 = df["volume"].iloc[2]
    close_3 = df["close"].iloc[2]
    return (vol_3 > (vol_2 * VOLUME_RATIO)) & (close_3 > close_2) & (close_3 > close_2) #(vol_3 > vol_2 * VOLUME_RATIO)

# 4. Tüm USDT Coinlerini Tarayarak Şartı Sağlayanları Bul
def scan_usdt_symbols_with_increasing_volume():
    symbols = get_usdt_symbols()
    increasing_volume_symbols = []

    for symbol in symbols:
        df = get_last_ohlcv(symbol)
        if df is not None and is_volume_increasing_by_percent(df):
            last_volume = df["volume"].iloc[-2]
            last_close = df["close"].iloc[-2]
            volume_value = last_volume * last_close
            increasing_volume_symbols.append({"symbol": symbol, "volume_value": volume_value})
            print(f"Hacmi artan çift bulundu: {symbol}, İşlem Hacmi: {volume_value:,.2f} $")
        # Her istekten sonra bekle
        time.sleep(0.05)

    # İşlem hacmine göre sırala
    sorted_symbols = sorted(increasing_volume_symbols, key=lambda x: x["volume_value"], reverse=True)
    return sorted_symbols

def send_results_in_chunks(result_list, chunk_size=10):
    """
    Telegram'a mesajları x'erli gruplar halinde gönder
    """

    if len(result_list) < 1:
        channelMsg = f"***\nBulunamadı !\n***\n"
        send_message_to_telegram(channel_00, channelMsg)
        send_message_to_telegram(channel_04, channelMsg)
        
    for i in range(0, len(result_list), chunk_size):
        chunk = result_list[i:i+chunk_size]
        formatted_message = "\n".join(chunk)
        debugMsg = f"***\nTime Frame : {TIME_FRAME}\nCandle : {CANDLE_COUNT}\n***\n\n*** RESULTS ***\n\n{formatted_message}\n"
        print(debugMsg)

        if IS_TELEGRAM_MSG_ACTIVE:
            channelMsg = f"***\nTime Frame : {TIME_FRAME}\n***\n\n*** RESULTS ***\n\n{formatted_message}\n"
            send_message_to_telegram(channel_00, channelMsg)
            send_message_to_telegram(channel_04, channelMsg)


def wait_until_minute(minute=55):
    while True:
        now = datetime.datetime.now()
        if now.minute == minute:
            break
        wait_seconds = 60 - now.second
        time.sleep(wait_seconds)              

# Çalıştırma
if __name__ == "__main__":
    send_message_to_telegram(channel_00, "TMT Strategy Is Started...\n")
    send_message_to_telegram(channel_04, "TMT Strategy Is Started...\n")

    while True:
        #wait_until_minute(55)  # her xx:55'te tetikle

        results = scan_usdt_symbols_with_increasing_volume()

        sorted_results = [f"{item['symbol']}.P (Volume: {item['volume_value']:,.2f} $)\n" for item in results[:10]]

        send_results_in_chunks(sorted_results)

        # 60 saniye bekleyerek tekrar xx:55’e kadar boş döngü engellenir
        time.sleep(600)
