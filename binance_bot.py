from binance.client import Client  

import pandas as pd 
import winsound 
import user_api_key 
import time 
from ta.trend import EMAIndicator 
from ta.momentum import RSIIndicator 
  
import matplotlib.pyplot as plt

from datetime import datetime 
import requests 
import tkinter 
from tkinter import * 
from threading import Thread 

import telegram_bot


symbol = 'BTCUSDT' 
interval = '4h' 
limit = 50
 
def calculate_trade_strategy():
    client = Client(user_api_key.key_id,user_api_key.secret_key_id) 
    candles = client.get_klines(symbol=symbol, interval=interval, limit=limit) 
 
    df = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
                                        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                                        'taker_buy_quote_asset_volume', 'ignore']) 
    num_rows = df.shape[0] # Make sure that num_rows is correct in case 1000 periods haven't happened yet 

    ## Clean data 
    df = df[['open_time', 'open', 'high', 'low', 'close', 'close_time', 'volume']] 
    df['open_time'] = pd.to_datetime(df["open_time"], unit="ms")
    df['close_time'] = pd.to_datetime(df["close_time"], unit="ms")
    df['open'] = df['open'].astype('float') 
    df['close'] = df['close'].astype('float') 
    df['high'] = df['high'].astype('float') 
    df['low'] = df['low'].astype('float') 
    df['volume'] = df['volume'].astype('float')
    serverTime = client.get_server_time() 
    serverTime = time.strftime('%m.%d.%Y %H:%M:%S',time.gmtime(serverTime['serverTime']/1000.)) 
 
    #create prices for drawing
    prices = pd.DataFrame({'open': df['open'].array,
                        'close': df['close'].array,
                        'high': df['high'].array,
                        'low': df['low'].array},
                        index=pd.date_range(df['open_time'][0], periods=limit, freq=interval))
    #draw_candle_chart(prices)

    #ema9  = EMAIndicator(df["close"],9)    
    #print(rsi(df['close'],14,False)) 
    rsi = RSIIndicator(df["close"],14) 
    df["RSI"] = rsi.rsi() 
    #mesaj = serverTime + "  " + df['RSI'][limit-1] 
    print("\n***" + symbol + "***\n")
    print(df)
    #telegram_bot.send_message(df['RSI'][limit-2]) 
    #print(df["RSI"])


def draw_candle_chart(prices):
    #display DataFrame
    print(prices)

    #create figure
    plt.figure()

    plt.title(symbol)

    #define width of candlestick elements
    width = .1
    width2 = .02

    #define up and down prices
    up = prices[prices.close>=prices.open]
    down = prices[prices.close<prices.open]

    #define colors to use
    col1 = 'green'
    col2 = 'red'

    #plot up prices
    plt.bar(up.index,up.close-up.open,width,bottom=up.open,color=col1)
    plt.bar(up.index,up.high-up.close,width2,bottom=up.close,color=col1)
    plt.bar(up.index,up.low-up.open,width2,bottom=up.open,color=col1)

    #plot down prices
    plt.bar(down.index,down.close-down.open,width,bottom=down.open,color=col2)
    plt.bar(down.index,down.high-down.open,width2,bottom=down.open,color=col2)
    plt.bar(down.index,down.low-down.close,width2,bottom=down.close,color=col2)


    #rotate x-axis tick labels
    plt.xticks(rotation=45, ha='right')

    plt.autoscale()

    #display candlestick chart
    plt.show()