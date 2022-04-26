from operator import index
import array as arr
from binance.client import Client  
import pandas as pd 
import pandas_ta as tb
import user_api_key 
import time   
from telegram_bot import *
from datetime import datetime 
from datetime import timedelta
from ta.momentum import RSIIndicator
from data_manager import get_symbol_list
import operator

client = Client(user_api_key.key_id,user_api_key.secret_key_id) 

# Teknik Analiz
rsiPeriod = 21

# Parite Bilgileri
timeFrame = 1
interval = '1m' 
symbol = ""
limit = rsiPeriod * 6

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
    global candleTime

    if (market == "Spot"):
        symbolList = symbolListSpot
    elif (market == "Future"):
        symbolList = symbolListFuture

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
        hypeRate = (df['high'][limit-2] / df['low'][limit-2]) + abs(df['RSI'][limit-2] - 35)
        #hypeRate = (df['high'][limit-2] / df['low'][limit-2])
        #hypeRate = (df['high'][limit-2] / df['low'][limit-2]) + abs(df['RSI'][limit-2] - 50) # RSI kapatıldı
        hypeRate = round(hypeRate,5)

        ## Add to hype list
        if hypeRate >= 0:
            searchList[symbol] = hypeRate

    ## Sort from biggest to smallest
    searchList = dict(sorted(searchList.items(),key=operator.itemgetter(1),reverse = True)) # ascending order   

    # Update symbol lists
    symbolListFuture = get_symbol_list("USDT", "Future")
    symbolListSpot = get_symbol_list("USDT", "Spot")

def do_work_hype_coin_scanning(market):
    # Aynı mum içinde tekrar tekrar işlem yapmasın diye bir sonraki mum açılışını bekle
    # Wait 1 second until we are synced up with the 'every 5 minute' clock  
    #while datetime.now().minute not in {0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55}: 
    #while datetime.now().minute % timeFrame != 0: 
    while datetime.now().second == 0:
        time.sleep(1) 

    calculate_hype_point(market)

    debugMsg = ""
    debugMsg = warn + " " + market + " Coin Liste Taraması (" + interval + ")\n\n"
    debugMsg += "Hesaplanan Mum Zamanı : " + str(candleTime) + "\n\n"

    counter = 0
    for key, value in searchList.items():
        if(counter == 5):
            break
        debugMsg += str(key) + " : " + str(value) + "\n"       
        counter = counter + 1

    send_message_to_telegram(channelTarama, debugMsg)
    debugMsg = ""

while (1):
    do_work_hype_coin_scanning("Future")    
    time.sleep(1)        