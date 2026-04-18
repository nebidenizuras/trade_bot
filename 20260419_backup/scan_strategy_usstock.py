import yfinance as yf
import pandas as pd
import time
import datetime
from telegram_bot import send_message_to_telegram, channel_05  # ABD için farklı kanal

US_SYMBOLS = [
    'A', 'AAL', 'AAP', 'AAPL', 'ABBV', 'ABT', 'ACN', 'ADBE', 'ADI', 'ADM', 'ADP', 'ADSK', 'AEE', 'AEP', 'AES', 'AFL',
    'AIG', 'AIZ', 'AJG', 'AKAM', 'ALB', 'ALGN', 'ALL', 'ALLE', 'AMAT', 'AMD', 'AME', 'AMGN', 'AMP', 'AMT', 'AMZN',
    'ANET', 'AON', 'APA', 'APD', 'APH', 'ARE', 'ATO', 'AVB', 'AVGO', 'AVY', 'AWK', 'AXON', 'AXP', 'AZO',
    'BA', 'BAC', 'BALL', 'BAX', 'BBWI', 'BBY', 'BDX', 'BEN', 'BIO', 'BIIB', 'BK', 'BKNG', 'BKR', 'BLDR', 'BMY',
    'BR', 'BRO', 'BSX', 'BWA', 'BX', 'C', 'CACC', 'CAG', 'CAH', 'CARR', 'CAT', 'CB', 'CBOE', 'CBRE', 'CCI', 'CCL',
    'CDNS', 'CDW', 'CE', 'CF', 'CHD', 'CHRW', 'CHTR', 'CI', 'CINF', 'CL', 'CLX', 'CMA', 'CMCSA', 'CME',
    'CMG', 'CMI', 'CMS', 'CNC', 'CNP', 'COF', 'COO', 'COP', 'COST', 'CPB', 'CPRT', 'CPT', 'CRL', 'CRM', 'CSCO',
    'CSGP', 'CSX', 'CTAS', 'CTRA', 'CTSH', 'CTVA', 'CVS', 'CVX', 'CZR', 'D', 'DAL', 'DD', 'DE', 
    'DG', 'DGX', 'DHI', 'DHR', 'DIS', 'DLR', 'DLTR', 'DOV', 'DOW', 'DPZ', 'DRI', 'DTE', 'DUK', 'DVA', 'DVN', 'DXCM',
    'EA', 'EBAY', 'ECL', 'ED', 'EFX', 'EG', 'EIX', 'EL', 'ELV', 'EMN', 'EMR', 'ENPH', 'EOG', 'EPAM', 'EQIX', 'EQR',
    'EQT', 'ES', 'ESS', 'ETN', 'ETR', 'ETSY', 'EVRG', 'EW', 'EXC', 'EXPD', 'EXPE', 'EXR', 'F', 'FAST', 'FCX',
    'FDS', 'FDX', 'FE', 'FFIV', 'FI', 'FICO', 'FIS', 'FITB', 'FL', 'FLEX', 'FLR', 'FLS', 'FMC', 'FOXA',
    'FOXF', 'FSLR', 'FTNT', 'FTV', 'GD', 'GE', 'GEN', 'GILD', 'GIS', 'GL', 'GLW', 'GM', 'GNRC', 'GOOG',
    'GOOGL', 'GPC', 'GPN', 'GRMN', 'GS', 'GWW', 'HAL', 'HAS', 'HBAN', 'HCA', 'HD', 'HIG', 'HII', 'HLT',
    'HOLX', 'HON', 'HPE', 'HPQ', 'HRL', 'HSIC', 'HST', 'HSY', 'HUBB', 'HUM', 'HWM', 'IBM', 'ICE', 'IDXX', 'ILMN',
    'INCY', 'INTC', 'INTU', 'IP', 'IPG', 'IQV', 'IR', 'IRM', 'ISRG', 'IT', 'ITW', 'IVZ', 'J', 'JBHT', 'JCI', 'JKHY',
    'JNJ', 'JPM', 'K', 'KEY', 'KEYS', 'KHC', 'KIM', 'KLAC', 'KMB', 'KMI', 'KO', 'KR', 'L', 'LDOS',
    'LEN', 'LH', 'LHX', 'LIN', 'LKQ', 'LLY', 'LMT', 'LNC', 'LNT', 'LOW', 'LRCX', 'LUMN', 'LUV', 'LVS', 'LW',
    'LYB', 'LYV', 'MA', 'MAA', 'MAR', 'MAS', 'MCD', 'MCHP', 'MCK', 'MCO', 'MDLZ', 'MDT', 'MET', 'META', 'MGM',
    'MHK', 'MKC', 'MKTX', 'MLM', 'MMC', 'MMM', 'MNST', 'MO', 'MOS', 'MPC', 'MPWR', 'MRK', 'MRNA', 'MRVL',
    'MS', 'MSCI', 'MSFT', 'MSI', 'MTB', 'MTCH', 'MTD', 'MU', 'NCLH', 'NDAQ', 'NEE', 'NEM', 'NFLX', 'NI', 'NKE',
    'NOC', 'NOW', 'NRG', 'NSC', 'NTAP', 'NTRS', 'NUE', 'NVDA', 'NVR', 'NWL', 'NWSA', 'NXPI', 'O', 'ODFL', 'OGN',
    'OKE', 'ON', 'ORCL', 'ORLY', 'OTIS', 'OXY', 'PARA', 'PAYC', 'PAYX', 'PCAR', 'PCG', 'PEP', 'PFE', 'PFG', 'PG',
    'PGR', 'PH', 'PHM', 'PKG', 'PLD', 'PM', 'PNC', 'PNR', 'PNW', 'PODD', 'PPG', 'PPL', 'PRU', 'PSA', 'PSX', 'PTC',
    'PWR', 'PWR', 'PYPL', 'QCOM', 'QRVO', 'RCL', 'REG', 'REGN', 'RF', 'RHI', 'RJF', 'RL', 'RMD',
    'ROK', 'ROL', 'ROP', 'ROST', 'RSG', 'RTX', 'SBAC', 'SBUX', 'SCHW', 'SEDG', 'SEE', 'SHW', 'SJM', 'SLB',
    'SNA', 'SNPS', 'SO', 'SPG', 'SPGI', 'SPY', 'SRE', 'STE', 'STLD', 'STT', 'STX', 'STZ', 'SWK', 'SWKS', 'SYF',
    'SYK', 'SYY', 'T', 'TAP', 'TDG', 'TDY', 'TECH', 'TEL', 'TER', 'TFC', 'TFX', 'TGT', 'TJX', 'TMO', 'TMUS',
    'TPR', 'TRGP', 'TRMB', 'TROW', 'TRV', 'TSCO', 'TSLA', 'TSN', 'TT', 'TTWO', 'TXN', 'TXT', 'TYL', 'UAL', 'UDR',
    'UHS', 'ULTA', 'UNH', 'UNP', 'UPS', 'URI', 'USB', 'V', 'VFC', 'VLO', 'VMC', 'VRSK', 'VRSN', 'VRTX',
    'VTR', 'VTRS', 'VZ', 'WAB', 'WAT', 'WBA', 'WDC', 'WEC', 'WELL', 'WFC', 'WHR', 'WM', 'WMB', 'WMT', 'WRB',
    'WST', 'WTW', 'WY', 'WYNN', 'XEL', 'XOM', 'XRAY', 'XYL', 'YUM', 'ZBH', 'ZBRA', 'ZION', 'ZTS'
]


