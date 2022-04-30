'''
- EMA 3 Close > EMA 8 close ise long gir, short'a dönerse kapat
- EMA 3 Close < EMA 8 close ise short gir, long'a dönerse kapat
'''

from datetime import datetime   
from datetime import timedelta
from time import sleep    

from binance.client import Client  
from user_api_key import key_id, secret_key_id

import pandas as pd 

from telegram_bot import warn, send_message_to_telegram, channelAlbiz

from ta.trend import ema_indicator

client = Client(key_id, secret_key_id) 

islemFiyati = 0
hedefFiyati = 0
islemBuyuklugu = 0

#ATTRIBUTES
kaldirac = 1
feeOrani = 0.0004 # percent
karOrani = 0.0 # percent

baslangicPara = 111
cuzdan = baslangicPara

islemFee = 0
islemKar = 0

toplamFee = 0
toplamKar = 0

startTime = 0
stopTime = 0

position = ""
start = False
islemBitti = False

ema_buy_price = 0.0
ema_sell_price = 0.0
emaSignalPrice = 0.0
current_price = 0.0

IsEMAUpdate = False

long_signal = False
short_signal = False

# Sinyal Değerleri
emaBuy = 3   
emaBuyType = "close"
emaSell = 8    
emaSellType = "close"

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

# Parite Bilgileri
symbol = "AVAXUSDT"
interval = "1m"
timeFrame = 1
limit = emaSell * 4

df = ['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
      'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
      'taker_buy_quote_asset_volume', 'ignore']

def signal_update():
    global ema_buy_price
    global ema_sell_price
    global current_price
    global long_signal
    global short_signal

    candles = client.futures_klines(symbol=symbol, interval=interval, limit=limit) 
    df = pd.DataFrame(candles, columns=['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
                                        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                                        'taker_buy_quote_asset_volume', 'ignore']) 
    ## Clean data 
    df = df[['openTime', 'open', 'high', 'low', 'close', 'closeTime']]       
    df['open'] = df['open'].astype('float')
    df['close'] = df['close'].astype('float')
    df['high'] = df['high'].astype('float')
    df['low'] = df['low'].astype('float')
    df["openTime"] = pd.to_datetime(df["openTime"],unit= "ms") + timedelta(hours=3)
    df["closeTime"] = pd.to_datetime(df["closeTime"],unit= "ms") + timedelta(hours=3)
    df["EMABUY"] = ema_indicator(df[emaBuyType],emaBuy)
    df["EMASELL"] = ema_indicator(df[emaSellType],emaSell)

    ema_sell_price = df["EMASELL"][limit-1]
    ema_buy_price = df["EMABUY"][limit-1]
    current_price = df["close"][limit-1]

    long_signal = (ema_buy_price > ema_sell_price)
    short_signal = (ema_buy_price < ema_sell_price)
    
#signal_update()

