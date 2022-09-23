'''
- EMA 3 Close > EMA 8 close ise long gir, short'a dönerse kapat
- EMA 3 Close < EMA 8 close ise short gir, long'a dönerse kapat
'''

from datetime import datetime   
from datetime import timedelta
from time import sleep    

from Indicators.heikin_ashi import calculate_heikin_ashi
from binance.client import Client  
from user_api_key import key_id, secret_key_id

import pandas_ta as tb
import pandas as pd 

from telegram_bot import warn, send_message_to_telegram, channel_00

from ta.trend import ema_indicator

client = Client(key_id, secret_key_id) 

islemFiyati = 0
hedefFiyati = 0
islemBuyuklugu = 0

#ATTRIBUTES
kaldirac = 1
feeOrani = 0.00027 # percent
karOrani = 0.0 # percent

baslangicPara = 100
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

ema_long_price = 0.0
ema_short_price = 0.0
current_price = 0.0

long_signal = False
short_signal = False

# Sinyal Değerleri
LongLength = 1
LongSource = "close"
ShortLength = 2 
ShortSource = "close"
TrendLength = 8 
TrendSource = "open"

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

# Parite Bilgileri
symbol = "XRPBUSD"
interval = "5m"
timeFrame = 5
limit = TrendLength * 4

df = ['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
      'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
      'taker_buy_quote_asset_volume', 'ignore']

