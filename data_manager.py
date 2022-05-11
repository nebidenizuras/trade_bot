from binance.client import Client
import user_api_key
import csv
from tqdm import tqdm
from time import sleep
import pandas as pd 
from datetime import timedelta
import pandas_ta as tb
from operator import index
import operator

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
#client = Client(user_api_key.TESTNET_API_KEY, user_api_key.TESTNET_API_SECRET_KEY)


# Write Historical Data To File
def historical_data_write_to_file(symbol, timeFrame, candlesticks):
    csvFileW = open(symbol + "_" + timeFrame +".csv", "w", newline='')
    klines_writer = csv.writer(csvFileW, delimiter=",")

    for candlestick in candlesticks:
        klines_writer.writerow (candlestick)
    
    csvFileW.close()

# Get Historical Data
def get_historical_data_list(market):
    symbolList = ["APEUSDT"]#["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "AVAXUSDT", "NEARUSDT", "LUNAUSDT", "WAVESUSDT"]
    timeFrame= client.KLINE_INTERVAL_15MINUTE
    startDateOfData = "20 April, 2022"
    endDateOfData = "27 April, 2022"

    for symbol in tqdm(symbolList):
        print("\nStarted Data Downloading...: " + symbol + " " + timeFrame + " Time Frame")
        
        if (market == "Spot"):
            candlesticks = client.get_historical_klines(symbol, timeFrame, startDateOfData, endDateOfData)
        elif (market == "Future"):
            candlesticks = client.futures_historical_klines(symbol, timeFrame, startDateOfData, endDateOfData)
        
        historical_data_write_to_file(symbol, timeFrame, candlesticks)

    print("Finished Data Downloading...")

# Get Historical Data of Symbol
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

# Get Hype Symbol List
def get_calculated_hype_symbol_list(market, interval, symbolList):
    hypeRate = 0
    symbol = ""
    searchList = {}
    candleTime = 0

    # Teknik Analiz
    rsiPeriod = 13
    limit = rsiPeriod * 6

    for symbol in symbolList:
        if (market == "Spot"):
            candles = client.get_klines(symbol=symbol, interval=interval, limit=limit) 
        elif (market == "Future"):
            candles = client.futures_klines(symbol=symbol, interval=interval, limit=limit)

        ## Get Data
        df = pd.DataFrame(candles, columns=['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
                                            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                                            'taker_buy_quote_asset_volume', 'ignore']) 
        
        ## Clean data 
        df = df[['openTime', 'open', 'high', 'low', 'close', 'closeTime']]       
        df['openTime'] = pd.to_datetime(df["openTime"], unit="ms") + timedelta(hours=3)
        df['closeTime'] = pd.to_datetime(df["closeTime"], unit="ms") + timedelta(hours=3)
        df['high'] = df['high'].astype('float')
        df['open'] = df['open'].astype('float') 
        df['close'] = df['close'].astype('float')          
        df['low'] = df['low'].astype('float')
        df["RSI"] = tb.rsi(df["close"],rsiPeriod)
        
        ## Calculate Hype Rate
        candleTime = df['openTime'][limit-2]
        hypeRate = (df['high'][limit-2] / df['low'][limit-2]) + abs(df['RSI'][limit-2])
        hypeRate = round(hypeRate,5)

        ## Add to hype list
        if hypeRate >= 0:
            searchList[symbol] = hypeRate

    ## Sort from biggest to smallest
    searchList = dict(sorted(searchList.items(),key=operator.itemgetter(1),reverse = True)) # ascending order   

    return searchList, candleTime

# Get Current Price of Symbol
def get_current_price_of_symbol(coin_symbol, market='Future'):
    info = []

    if (market == "Spot"):
        info = client.get_symbol_ticker(symbol=coin_symbol)
    elif (market == "Future"):
        info = client.futures_symbol_ticker(symbol=coin_symbol)

    price = float(info.get('price'))    
    time = info.get('time')

    return price

# Get Current Server Time as UTC+3
def get_current_time(market='Future'):
    info = []

    if (market == "Spot"):
        info = client.get_server_time()
    elif (market == "Future"):
        info = client.futures_time()

    time = str(pd.to_datetime(info.get('serverTime'), unit='ms') + timedelta(hours=3))
    timeStr = time.split(".", 1)[0]

    return timeStr

# Get Minimum Lot Size For Order
def get_min_lot_size(symbol: str, market='Future'):
    return client.get_symbol_info(symbol)['filters'][2]['minQty']

# Get Base Asset Name
def get_base_asset(symbol: str, market='Future'):
    return client.get_symbol_info(symbol)['baseAsset']

# Get Tick Size Of Symbol (Step)
def get_tick_step_size(symbol: str, market='Future'):
    tick_step = 0
    #tick_size = client.get_symbol_info(symbol)['filters'][0]['tickSize']  
    tick_size = get_min_lot_size(symbol, market)

    for i in tick_size:
        if i == str(0):
            tick_step += 1
        elif i == str(1):
            break 
   
    return tick_step

# Get Wallet
def get_wallet(market='Future'):
    result = []
    
    if (market == "Spot"):
        balances = client.get_account()['balances']
    elif (market == "Future"):
        balances = client.futures_account()['balances']

    for i in balances:
        if float(i['free'])*get_current_price_of_symbol(f"{i['asset']}USDT",market)>10:
            result.append(f"{i['asset']}USDT")

    return result

# Get Wallet
def get_symbol_free_quantity_in_wallet(symbol: str, market='Future'):
    quantity = float(0)
    
    if (market == "Spot"):
        balances = client.get_account()['balances']
    elif (market == "Future"):
        balances = client.futures_account()['balances']

    for i in balances:
        if str(i['asset']) == str(symbol):
            quantity = i['free']

    return quantity

# Get Precision
def get_precision(symbol: str, market='Future'):    
    info = []
    pricePrecision = 0

    if (market == "Spot"):
        info = client.get_exchange_info()   
    elif (market == "Future"):
        info = client.futures_exchange_info()   
    
    pricePrecision = {si['symbol']:si['quantityPrecision'] for si in info['symbols'] if si['symbol'] in symbol}
       
    return int(pricePrecision[symbol]) 