while(True):
    try:
        candles = client.futures_klines(symbol=symbol, interval=interval, limit=limit) 
        df = pd.DataFrame(candles, columns=['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
                                            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                                            'taker_buy_quote_asset_volume', 'ignore']) 
        ## Clean data 
        df = df[['openTime', 'open', 'high', 'low', 'close', 'closeTime']]       
        df['open'] = df['open'].astype('float')
        df['close'] = df['close'].astype('float')
        df['high'] = df['high'].astype('float')
        df['low'] = df['low'].astype('float')
        df["openTime"] = pd.to_datetime(df["openTime"],unit= "ms") + timedelta(hours=3)
        df["closeTime"] = pd.to_datetime(df["closeTime"],unit= "ms") + timedelta(hours=3)
        df["EMABUY"] = ema_indicator(df[emaBuyType],emaBuy)
        df["EMASELL"] = ema_indicator(df[emaSellType],emaSell)

        ema_sell_price = df["EMASELL"][limit-1]
        ema_buy_price = df["EMABUY"][limit-1]
        current_price = df["close"][limit-1]

        long_signal = (ema_buy_price > ema_sell_price)
        short_signal = (ema_buy_price < ema_sell_price)

        ### Giriş Bilgilerini Ayarla
        if (start == False) and (position == "") and ((long_signal == True) or (short_signal == True)): 
            start = True       
            startTime =  df["openTime"][limit-1]
            debugMsg = ""
            debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
            debugMsg += warn +  " " + str(toplamIslemSayisi + 1) + ". Signal "
            if long_signal:
                debugMsg += "LONG\n"
            elif short_signal:
                debugMsg += "SHORT\n"
            debugMsg += "\n"

    ### LONG İŞLEM ###
        # Long İşlem Aç
        if (start == True) and (position == "") and (long_signal == True):
            position = "Long"    

            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFiyati = current_price
            islemBuyuklugu = cuzdan * kaldirac
            islemFee = islemBuyuklugu * kaldirac * feeOrani
            toplamFee += islemFee            

            debugMsg += "Order Time\t\t: " + str(df["openTime"][limit-1]) + "\n"
            debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            #debugMsg += "LONG Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t\t: " + str(round(islemFee,4)) + "\n"
            debugMsg += "\n" 
            debugMsg += "\n"
            debugMsg += "Reference Bands\n" 
            debugMsg += "EMA(" + str(emaBuy) + ") -> " + str(round(ema_buy_price,4)) + "\n" 
            debugMsg += "EMA(" + str(emaSell) + ") -> " + str(round(ema_sell_price,4)) + "\n"
            debugMsg += "\n"  
            send_message_to_telegram(channelAlbiz, debugMsg)
            debugMsg = ""  

        # Long İşlem Kapat
        if (start == True) and (position == "Long") and (short_signal == True):
            hedefFiyati = ema_sell_price
            karOrani = ((hedefFiyati - islemFiyati) / islemFiyati)
            islemKar = cuzdan * karOrani * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
            debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal LONG Close Take Profit \n"
            debugMsg += "\n"
            debugMsg += "Order Time\t\t: " + str(df["openTime"][limit-1]) + "\n"
            debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "LONG Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t\t: % " + str(round(karOrani * 100,3)) + "\n"

            if(islemKar > 0):
                toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            else:
                toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
        
            islemBitti = True

    # SHORT İŞLEM
        # Short İşlem Aç
        if (start == True) and (position == "") and (short_signal == True):
            position = "Short"  

            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFiyati = current_price
            islemBuyuklugu = cuzdan * kaldirac
            islemFee = islemBuyuklugu * kaldirac * feeOrani
            toplamFee += islemFee     

            debugMsg += "Order Time\t\t: " + str(df["openTime"][limit-1]) + "\n"
            debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            #debugMsg += "SHORT Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t\t: " + str(round(islemFee,4)) + "\n"
            debugMsg += "\n" 
            debugMsg += "\n"
            debugMsg += "Reference Bands\n" 
            debugMsg += "EMA(" + str(emaBuy) + ") -> " + str(round(ema_buy_price,4)) + "\n" 
            debugMsg += "EMA(" + str(emaSell) + ") -> " + str(round(ema_sell_price,4)) + "\n"
            debugMsg += "\n"  
            send_message_to_telegram(channelAlbiz, debugMsg)
            debugMsg = ""  

        # Short İşlem Kapat
        if (start == True) and (position == "Short") and (long_signal == True):
            hedefFiyati = ema_buy_price
            karOrani = ((islemFiyati - hedefFiyati) / islemFiyati)
            islemKar = cuzdan * karOrani * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
            debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal SHORT Close Take Profit \n"
            debugMsg += "\n"
            debugMsg += "Order Time\t\t: " + str(df["openTime"][limit-1]) + "\n"
            debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "SHORT Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t\t: % " + str(round(karOrani * 100,3)) + "\n"     

            if(islemKar > 0):
                toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            else:
                toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

            islemBitti = True 

        if islemBitti == True:  
            debugMsg += "\n"
            debugMsg += "Report\n"
            debugMsg += "\n"
            debugMsg += "Strategy : " + str(symbol) + " " + str(kaldirac) + "x " + str(interval) + " EMA" + str(emaBuy) + " " + str(emaBuyType) + " EMA" + str(emaSell) + " " + str(emaSellType) + "\n"
            debugMsg += "Invest\t: " + str(round(baslangicPara,7)) + "\n"
            debugMsg += "ROI\t: " + str(round(toplamKar,7)) + "\n"
            debugMsg += "Total Fee\t: " + str(round(toplamFee,3)) + "\n"
            debugMsg += "Fund\t: " + str(round(cuzdan,7)) + "\n"
            debugMsg += "ROI\t: % " + str(round((toplamKar / baslangicPara) * 100,3)) + "\n"
            debugMsg += "\n"
            debugMsg += "Total Orders\t: " + str(toplamIslemSayisi) + "\n"
            debugMsg += "TP Orders\t: " + str(toplamKarliIslemSayisi) + "\n"
            debugMsg += "SL Orders\t: " + str(toplamZararKesIslemSayisi) + "\n"
            debugMsg += "Gain Orders\t: % " + str(round((toplamKarliIslemSayisi / toplamIslemSayisi) * 100,1)) + "\n"
            debugMsg += "Lose Orders\t: % " + str(round((toplamZararKesIslemSayisi / toplamIslemSayisi) * 100,1)) + "\n"        
            send_message_to_telegram(channelAlbiz, debugMsg)
            debugMsg = "" 
                
            islemBitti = False
            position = ""   
            start = False         
            islemKar = 0
            islemFee = 0
            islemFiyati = 0
            hedefFiyati = 0

        if (cuzdan + 10) < toplamFee:
            debugMsg = warn + warn + warn + "\nCüzdanda Para Kalmadı\n" + warn + warn + warn
            send_message_to_telegram(channelAlbiz, debugMsg)
            debugMsg = "" 
            quit() 

        sleep(0.5) 
    except Exception as e:
        debugMsg = "Error : " + str(e) + "\n\n"
        debugMsg += warn + "\nSistem Durduruluyor...\n" + warn
        send_message_to_telegram(channelAlbiz, debugMsg)
        debugMsg = ""
        quit()