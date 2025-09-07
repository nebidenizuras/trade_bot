from binance.client import Client
from telegram_bot import send_message_to_telegram, channel_06
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
    "15m": channel_06,
    "1h": channel_06,
    "4h": channel_06,
    "1d": channel_06,
}

# ================== ORTAK FONKSİYONLAR ==================
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
        df["ema8"] = df["close"].ewm(span=8, adjust=False).mean()
        return df
    except Exception as e:
        print(f"[{timeframe}] Hata: {symbol} - {e}")
        return None

# ================== PUANLAMA ==================
def get_score(df, timeframe, signal_type="long"):
    if len(df) < 8:
        return 0

    score = 0

    # son mum
    close_1 = df["close"].iloc[-1]
    open_1 = df["open"].iloc[-1]
    vol_1 = df["volume"].iloc[-1]
    ema8_1 = df["ema8"].iloc[-1]  

    close_2 = df["close"].iloc[-2]
    open_2 = df["open"].iloc[-2]
    vol_2 = df["volume"].iloc[-2]
    ema8_2 = df["ema8"].iloc[-2]  

    close_3 = df["close"].iloc[-3]
    open_3 = df["open"].iloc[-3]
    vol_3 = df["volume"].iloc[-3]
    ema8_3 = df["ema8"].iloc[-3] 

    if timeframe == "1h":
        if (close_1 * vol_1 < 9000000):
                return 0
            
    if timeframe == "15m":
        if (close_1 * vol_1 < 2500000):
                return 0

    if signal_type == "long":
        if close_1 > ema8_1:
            score += 1
        else:
            return 0
        if vol_1 > vol_2 * VOLUME_RATIO:
            score += 1
        if vol_2 > vol_3 * VOLUME_RATIO:
            score += 1
        if close_1 > open_1:
            score += 1
        else:
            return 0
        if close_2 < ema8_2:
            score += 1
        if close_3 < ema8_3:
            score += 1
        if (((close_1 - open_1) / open_1) * 100) > 3:
            score += 3
        
    else:  # short
        if close_1 < ema8_1:
            score += 1
        else:
            return 0
        if vol_1 > vol_2 * VOLUME_RATIO:
            score += 1
        if vol_2 > vol_3 * VOLUME_RATIO:
            score += 1
        if close_1 < open_1:
            score += 1
        else:
            return 0
        if close_2 > ema8_2:
            score += 1
        if close_3 > ema8_3:
            score += 1
        if (((open_1 - close_1) / open_1) * 100) > 3:
            score += 3

    return score

# ================== TEK TARAMA FONKSİYONU ==================
def process_and_scan(symbols, timeframe, candle_count, signal_type="long"):
    results = []

    def process_symbol_inner(symbol):
        df = get_last_ohlcv(symbol, timeframe, candle_count)
        if df is not None:
            score = get_score(df, timeframe, signal_type)
            if score > 0:
                last_volume = df["volume"].iloc[-1]
                last_close = df["close"].iloc[-1]
                last_open = df["open"].iloc[-1]
                last_ratio = ((abs(last_open - last_close) / last_open) * 100)
                volume_value = last_volume * last_close
                return {"symbol": symbol, "score": score, "volume_value": volume_value, "ratio": last_ratio}
        return None

    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(process_symbol_inner, s) for s in symbols]
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    sorted_results = sorted(results, key=lambda x: (x["score"], x["volume_value"]), reverse=True)
    send_results_generic(sorted_results[:20], timeframe, signal_type)

# ================== TEK MESAJ FONKSİYONU ==================
def send_results_generic(result_list, timeframe, signal_type="long"):
    channel_id = channel_by_timeframe.get(timeframe)
    symbol_type = "\U0001F7E2" if signal_type == "long" else "\U0001F534"

    if not result_list:
        msg = f"***\n{timeframe.upper()} {symbol_type} {signal_type} taramasında uygun coin bulunamadı.\n***"
        if channel_id:
            send_message_to_telegram(channel_id, msg)
        print(msg)
        return

    formatted = "\n".join([
        f"{symbol_type} {item['symbol']} | Score: {item['score']} (Volume: {item['volume_value']:,.2f} $) (% {item['ratio']:,.2f})\n"
        f"https://tr.tradingview.com/chart/?symbol=BINANCE:{item['symbol']}.P\n"
        for item in result_list
    ])

    msg = f"***\nTime Frame: {timeframe.upper()} {symbol_type} {signal_type.upper()}\n***\n\n*** SONUÇLAR ***\n\n{formatted}"
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
                        process_and_scan(symbols, tf, TIMEFRAME_CONFIG[tf], signal_type="long")
                        process_and_scan(symbols, tf, TIMEFRAME_CONFIG[tf], signal_type="short")
                    except Exception as e:
                        print(f"❌ {tf} taraması sırasında hata: {e}")         

        if now.minute == 58:
            if current_key not in already_run:
                already_run.add(current_key)
                for tf in ["1h"]:
                    try:
                        process_and_scan(symbols, tf, TIMEFRAME_CONFIG[tf], signal_type="long")
                        process_and_scan(symbols, tf, TIMEFRAME_CONFIG[tf], signal_type="short")
                    except Exception as e:
                        print(f"❌ {tf} taraması sırasında hata: {e}")      

        '''
        if now.minute == 57 and now.hour in [23, 3, 7, 11, 15, 19]:
            if current_key not in already_run:
                already_run.add(current_key)
                for tf in ["4h"]:
                    try:
                        process_and_scan(symbols, tf, TIMEFRAME_CONFIG[tf], signal_type="long")
                        process_and_scan(symbols, tf, TIMEFRAME_CONFIG[tf], signal_type="short")
                    except Exception as e:
                        print(f"❌ {tf} taraması sırasında hata: {e}")                  

        if now.minute == 56 and now.hour == 23:
            if current_key not in already_run:
                already_run.add(current_key)
                for tf in ["1d"]:
                    try:
                        process_and_scan(symbols, tf, TIMEFRAME_CONFIG[tf], signal_type="long")
                        process_and_scan(symbols, tf, TIMEFRAME_CONFIG[tf], signal_type="short")
                    except Exception as e:
                        print(f"❌ {tf} taraması sırasında hata: {e}")                                  
        '''

        time.sleep(30)

# ================== MAIN ==================
if __name__ == "__main__":
    # Başlangıç mesajı
    for tf, channel in channel_by_timeframe.items():
        send_message_to_telegram(channel, f"🔔 TMT CRYPTO Strategy `{tf}` zaman dilimi için başlatıldı. (LONG & SHORT)")

    # İlk çalıştırmada tüm timeframe'leri tarat
    symbols = get_usdt_symbols()
    #for tf in ["15m", "1h", "4h", "1d"]:
    for tf in ["15m", "1h"]:
        try:
            process_and_scan(symbols, tf, TIMEFRAME_CONFIG[tf], signal_type="long")
            time.sleep(2)
            process_and_scan(symbols, tf, TIMEFRAME_CONFIG[tf], signal_type="short")
            time.sleep(5)
        except Exception as e:
            print(f"❌ İlk taramada hata: {tf} - {e}")

    scheduler_loop()
