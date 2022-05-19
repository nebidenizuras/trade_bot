from http import client
from Indicators import heikin_ashi
import pandas_ta as ta
import pandas as pd
import time
import schedule
import ccxt
from datetime import datetime 
from time import sleep
from datetime import timedelta 
import requests 
from threading import Thread 
from data_manager import get_symbol_list
from threading import Thread
from telegram_bot import warn

def send_message(message): 
    channel_id = "-1001509604144"
    message_url = "https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c/sendMessage"
    #print(message)
    #'''
    #iş yükü parçacıgı için 
    def thread1(): 
        requests.post(url=message_url ,data={"chat_id":channel_id,"text":message}).json()  

    #thread ile fonksiyonu başlatır 
    th = Thread(target=thread1) 
    th.start()
    #'''

def compute_process(timeFrame):
    long_signal_count = 0
    short_signal_count = 0

    longMsg = warn + " LONG Sinyaller (" + timeFrame + ")\n\n" 
    shortMsg = warn + " SHORT Sinyaller (" + timeFrame + ")\n\n" 
    exchange = ccxt.binance({
    "apiKey": "",
    "secret": "",
    'options': {
    'defaultType': 'future'
    },
    'enableRateLimit': True
    })  

    Limit = 100
    symbol_list = get_symbol_list('USDT','Future')

    # RSI SET
    rsi_low_limit = 30
    rsi_high_limit = 70
    
    for Symbol in symbol_list:
        try:
            # Get Data
            bars = exchange.fetch_ohlcv(symbol = Symbol, timeframe=timeFrame, since = None, limit = Limit)
                        
            # Prepare Candle Data
            df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
            dfHA = heikin_ashi.calculate_heikin_ashi(df)
            df['open'] = dfHA['open'].astype('float')
            df['close'] = dfHA['close'].astype('float')
            df['high'] = dfHA['high'].astype('float')
            df['low'] = dfHA['low'].astype('float')
            df['timestamp'] = pd.to_datetime(df['timestamp'],unit= "ms") + timedelta(hours=3)

            # Calculate RSI
            df['RSI'] = ta.rsi(df["close"], length=14)
            rsi_value = df["RSI"][len(df.index) - 1]

            # Calculate Vortex
            vortex = ta.vortex(high=df['high'], low=df['low'], close=df['close'], length=14)
            df['VTLONG'] = vortex['VTXP_14']
            df['VTSHORT'] = vortex['VTXM_14']            
            vortex_long_value = df['VTLONG'][len(df.index) - 1]
            vortex_short_value = df['VTSHORT'][len(df.index) - 1]            

            # Find LONG Positions
            if (rsi_value <= rsi_low_limit) and (vortex_long_value < 0.9):
                longMsg += Symbol + "\n"
                long_signal_count += 1
            
            # Find SHORT Positions
            if (rsi_value >= rsi_high_limit) and (vortex_short_value < 0.9):
                shortMsg += Symbol + "\n"
                short_signal_count += 1

        except Exception as e:
                debugMsg = warn + " Error : \n" + str(e) + "\n\n"
                debugMsg += warn + "\nSistem Tekrar Bağlanmayı Deniyor...\n" + warn
                send_message(debugMsg)
                sleep(5)
                continue

    # Bilgileri Gönder    
    if(long_signal_count == 0):
        longMsg += "----------\n"  

    if(short_signal_count == 0):
        shortMsg += "----------\n"    

    send_message(longMsg + "\n" + shortMsg)


def job_1m():
    t = Thread(target=compute_process, args=["1m"])
    t.start()

def job_5m():    
    t = Thread(target=compute_process, args=["5m"])
    t.start()

def job_15m():
    t = Thread(target=compute_process, args=["15m"])
    t.start()

def job_1h():    
    t = Thread(target=compute_process, args=["1h"])
    t.start()

def job_4h():    
    t = Thread(target=compute_process, args=["4h"])
    t.start()

def job_1d():    
    t = Thread(target=compute_process, args=["1d"])
    t.start()

send_message("Bot Starting\n")

IsOK1m = False
IsOK5m = False
IsOK15m = False
IsOK1h = False
IsOK4h = False
IsOK1d = False

while True:   
    dateTime = datetime.now()

    '''
    if (dateTime.second != 1):
        IsOK1m = False
    if (dateTime.minute % 5 != 0):
        IsOK5m = False
    '''

    if (dateTime.minute % 15 != 0):
        IsOK15m = False
    if (dateTime.minute != 0):
        IsOK1h = False
        IsOK4h = False
    if (dateTime.hour != 3):
        IsOK1d = False

    '''
    if (dateTime.second == 1) and (IsOK1m == False): 
        job_1m()
        IsOK1m = True

    if (dateTime.minute % 5 == 0) and (IsOK5m == False): 
        job_5m()
        IsOK5m = True
    '''

    if (dateTime.minute % 15 == 0) and (IsOK15m == False): 
        job_15m()
        IsOK15m = True

    if (dateTime.minute == 0) and (IsOK1h == False): 
        job_1h()
        IsOK1h= True

    if (dateTime.hour in {3,7,11,15,19,23}) and (dateTime.minute == 0) and (IsOK4h == False): 
        job_4h()
        IsOK4h = True

    if (dateTime.hour == 3) and (dateTime.minute == 0) and (IsOK1d == False): 
        job_1d()
        IsOK1d = True

    time.sleep(1)

'''      
def job_1m():
    t = Thread(target=compute_process, args=["1m"])
    t.start()

def job_5m():
    t = Thread(target=compute_process, args=["5m"])
    t.start()

def job_15m():
    t = Thread(target=compute_process, args=["15m"])
    t.start()

def job_1h():
    t = Thread(target=compute_process, args=["1h"])
    t.start()

def job_4h():
    t = Thread(target=compute_process, args=["4h"])
    t.start()

def job_1d():
    t = Thread(target=compute_process, args=["1d"])
    t.start()

schedule.every(1).minutes.do(job_1m) # too much message for bot
schedule.every(5).minutes.do(job_5m) # too much message for bot
schedule.every(15).minutes.do(job_15m)
schedule.every(1).hours.do(job_1h)
schedule.every(4).hours.do(job_4h)
schedule.every(1).days.do(job_1d)

send_message("Bot Starting\n")

while True:    
    schedule.run_pending()
    time.sleep(1)
'''