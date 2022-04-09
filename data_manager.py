from binance import Client
import user_api_key
import csv
from tqdm import tqdm

""" 
 ***    Data List   ***
[Open time, Open, High, Low, Close, Volume, Close time, 
 Quote asset volume, Number of trades, Taker buy base asset volume, 
 Taker buy quote asset volume, Ignore]
"""

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

client = Client(user_api_key.key_id, user_api_key.secret_key_id)
symbolList = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "AVAXUSDT", "NEARUSDT"]
timeFrame= client.KLINE_INTERVAL_3MINUTE

startDateOfData = "1 January, 2020"
endDateOfData = "9 April, 2022"

def historical_data_write_to_file():
    csvFileW = open(symbol + "_" + timeFrame +".csv", "w", newline='')
    klines_writer = csv.writer(csvFileW, delimiter=",")

    for candlestick in candlesticks:
        klines_writer.writerow (candlestick)
    
    csvFileW.close()

# Get Historical Data
for symbol in tqdm(symbolList):
    print("\nStarted Data Downloading...: " + symbol + " " + timeFrame + " Time Frame")
    candlesticks = client.get_historical_klines(symbol, timeFrame, startDateOfData, endDateOfData)
    historical_data_write_to_file()

print("Finished Data Downloading...")
