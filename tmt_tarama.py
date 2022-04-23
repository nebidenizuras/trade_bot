from operator import index
import array as arr
from binance.client import Client  
import pandas as pd 
import user_api_key 
import time   
from telegram_bot import send_message_tarama, warn
from datetime import datetime 
from datetime import timedelta
from ta.momentum import RSIIndicator
from data_manager import get_symbol_list

client = Client(user_api_key.key_id,user_api_key.secret_key_id) 

# Teknik Analiz
rsiPeriod = 13

# Parite Bilgileri
timeFrame = 60
interval = '1h' 
symbol = ""
limit = rsiPeriod * 2

symbolListFuture = get_symbol_list("USDT", "Future")
symbolListSpot = get_symbol_list("USDT", "Spot")
symbolList = ""

debugMsg = ""
candleTime = 0
hypeRate = 0
rateList = []
searchList = []
searchListOrdered = []

def calculate_hype_point(market):
    global symbolList
    global symbolListFuture
    global symbolListSpot

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
        rsi = RSIIndicator(df["high"],rsiPeriod)
        df["RSI"] = rsi.rsi()
        
        candleTime = df['openTime'][limit-2]
        hypeRate = (df['high'][limit-2] / df['low'][limit-2]) * abs(df['RSI'][limit-2] - 50)
        rateList.append(hypeRate)

    searchList = dict(zip(symbolList, rateList))
    searchListOrdered = dict(sorted(searchList.items(),key=lambda x:x[1],reverse = True)) # ascending order

    debugMsg = warn + " " + market + " Coin Liste Taraması (" + interval + ")\n\n"
    debugMsg += "Hesaplanan Mum Zamanı : " + str(candleTime) + "\n\n"

    counter = 0
    for i in searchListOrdered:
        debugMsg += str(i) + " : " + str(round(searchListOrdered[i], 3)) + "\n"       

    send_message_tarama(debugMsg)
    debugMsg = ""

    # Sembol listesini güncelle, silinen ve eklenen coinler güncellensin
    symbolListFuture = get_symbol_list("USDT", "Future")
    symbolListSpot = get_symbol_list("USDT", "Spot")

    # Aynı mum içinde tekrar tekrar işlem yapmasın diye bir sonraki mum açılışını bekle
    # Wait 1 second until we are synced up with the 'every 1 hour' clock            
    while datetime.now().minute not in {1}: 
        time.sleep(1)

while (1):
    calculate_hype_point("Future")
    time.sleep(1)        