# Hacim artışı oranı
VOLUME_RATIO = 1.1

# Timeframe ayarı
TIMEFRAME = "1d"
INTERVAL = "1d"

# Telegram kanal
CHANNEL = channel_05

def is_long_signal(df):
    if len(df) < 8:  # EMA8 için en az 8 mum
        return False

    # MultiIndex kolon varsa düzelt
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # EMA8 hesapla
    df["ema8"] = df["Close"].ewm(span=8, adjust=False).mean()

    # Hacim ve fiyat kontrolleri
    vol_prev = df['Volume'].iloc[-2]
    close_prev = df['Close'].iloc[-2]
    ema8_prev = df['ema8'].iloc[-2]

    vol_last = df['Volume'].iloc[-1]
    close_last = df['Close'].iloc[-1]
    open_last = df['Open'].iloc[-1]
    ema8_last = df['ema8'].iloc[-1]

    return (
        close_prev <= ema8_prev
        and close_last > ema8_last
        and vol_last > vol_prev * VOLUME_RATIO
        and close_last > open_last
    )

def scan_symbols():
    results = []
    for symbol in US_SYMBOLS:
        try:
            df = yf.download(symbol, period="1mo", interval=INTERVAL, progress=False, auto_adjust=False)
            if df is not None and not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                if is_long_signal(df):
                    vol = df['Volume'].iloc[-1]
                    close = df['Close'].iloc[-1]
                    value = vol * close
                    results.append({"symbol": symbol, "volume_value": value})
        except Exception as e:
            print(f"Hata: {symbol} - {e}")

    results = sorted(results, key=lambda x: x["volume_value"], reverse=True)
    return results[:20]

def send_message(channel_id, result_list):
    if not result_list:
        msg = f"***\n{TIMEFRAME.upper()} taramasında uygun hisse bulunamadı.\n***"
        if channel_id:
            send_message_to_telegram(channel_id, msg)
        print(msg)
        return

    message = f"***\nTime Frame: {TIMEFRAME.upper()}\n***\n\n*** SONUÇLAR ***\n\n"
    for item in result_list:
        message += f"{item['symbol']} - İşlem Hacmi: {item['volume_value']:,.2f} $\n"

    print(message)
    if channel_id:
        send_message_to_telegram(channel_id, message)

def worker():
    print(f"[{datetime.datetime.now(datetime.timezone.utc)}] 1d timeframe taraması başlıyor...")
    results = scan_symbols()
    send_message(CHANNEL, results)

def scheduler_loop():
    worker()

    while True:
        now = datetime.datetime.now(datetime.timezone.utc)
        if now.hour == 20 and now.minute == 55:  # UTC 20:55 ≈ New York 16:55
            worker()

        time.sleep(30)

if __name__ == "__main__":    
    send_message_to_telegram(CHANNEL, f"🔔 USSTOCK Strategy 1d zaman dilimi için başlatıldı.")
    scheduler_loop()
