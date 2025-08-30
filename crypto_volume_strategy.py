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

# ================== LONG TARAFI ==================
def is_long_signal(df):
    if len(df) < 8:
        return False

    close_prev = df["close"].iloc[-2]   # önceki kapanış
    ema8_prev = df["ema8"].iloc[-2]     # önceki EMA8
    vol_prev = df["volume"].iloc[-2]    # önceki mum hacmi

    close_last = df["close"].iloc[-1]   # son kapanış
    open_last = df["open"].iloc[-1]     # son açılış
    ema8_last = df["ema8"].iloc[-1]     # son EMA8    
    vol_last = df["volume"].iloc[-1]    # son mum hacmi

    return (
        close_prev <= ema8_prev
        and close_last > ema8_last
        and vol_last > vol_prev * VOLUME_RATIO
        and close_last > open_last
    )

def process_symbol(symbol, timeframe, candle_count):
    df = get_last_ohlcv(symbol, timeframe, candle_count)
    if df is not None and is_long_signal(df):
        last_volume = df["volume"].iloc[-1]
        last_close = df["close"].iloc[-1]
        volume_value = last_volume * last_close
        return {"symbol": symbol, "volume_value": volume_value}
    return None

def scan_symbols_long(timeframe, candle_count):
    symbols = get_usdt_symbols()
    results = []
    print(f"🔍 [{timeframe}] \U0001F7E2 LONG taraması başlatıldı. Toplam {len(symbols)} sembol kontrol edilecek...")

    with ThreadPoolExecutor(max_workers=15) as executor:
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
        msg = f"***\n{timeframe.upper()} \U0001F7E2 LONG taramasında uygun coin bulunamadı.\n***"
        if channel_id:
            send_message_to_telegram(channel_id, msg)
        print(msg)
        return

    formatted = "\n".join([
        f"\U0001F7E2 {item['symbol']} (Volume: {item['volume_value']:,.2f} $)\n"
        f"https://tr.tradingview.com/chart/?symbol=BINANCE:{item['symbol']}.P\n"
        for item in result_list
    ])
    msg = f"***\nTime Frame: {timeframe.upper()} \U0001F7E2 LONG\n***\n\n*** SONUÇLAR ***\n\n{formatted}"

    print(msg)
    if IS_TELEGRAM_MSG_ACTIVE and channel_id:
        send_message_to_telegram(channel_id, msg)

# ================== SHORT TARAFI ==================
def is_short_signal(df):
    if len(df) < 8:
        return False

    close_prev = df["close"].iloc[-2]   # önceki kapanış
    ema8_prev = df["ema8"].iloc[-2]     # önceki EMA8
    vol_prev = df["volume"].iloc[-2]    # önceki mum hacmi

    close_last = df["close"].iloc[-1]   # son kapanış
    open_last = df["open"].iloc[-1]     # son açılış
    ema8_last = df["ema8"].iloc[-1]     # son EMA8    
    vol_last = df["volume"].iloc[-1]    # son mum hacmi

    return (
        close_prev >= ema8_prev
        and close_last < ema8_last
        and vol_last > vol_prev * VOLUME_RATIO
        and close_last < open_last
    )

def process_symbol_short(symbol, timeframe, candle_count):
    df = get_last_ohlcv(symbol, timeframe, candle_count)
    if df is not None and is_short_signal(df):
        last_volume = df["volume"].iloc[-1]
        last_close = df["close"].iloc[-1]
        volume_value = last_volume * last_close
        return {"symbol": symbol, "volume_value": volume_value}
    return None

def scan_symbols_short(timeframe, candle_count):
    symbols = get_usdt_symbols()
    results = []
    print(f"[{timeframe}] \U0001F534 SHORT taraması başlatıldı. Toplam {len(symbols)} sembol kontrol edilecek...")

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(process_symbol_short, symbol, timeframe, candle_count) for symbol in symbols]
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    sorted_results = sorted(results, key=lambda x: x["volume_value"], reverse=True)
    send_results_short(sorted_results[:20], timeframe)

def send_results_short(result_list, timeframe):
    channel_id = channel_by_timeframe.get(timeframe)

    if not result_list:
        msg = f"***\n{timeframe.upper()} \U0001F534 SHORT taramasında uygun coin bulunamadı.\n***"
        if channel_id:
            send_message_to_telegram(channel_id, msg)
        print(msg)
        return

    formatted = "\n".join([
        f"\U0001F534 {item['symbol']} (Volume: {item['volume_value']:,.2f} $)\n"
        f"https://tr.tradingview.com/chart/?symbol=BINANCE:{item['symbol']}.P\n"
        for item in result_list
    ])
    msg = f"***\nTime Frame: {timeframe.upper()} \U0001F534 SHORT\n***\n\n*** SONUÇLAR ***\n\n{formatted}"

    print(msg)
    if IS_TELEGRAM_MSG_ACTIVE and channel_id:
        send_message_to_telegram(channel_id, msg)

# ================== ZAMANLAYICI ==================
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
                        scan_symbols_long(tf, TIMEFRAME_CONFIG[tf])
                        scan_symbols_short(tf, TIMEFRAME_CONFIG[tf])
                    except Exception as e:
                        print(f"❌ {tf} taraması sırasında hata: {e}")         

        if now.minute == 58:
            if current_key not in already_run:
                already_run.add(current_key)
                for tf in ["1h"]:
                    try:
                        scan_symbols_long(tf, TIMEFRAME_CONFIG[tf])
                        scan_symbols_short(tf, TIMEFRAME_CONFIG[tf])
                    except Exception as e:
                        print(f"❌ {tf} taraması sırasında hata: {e}")      

        if now.minute == 57 and now.hour in [23, 3, 7, 11, 15, 19]:
            if current_key not in already_run:
                already_run.add(current_key)
                for tf in ["4h"]:
                    try:
                        scan_symbols_long(tf, TIMEFRAME_CONFIG[tf])
                        scan_symbols_short(tf, TIMEFRAME_CONFIG[tf])
                    except Exception as e:
                        print(f"❌ {tf} taraması sırasında hata: {e}")                  

        if now.minute == 56 and now.hour == 23:
            if current_key not in already_run:
                already_run.add(current_key)
                for tf in ["1d"]:
                    try:
                        scan_symbols_long(tf, TIMEFRAME_CONFIG[tf])
                        scan_symbols_short(tf, TIMEFRAME_CONFIG[tf])
                    except Exception as e:
                        print(f"❌ {tf} taraması sırasında hata: {e}")                                  
    
        time.sleep(30)

# ================== MAIN ==================
if __name__ == "__main__":
    # Başlangıç mesajı
    for tf, channel in channel_by_timeframe.items():
        send_message_to_telegram(channel, f"🔔 TMT CRYPTO Strategy `{tf}` zaman dilimi için başlatıldı. (LONG & SHORT)")

    # İlk çalıştırmada tüm timeframe'leri tarat
    for tf in ["15m", "1h", "4h", "1d"]:
        try:
            scan_symbols_long(tf, TIMEFRAME_CONFIG[tf])
            time.sleep(2)
            scan_symbols_short(tf, TIMEFRAME_CONFIG[tf])
            time.sleep(5)
        except Exception as e:
            print(f"❌ İlk taramada hata: {tf} - {e}")

    scheduler_loop()
