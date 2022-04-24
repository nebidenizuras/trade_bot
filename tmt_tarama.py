from operator import index
import array as arr
from binance.client import Client  
import pandas as pd 
import pandas_ta as tb
import user_api_key 
import time   
from telegram_bot import send_message_tarama, warn
from datetime import datetime 
from datetime import timedelta
from ta.momentum import RSIIndicator
from data_manager import get_symbol_list
import operator

client = Client(user_api_key.key_id,user_api_key.secret_key_id) 

# Teknik Analiz
rsiPeriod = 12

# Parite Bilgileri
timeFrame = 5
interval = '5m' 
symbol = ""
limit = rsiPeriod * 3

symbolListFuture = get_symbol_list("USDT", "Future")
symbolListSpot = get_symbol_list("USDT", "Spot")
symbolList = ""

debugMsg = ""
candleTime = 0
hypeRate = 0
searchList = {}

def calculate_hype_point(market):
    global symbolList
    global symbolListFuture
    global symbolListSpot
    global searchList

    if (market == "Spot"):
        symbolList = symbolListSpot
    elif (market == "Future"):
        symbolList = symbolListFuture

    for symbol in symbolList:
        if (market == "Spot"):
            candles = client.get_klines(symbol=symbol, interval=interval, limit=limit) 
        elif (market == "Future"):
            candles = client.futures_klines(symbol=symbol, interval=interval, limit=limit)

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
        
        candleTime = df['openTime'][limit-2]
        hypeRate = (df['high'][limit-2] / df['low'][limit-2]) + abs(df['RSI'][limit-2] - 50)
        hypeRate = round(hypeRate,3)
        if hypeRate >= 0:
            searchList[symbol] = hypeRate

    searchList = dict(sorted(searchList.items(),key=operator.itemgetter(1),reverse = True)) # ascending order

    debugMsg = warn + " " + market + " Coin Liste Taraması (" + interval + ")\n\n"
    debugMsg += "Hesaplanan Mum Zamanı : " + str(candleTime) + "\n\n"

    for key, value in searchList.items():
        debugMsg += str(key) + " : " + str(value) + "\n"       

    send_message_tarama(debugMsg)
    debugMsg = ""

    # Sembol listesini güncelle, silinen ve eklenen coinler güncellensin
    symbolListFuture = get_symbol_list("USDT", "Future")
    symbolListSpot = get_symbol_list("USDT", "Spot")

    time.sleep(30)

    # Aynı mum içinde tekrar tekrar işlem yapmasın diye bir sonraki mum açılışını bekle
    # Wait 1 second until we are synced up with the 'every 1 hour' clock  
    while datetime.now().minute not in {0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55}: 
    #while datetime.now().minute % timeFrame != 0: 
        time.sleep(5)         

while (1):
    calculate_hype_point("Future")
    time.sleep(1)        