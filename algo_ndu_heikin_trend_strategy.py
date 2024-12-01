from binance.client import Client
import pandas as pd
import time

# Binance API Anahtarlarınızı Girin
API_KEY = "YOUR_BINANCE_API_KEY"
API_SECRET = "YOUR_BINANCE_SECRET_KEY"
client = Client(API_KEY, API_SECRET)

def get_usdt_symbols():
    """
    Binance Futures'taki tüm USDT çiftlerini çeker.
    """
    exchange_info = client.futures_exchange_info()
    usdt_symbols = [
        symbol["symbol"]
        for symbol in exchange_info["symbols"]
        if symbol["quoteAsset"] == "USDT" and symbol["status"] == "TRADING"
    ]
    print(f"Toplam {len(usdt_symbols)} USDT paritesinde çift bulundu.")
    return usdt_symbols

def get_ohlcv(symbol, interval, limit=100):
    """
    Belirtilen sembol için OHLCV verisini çeker.
    """
    try:
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', '_', '_', '_', '_', '_', '_'
        ])
        df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        return df
    except Exception as e:
        print(f"{symbol} için veri alınamadı. Hata: {e}")
        return None

def calculate_heikin_ashi(df):
    """
    Klasik mum verilerinden Heikin-Ashi mumlarını hesaplar.
    """
    heikin_ashi_df = pd.DataFrame()
    
    # İlk mum için açılış fiyatı (initial open, close)
    heikin_ashi_df['open'] = (df['open'] + df['close']) / 2
    heikin_ashi_df['close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    heikin_ashi_df['high'] = df[['high', 'open', 'close']].max(axis=1)
    heikin_ashi_df['low'] = df[['low', 'open', 'close']].min(axis=1)

    # Sonraki mumlar için: önceki mumun açılış ve kapanışı ile şu anki mum verilerini kullan
    for i in range(1, len(df)):
        heikin_ashi_df['open'].iloc[i] = (heikin_ashi_df['open'].iloc[i-1] + heikin_ashi_df['close'].iloc[i-1]) / 2
        heikin_ashi_df['close'].iloc[i] = (df['open'].iloc[i] + df['high'].iloc[i] + df['low'].iloc[i] + df['close'].iloc[i]) / 4
        heikin_ashi_df['high'].iloc[i] = max(df['high'].iloc[i], heikin_ashi_df['open'].iloc[i], heikin_ashi_df['close'].iloc[i])
        heikin_ashi_df['low'].iloc[i] = min(df['low'].iloc[i], heikin_ashi_df['open'].iloc[i], heikin_ashi_df['close'].iloc[i])

    return heikin_ashi_df

def find_special_mum(heikin_ashi_df):
    """
    Heikin-Ashi mumlarında, açılış = en düşük ve yeşil olan mumları bulur.
    """
    if len(heikin_ashi_df) < 2:
        return False
    
    # Bir önceki mum
    open_price = heikin_ashi_df['open'].iloc[-2]
    low_price = heikin_ashi_df['low'].iloc[-2]
    close_price = heikin_ashi_df['close'].iloc[-2]

    # Şartları kontrol et: Açılış fiyatı ve en düşük fiyatın eşit olup olmaması ve mumun yeşil olması
    if open_price == low_price and close_price > open_price:
        return True
    return False

def scan_all_usdt_symbols(interval="15m"):
    """
    Tüm USDT çiftlerini tarar ve Heikin-Ashi mum stratejisini sağlayanları listeler.
    """
    usdt_symbols = get_usdt_symbols()
    matching_symbols = []

    for symbol in usdt_symbols:
        df = get_ohlcv(symbol, interval)
        if df is not None:
            heikin_ashi_df = calculate_heikin_ashi(df)
            if find_special_mum(heikin_ashi_df):
                matching_symbols.append(symbol)
                print(f"Şartları sağlayan çift bulundu: {symbol}")

        # Binance API limitlerini aşmamak için bekleme süresi
        time.sleep(0.1)

    return matching_symbols

if __name__ == "__main__":
    print("Tüm USDT çiftleri taranıyor...")
    results = scan_all_usdt_symbols(interval="15m")  # 15 dakikalık mumlar için
    print("\nŞartları sağlayan USDT çiftleri:")
    for symbol in results:
        print(symbol)
