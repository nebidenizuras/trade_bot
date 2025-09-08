import yfinance as yf
import pandas as pd
import itertools
from tqdm import tqdm
from datetime import datetime
from joblib import Parallel, delayed
import numpy as np

# EMA strateji testi için bir fonksiyon tanımla

def calculate_ema(data, span):
    alpha = 2 / (span + 1)
    ema = np.zeros_like(data)
    ema[0] = data[0]  # İlk değer
    for i in range(1, len(data)):
        ema[i] = alpha * data[i] + (1 - alpha) * ema[i - 1]
    return ema

def ema_strategy(data, ema_short, ema_long):
    # EMA hesaplamalarını optimize etmek için NumPy kullanımı
    data[f'EMA{ema_short}'] = calculate_ema(data['Close'].values, ema_short)
    data[f'EMA{ema_long}'] = calculate_ema(data['Close'].values, ema_long)

    # İşlem sinyallerini belirle (sadece alış ve pozisyon kapatma)
    data['Signal'] = 0
    data.loc[(data[f'EMA{ema_short}'] > data[f'EMA{ema_long}']), 'Signal'] = 1
    data.loc[(data[f'EMA{ema_short}'] <= data[f'EMA{ema_long}']), 'Signal'] = -1

    # Pozisyonu hesapla ve işlem detaylarını tut
    trades = []
    position = 0  # Başlangıç pozisyonu
    initial_balance = 100000  # Başlangıç bakiyesi
    balance = initial_balance

    for i in range(len(data)):
        if data['Signal'].iloc[i] == 1 and position == 0:  # Alış sinyali
            position = balance / data['Close'].iloc[i]
            trades.append({
                'Date': data.index[i],
                'Type': 'Buy',
                'Price': data['Close'].iloc[i],
                'Balance': balance,
                'Profit (%)': None,
                'EMA Short Value': data[f'EMA{ema_short}'].iloc[i],
                'EMA Long Value': data[f'EMA{ema_long}'].iloc[i],
                'EMA Short': ema_short,
                'EMA Long': ema_long
            })
        elif data['Signal'].iloc[i] == -1 and position > 0:  # Pozisyon kapatma sinyali
            sell_balance = position * data['Close'].iloc[i]
            profit = (sell_balance - balance) / balance * 100
            trades.append({
                'Date': data.index[i],
                'Type': 'Sell',
                'Price': data['Close'].iloc[i],
                'Balance': sell_balance,
                'Profit (%)': profit,
                'EMA Short Value': data[f'EMA{ema_short}'].iloc[i],
                'EMA Long Value': data[f'EMA{ema_long}'].iloc[i],
                'EMA Short': ema_short,
                'EMA Long': ema_long
            })
            balance = sell_balance
            position = 0

    # İşlemleri DataFrame olarak döndür
    trades_df = pd.DataFrame(trades)

    # Kümülatif getiri hesapla
    total_return = (balance / initial_balance - 1) * 100

    return total_return, trades_df

# Hisseler için en iyi EMA kombinasyonunu bul

def find_best_ema(stock_symbol):
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = '2020-01-01'
    try:
        data = yf.download(stock_symbol, start=start_date, end=end_date, progress=False)
    except Exception as e:
        print(f"Veri indirilemedi: {e}")
        return stock_symbol, None, None, None, None

    if data.empty or len(data) < 200:  # Yetersiz veri kontrolü
        return stock_symbol, None, None, None, None

    best_ema_short = None
    best_ema_long = None
    best_return = -float('inf')
    best_trades_details = None

    combinations = list(itertools.combinations(range(1, 201), 2))

    def process_combination(ema_short, ema_long):
        total_return, trades = ema_strategy(data.copy(), ema_short, ema_long)
        return ema_short, ema_long, total_return, trades

    results = Parallel(n_jobs=-1)(delayed(process_combination)(ema_short, ema_long) for ema_short, ema_long in combinations)

    for ema_short, ema_long, total_return, trades in results:
        if total_return > best_return:
            best_return = total_return
            best_ema_short = ema_short
            best_ema_long = ema_long
            best_trades_details = trades

    start_date_actual = data.index.min()
    end_date_actual = data.index.max()

    return stock_symbol, best_ema_short, best_ema_long, best_return, best_trades_details, start_date_actual, end_date_actual

# En iyi EMA kombinasyonlarını bul ve Excel'e kaydet
bist_symbols = [
    'TUPRS.IS', 'FROTO.IS'  # Sadece TOASO
]

results = []
all_trade_details = []

for symbol in tqdm(bist_symbols, desc="Hisseler işleniyor"):
    symbol, ema_short, ema_long, performance, trades, start_date, end_date = find_best_ema(symbol)
    results.append({
        'Hisse': symbol,
        'EMA Short': ema_short,
        'EMA Long': ema_long,
        'Performans (%)': performance,
        'Başlangıç Tarihi': start_date,
        'Bitiş Tarihi': end_date
    })
    if trades is not None:
        trades['Hisse'] = symbol
        all_trade_details.append(trades)

# Sonuçları bir DataFrame'e dönüştür
results_df = pd.DataFrame(results)
trade_details_df = pd.concat(all_trade_details, ignore_index=True) if all_trade_details else pd.DataFrame()

# Excel'e yaz
excel_file_name = f"{symbol.split('.')[0]}_ema_strateji_sonuclari.xlsx"
with pd.ExcelWriter(excel_file_name) as writer:
    results_df.to_excel(writer, sheet_name='En İyi Sonuçlar', index=False)
    trade_details_df.to_excel(writer, sheet_name='İşlem Detayları', index=False)

print(f"Sonuçlar '{excel_file_name}' dosyasına kaydedildi.")
