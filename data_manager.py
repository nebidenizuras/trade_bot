from binance import Client
import user_api_key
import csv
from tqdm import tqdm
from time import sleep

"""
# https://www.binance.com/en/landing/data
# https://github.com/binance/binance-public-data/tree/master/Futures_Order_Book_Download
# https://github.com/binance/binance-public-data/
"""

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

def historical_data_write_to_file(symbol, timeFrame, candlesticks):
    csvFileW = open(symbol + "_" + timeFrame +".csv", "w", newline='')
    klines_writer = csv.writer(csvFileW, delimiter=",")

    for candlestick in candlesticks:
        klines_writer.writerow (candlestick)
    
    csvFileW.close()

# Get Historical Data
def get_historical_data_list(market):
    symbolList = ["MTLUSDT"]#["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "AVAXUSDT", "NEARUSDT", "LUNAUSDT", "WAVESUSDT"]
    timeFrame= client.KLINE_INTERVAL_5MINUTE
    startDateOfData = "20 April, 2022"
    endDateOfData = "24 April, 2022"

    for symbol in tqdm(symbolList):
        print("\nStarted Data Downloading...: " + symbol + " " + timeFrame + " Time Frame")
        
        if (market == "Spot"):
            candlesticks = client.get_historical_klines(symbol, timeFrame, startDateOfData, endDateOfData)
        elif (market == "Future"):
            candlesticks = client.futures_historical_klines(symbol, timeFrame, startDateOfData, endDateOfData)
        
        historical_data_write_to_file(symbol, timeFrame, candlesticks)

    print("Finished Data Downloading...")

def get_historical_data_symbol(market, symbol, startDateOfData, endDateOfData, timeFrame):
    print("\nStarted Data Downloading...: " + symbol + " " + timeFrame + " Time Frame")
    
    if (market == "Spot"):
        candlesticks = client.get_historical_klines(symbol, timeFrame, startDateOfData, endDateOfData)
    elif (market == "Future"):
        candlesticks = client.futures_historical_klines(symbol, timeFrame, startDateOfData, endDateOfData)
    
    historical_data_write_to_file(symbol, timeFrame, candlesticks)

    print("Finished Data Downloading...")

# Get Symbol Lists of Market (Future or Spot)
def get_symbol_list(asset, market):    
    if (market == "Spot"):
        coins = client.get_exchange_info()
    elif (market == "Future"):
        coins = client.futures_exchange_info()

    symbol_list = []
    for coin in coins['symbols']:
            if coin['quoteAsset'] == asset:  
                symbol_list.append(coin["baseAsset"] + asset) 
    
    return symbol_list

#get_historical_data_list("Future")
#get_symbol_list("USDT", "Spot")