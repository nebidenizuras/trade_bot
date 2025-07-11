from binance.client import Client
from telegram_bot import send_message_to_telegram, channel_00, channel_01, channel_02
import pandas as pd
import time
from datetime import datetime, UTC
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Binance API Keys
API_KEY = ""
API_SECRET = ""
client = Client(API_KEY, API_SECRET)

VOLUME_RATIO = 1.1
IS_TELEGRAM_MSG_ACTIVE = True

# Hangi zaman diliminde kaç mum alınacak
TIMEFRAME_CONFIG = {
    "1h": 3,
    "4h": 3,
    "1d": 3,
}

# Timeframe bazlı Telegram kanal ID'leri
channel_by_timeframe = {
    "1h": channel_02,
    "4h": channel_01,
    "1d": channel_00,
}

def get_usdt_symbols():
    exchange_info = client.futures_exchange_info()
    usdt_symbols = [
        symbol["symbol"]
        for symbol in exchange_info["symbols"]
        if symbol["quoteAsset"] == "USDT" and symbol["status"] == "TRADING"
    ]
    return usdt_symbols


def get_last_ohlcv(symbol, timeframe, candle_count):
    try:
        klines = client.futures_klines(symbol=symbol, interval=timeframe, limit=candle_count)
        df = pd.DataFrame(
            klines, columns=["timestamp", "open", "high", "low", "close", "volume", "_", "_", "_", "_", "_", "_"]
        )
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
        return df
    except Exception as e:
        print(f"[{timeframe}] Hata: {symbol} - {e}")
        return None


def is_volume_increasing_by_percent(df):
    if len(df) < 3:
        return False
    vol_2 = df["volume"].iloc[1]
    close_2 = df["close"].iloc[1]
    vol_3 = df["volume"].iloc[2]
    close_3 = df["close"].iloc[2]
    return (vol_3 > vol_2 * VOLUME_RATIO) and (close_3 > close_2)


def process_symbol(symbol, timeframe, candle_count):
    df = get_last_ohlcv(symbol, timeframe, candle_count)
    if df is not None and is_volume_increasing_by_percent(df):
        last_volume = df["volume"].iloc[-2]
        last_close = df["close"].iloc[-2]
        volume_value = last_volume * last_close
        return {"symbol": symbol, "volume_value": volume_value}
    return None


def scan_symbols(timeframe, candle_count):
    symbols = get_usdt_symbols()
    results = []

    print(f"[{timeframe}] Başlatılıyor...")

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(process_symbol, symbol, timeframe, candle_count) for symbol in symbols]

        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    sorted_results = sorted(results, key=lambda x: x["volume_value"], reverse=True)
    send_results(sorted_results[:10], timeframe)
    

def send_results(result_list, timeframe):
    channel_id = channel_by_timeframe.get(timeframe)

    if not result_list:
        msg = f"***\n{timeframe.upper()} taramasında uygun coin bulunamadı.\n***"
        if channel_id:
            send_message_to_telegram(channel_id, msg)
        return

    formatted = "\n".join([f"{item['symbol']}.P (Volume: {item['volume_value']:,.2f} $)" for item in result_list])
    msg = f"***\nTime Frame: {timeframe.upper()}\n***\n\n*** SONUÇLAR ***\n\n{formatted}"

    print(msg)

    if IS_TELEGRAM_MSG_ACTIVE and channel_id:
        send_message_to_telegram(channel_id, msg)


def is_time_to_run(now: datetime, tf: str) -> bool:
    if tf == "1h":
        return now.minute == 55
    elif tf == "4h":
        return now.minute == 55 and now.hour % 4 == 3
    elif tf == "1d":
        return now.minute == 55 and now.hour == 23
    return False


def scheduler_loop():
    print("🔁 Zamanlayıcı başlatıldı...")
    already_run = set()

    while True:
        now = datetime.now(UTC)  # UTC zamanı kullanılır
        current_key = now.strftime("%Y-%m-%d %H:%M")

        for tf, candle_count in TIMEFRAME_CONFIG.items():
            if is_time_to_run(now, tf):
                unique_id = f"{tf}-{current_key}"
                if unique_id not in already_run:
                    already_run.add(unique_id)
                    threading.Thread(target=scan_symbols, args=(tf, candle_count), daemon=True).start()

        time.sleep(30)  # Her 30 saniyede bir kontrol et


if __name__ == "__main__":
    # Her timeframe için kendi kanalına başlangıç mesajı gönder
    for tf, channel in channel_by_timeframe.items():
        send_message_to_telegram(channel, f"🔔 TMT Volume Strategy `{tf}` zaman dilimi için başlatıldı.")
    
    # Zamanlayıcıyı başlat
    scheduler_loop()
