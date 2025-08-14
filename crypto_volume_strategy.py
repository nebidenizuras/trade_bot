from binance.client import Client
from telegram_bot import send_message_to_telegram, channel_00, channel_01, channel_02, channel_03
import pandas as pd
import time
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

# Binance API Keys
API_KEY = ""
API_SECRET = ""
client = Client(API_KEY, API_SECRET)

# Telegram bildirim açık/kapat
IS_TELEGRAM_MSG_ACTIVE = True

# Hacim artış oranı
VOLUME_RATIO = 1.1

# Hangi zaman diliminde kaç mum alınacak
TIMEFRAME_CONFIG = {
    "15m": 20,
    "1h": 20,
    "4h": 20,
    "1d": 20,
}

# Telegram kanal ID'leri
channel_by_timeframe = {
    "15m": channel_03,
    "1h": channel_02,
    "4h": channel_01,
    "1d": channel_00,
}

def get_usdt_symbols():
    try:
        exchange_info = client.futures_exchange_info()
        return [
            symbol["symbol"]
            for symbol in exchange_info["symbols"]
            if symbol["quoteAsset"] == "USDT" and symbol["status"] == "TRADING"
        ]
    except Exception as e:
        print(f"❌ Sembol verisi alınamadı: {e}")
        return []

def get_last_ohlcv(symbol, timeframe, candle_count):
    try:
        klines = client.futures_klines(symbol=symbol, interval=timeframe, limit=candle_count)
        df = pd.DataFrame(
            klines, columns=["timestamp", "open", "high", "low", "close", "volume", "_", "_", "_", "_", "_", "_"]
        )
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)

        # 8 EMA hesapla
        df["ema8"] = df["close"].ewm(span=8, adjust=False).mean()

        return df
    except Exception as e:
        print(f"[{timeframe}] Hata: {symbol} - {e}")
        return None

def is_volume_increasing_by_percent(df):
    if len(df) < 8:
        return False

    vol_2 = df["volume"].iloc[-2]
    close_2 = df["close"].iloc[-2]
    vol_3 = df["volume"].iloc[-1]
    close_3 = df["close"].iloc[-1]
    open_3 = df["open"].iloc[-1]
    ema8_3 = df["ema8"].iloc[-1]

    # Hacim + fiyat + EMA kontrolü
    return (
        (vol_3 > (vol_2 * VOLUME_RATIO)) and
        (close_3 > close_2) and
        (close_3 > open_3) and
        (close_3 > ema8_3)  # EMA 8 üzerinde kapanış
    )

def process_symbol(symbol, timeframe, candle_count):
    df = get_last_ohlcv(symbol, timeframe, candle_count)
    if df is not None and is_volume_increasing_by_percent(df):
        last_volume = df["volume"].iloc[-1]
        last_close = df["close"].iloc[-1]
        volume_value = last_volume * last_close
        return {"symbol": symbol, "volume_value": volume_value}
    return None

def scan_symbols(timeframe, candle_count):
    symbols = get_usdt_symbols()
    results = []
    print(f"🔍 [{timeframe}] taraması başlatıldı. Toplam {len(symbols)} sembol kontrol edilecek...")

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(process_symbol, symbol, timeframe, candle_count) for symbol in symbols]
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    sorted_results = sorted(results, key=lambda x: x["volume_value"], reverse=True)
    send_results(sorted_results[:20], timeframe)

def send_results(result_list, timeframe):
    channel_id = channel_by_timeframe.get(timeframe)

    if not result_list:
        msg = f"***\n{timeframe.upper()} taramasında uygun coin bulunamadı.\n***"
        if channel_id:
            send_message_to_telegram(channel_id, msg)
        print(msg)
        return

    #formatted = "\n".join([f"{item['symbol']} (Volume: {item['volume_value']:,.2f} $)" for item in result_list])
    formatted = "\n".join([
        f"[{item['symbol']}](https://tr.tradingview.com/chart/?symbol=BINANCE:{item['symbol']}.P) "
        f"(Volume: {item['volume_value']:,.2f} $)"
        for item in result_list
    ])
    msg = f"***\nTime Frame: {timeframe.upper()}\n***\n\n*** SONUÇLAR ***\n\n{formatted}"

    print(msg)
    if IS_TELEGRAM_MSG_ACTIVE and channel_id:
        send_message_to_telegram(channel_id, msg)

def scheduler_loop():
    print("🔁 Zamanlayıcı başlatıldı...")
    already_run = set()

    while True:
        now = datetime.now(timezone.utc)
        current_key = now.strftime("%Y-%m-%d %H:%M")

        if now.minute in [14, 29, 44, 59]:
            if current_key not in already_run:
                already_run.add(current_key)
                for tf in ["15m"]:
                    try:
                        scan_symbols(tf, TIMEFRAME_CONFIG[tf])
                    except Exception as e:
                        print(f"❌ {tf} taraması sırasında hata: {e}")  

        if now.minute == 58:
            if current_key not in already_run:
                already_run.add(current_key)
                for tf in ["1h"]:
                    try:
                        scan_symbols(tf, TIMEFRAME_CONFIG[tf])
                    except Exception as e:
                        print(f"❌ {tf} taraması sırasında hata: {e}")      

        if now.minute == 57 and now.hour in [23, 3, 7, 11, 15, 19]:
            if current_key not in already_run:
                already_run.add(current_key)
                for tf in ["4h"]:
                    try:
                        scan_symbols(tf, TIMEFRAME_CONFIG[tf])
                    except Exception as e:
                        print(f"❌ {tf} taraması sırasında hata: {e}")                  

        if now.minute == 56 and now.hour == 23:
            if current_key not in already_run:
                already_run.add(current_key)
                for tf in ["1d"]:
                    try:
                        scan_symbols(tf, TIMEFRAME_CONFIG[tf])
                    except Exception as e:
                        print(f"❌ {tf} taraması sırasında hata: {e}")                                  
        
        time.sleep(30)

if __name__ == "__main__":
    # Başlangıç mesajı
    for tf, channel in channel_by_timeframe.items():
        send_message_to_telegram(channel, f"🔔 TMT CRYPTO Strategy `{tf}` zaman dilimi için başlatıldı.")

    # İlk çalıştırmada tüm timeframe'leri tarat
    for tf in ["15m", "1h", "4h", "1d"]:
        try:
            scan_symbols(tf, TIMEFRAME_CONFIG[tf])
        except Exception as e:
            print(f"❌ İlk taramada hata: {tf} - {e}")

    scheduler_loop()