send_message_to_telegram(channel_00, warn + warn + "Albız_v3 Started" + warn + warn)

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
        dfHA = calculate_heikin_ashi(df)
        df['open'] = dfHA['open'].astype('float')
        df['close'] = dfHA['close'].astype('float')
        df['high'] = dfHA['high'].astype('float')
        df['low'] = dfHA['low'].astype('float')
        df["LongLength"] = tb.ema(df[LongSource],LongLength)
        df["ShortLength"] = tb.ema(df[ShortSource],ShortLength)
        df["WMATREND"] = tb.wma(df[TrendSource],TrendLength)

        ema_short_price = df["ShortLength"][limit-2]
        ema_long_price = df["LongLength"][limit-2]
        wma_trend_price = df["WMATREND"][limit-2]
        current_price = df["close"][limit-1]

        long_trend = (ema_long_price > wma_trend_price) and (ema_short_price > wma_trend_price)
        short_trend = (ema_long_price < wma_trend_price) and (ema_short_price < wma_trend_price)
        long_signal = (ema_long_price > ema_short_price)
        short_signal = (ema_long_price < ema_short_price)

        ### Giriş Bilgilerini Ayarla
        if (start == False) and (position == "") and ((long_signal and long_trend) or (short_signal and short_trend)): 
            start = True       
            startTime = df["openTime"][limit-1]

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
        if (start == True) and (position == "") and (long_signal and long_trend):
            position = "Long"    

            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFiyati = current_price
            islemBuyuklugu = cuzdan * kaldirac
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee            

            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][limit-1]) + "\n"
            debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(islemBuyuklugu,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,4)) + "\n"
            debugMsg += "\n" 
            debugMsg += "\n"
            debugMsg += "Reference Bands\n" 
            debugMsg += "EMA(" + str(LongLength) + ") -> " + str(round(ema_long_price,4)) + "\n" 
            debugMsg += "EMA(" + str(ShortLength) + ") -> " + str(round(ema_short_price,4)) + "\n"
            debugMsg += "WMA(" + str(TrendLength) + ") -> " + str(round(wma_trend_price,4)) + "\n"
            debugMsg += "\n"  
            send_message_to_telegram(channel_00, debugMsg)
            debugMsg = ""  

        # Long İşlem Kapat
        if (start == True) and (position == "Long") and (short_signal):
            hedefFiyati = current_price
            karOrani = ((hedefFiyati - islemFiyati) / islemFiyati)
            islemKar = cuzdan * karOrani * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
            if (islemKar > 0):
                toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
                debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal LONG Close Take Profit\n"
            else:
                toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
                debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal LONG Close Stop Loss\n"            
            debugMsg += "\n"
            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][limit-1]) + "\n"
            debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            if (islemKar > 0):
                debugMsg += "LONG Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
            else:
                debugMsg += "LONG Order SL\t\t: " + str(round(hedefFiyati,7)) + "\n"            
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t\t: % " + str(round(karOrani * 100,3)) + "\n"                
        
            islemBitti = True

    # SHORT İŞLEM
        # Short İşlem Aç
        if (start == True) and (position == "") and (short_signal and short_trend):
            position = "Short"  

            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFiyati = current_price
            islemBuyuklugu = cuzdan * kaldirac
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee     

            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][limit-1]) + "\n"
            debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(islemBuyuklugu,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,4)) + "\n"
            debugMsg += "\n" 
            debugMsg += "\n"
            debugMsg += "Reference Bands\n" 
            debugMsg += "EMA(" + str(LongLength) + ") -> " + str(round(ema_long_price,4)) + "\n" 
            debugMsg += "EMA(" + str(ShortLength) + ") -> " + str(round(ema_short_price,4)) + "\n"
            debugMsg += "WMA(" + str(TrendLength) + ") -> " + str(round(wma_trend_price,4)) + "\n"
            debugMsg += "\n"  
            send_message_to_telegram(channel_00, debugMsg)
            debugMsg = ""  

        # Short İşlem Kapat
        if (start == True) and (position == "Short") and (long_signal):
            hedefFiyati = current_price
            karOrani = ((islemFiyati - hedefFiyati) / islemFiyati)
            islemKar = cuzdan * karOrani * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
            if (islemKar > 0):
                toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
                debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal SHORT Close Take Profit\n"
            else:
                toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
                debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal SHORT Close Stop Loss\n"            
            debugMsg += "\n"
            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][limit-1]) + "\n"
            debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            if (islemKar > 0):
                debugMsg += "SHORT Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
            else:
                debugMsg += "SHORT Order SL\t\t: " + str(round(hedefFiyati,7)) + "\n"            
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t\t: % " + str(round(karOrani * 100,3)) + "\n"  

            islemBitti = True 

        if islemBitti == True:  
            debugMsg += "\n"
            debugMsg += "Report\n"
            debugMsg += "\n"
            debugMsg += "Strategy\t: " + str(symbol) + " (" + str(kaldirac) + "x) (" + str(interval) + ") WMA" + str(TrendLength) + " " + str(TrendSource) + " EMA" + str(LongLength) + " " + str(LongSource) + " EMA" + str(ShortLength) + " " + str(ShortSource) + "\n"
            debugMsg += "Invest\t\t: " + str(round(baslangicPara,7)) + "\n"
            debugMsg += "ROI\t\t: " + str(round(toplamKar,7)) + "\n"
            debugMsg += "Total Fee\t: " + str(round(toplamFee,3)) + "\n"
            debugMsg += "Fund\t\t: " + str(round(cuzdan,7)) + "\n"
            debugMsg += "ROI\t\t: % " + str(round((toplamKar / baslangicPara) * 100,3)) + "\n"
            debugMsg += "Net ROI\t\t: % " + str(round((((cuzdan-toplamFee) - baslangicPara) / baslangicPara) * 100,3)) + "\n"
            debugMsg += "\n"
            debugMsg += "Total Orders\t: " + str(toplamIslemSayisi) + "\n"
            debugMsg += "TP Orders\t: " + str(toplamKarliIslemSayisi) + "\n"
            debugMsg += "SL Orders\t: " + str(toplamZararKesIslemSayisi) + "\n"
            debugMsg += "Gain Orders\t: % " + str(round((toplamKarliIslemSayisi / toplamIslemSayisi) * 100,1)) + "\n"
            debugMsg += "Lose Orders\t: % " + str(round((toplamZararKesIslemSayisi / toplamIslemSayisi) * 100,1)) + "\n"          
            send_message_to_telegram(channel_00, debugMsg)
            debugMsg = "" 

            # Zarar Kes yaparak Stop olduysak yeni mumu bekle
            if(islemKar < 0):
                while(0 <= datetime.now().second <= 1):
                    sleep(1)                    
                
            islemBitti = False
            position = ""   
            start = False         
            islemKar = 0
            islemFee = 0
            islemFiyati = 0
            hedefFiyati = 0

        if (cuzdan + 10) < toplamFee:
            debugMsg = warn + warn + warn + "\nCüzdanda Para Kalmadı\n" + warn + warn + warn
            send_message_to_telegram(channel_00, debugMsg)
            debugMsg = "" 
            quit() 

        sleep(1) 
    except Exception as e:
        debugMsg = "Error : " + str(e) + "\n\n"
        debugMsg += warn + "\nSistem Durduruluyor...\n" + warn
        send_message_to_telegram(channel_00, debugMsg)
        debugMsg = ""
        quit()