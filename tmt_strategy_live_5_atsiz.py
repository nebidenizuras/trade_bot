'''
- Bu stratejide işleme giriş bandı Fibonacci kanalına göre belirlenmektedir.
- EMA8 değeri FIB 0.5 üzerinde ise, long işleme değmişsem long girerim (FIB 0.572)
  FIB 0.772 de kar alırım
- EMA8 değeri FIB 0.5 altında ise, short işleme değmişsem short girerim (FIB 0.428)
  FIB 0.228 de kar alırım
- Stop noktaları diğer yön işlemin açıldığı yer ve eması 0.5'e uyumlu ise
'''

from Indicators.fibonacci_retracement import calculate_fib
from operator import index
import array as arr
from binance.client import Client  
import pandas as pd 
from user_api_key import key_id, secret_key_id
import time   
from telegram_bot import *
from datetime import datetime 
from datetime import timedelta
from ta.trend import ema_indicator

client = Client(key_id, secret_key_id) 

islemFiyati = 0
hedefFiyati = 0
stopFiyati = 0

#ATTRIBUTES
kaldirac = 1
feeOrani = 0.0004 # percent
bantMinimumOran = 0.002

baslangicPara = 111
cuzdan = baslangicPara

bantReferans = 0
cikisOrani = 3 * bantReferans
girisOrani = bantReferans / 2
referansOrtaFiyat = 0
longGirisFiyat = 0
shortGirisFiyat = 0
shortStopFiyat = 0
longStopFiyat = 0
shortKarFiyat = 0
longKarFiyat = 0
emaFiyat = 0
karOrani = 0

islemFiyati = 0
hedefFiyati = 0
stopFiyati = 0

islemFee = 0
toplamFee = 0

islemKar = 0
toplamKar = 0

position = ""
start = False
startTime = 0
stopTime = 0
islemBitti = False

# Sinyal Değerleri
fibVal = 8
emaVal = 5
emaType = "open" # "open" or "close"

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

# Parite Bilgileri
timeFrame = 15
symbol = "APEUSDT"
interval = "15m"
limit = fibVal + 2

df = ['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
      'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
      'taker_buy_quote_asset_volume', 'ignore']


while(True):
    if (position == ""):
        start = False
        long_signal = False 
        short_signal = False
        limit = fibVal + 2
        candles = client.futures_klines(symbol=symbol, interval=interval, limit=limit) 
        df = pd.DataFrame(candles, columns=['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
                                            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                                            'taker_buy_quote_asset_volume', 'ignore']) 
        ## Clean data 
        df['open'] = df['open'].astype('float')
        df['close'] = df['close'].astype('float')
        df['high'] = df['high'].astype('float')
        df['low'] = df['low'].astype('float')
        df["openTime"] = pd.to_datetime(df["openTime"],unit= "ms") + timedelta(hours=3)
        df["closeTime"] = pd.to_datetime(df["closeTime"],unit= "ms") + timedelta(hours=3)
        df["EMA"] = ema_indicator(df[emaType],emaVal)
        df["FIB_1"] = calculate_fib(df,fibVal, 1)
        df["FIB_0_772"] = calculate_fib(df,fibVal, 0.772)
        df["FIB_0_572"] = calculate_fib(df,fibVal, 0.572)
        df["FIB_0_500"] = calculate_fib(df,fibVal, 0.5)
        df["FIB_0_428"] = calculate_fib(df,fibVal, 0.428)
        df["FIB_0_228"] = calculate_fib(df,fibVal, 0.228)
        df["FIB_0"] = calculate_fib(df,fibVal, 0)    

        bantReferans = (((df["FIB_1"][limit-1] / df["FIB_0"][limit-1]) - 1) / 7)
        if (bantReferans >= bantMinimumOran):
            long_signal = df["EMA"][limit-1] > df["FIB_0_500"][limit-1]   
            short_signal = df["EMA"][limit-1] < df["FIB_0_500"][limit-1]

    if (start == True):
        limit = fibVal + 2
        candles = client.futures_klines(symbol=symbol, interval=interval, limit=limit) 
        df = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
                                            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                                            'taker_buy_quote_asset_volume', 'ignore']) 
        ## Clean data 
        df = df[['open_time', 'open', 'high', 'low', 'close', 'close_time']]       
        df['openTime'] = pd.to_datetime(df["open_time"], unit="ms") + timedelta(hours=3)
        df['closeTime'] = pd.to_datetime(df["close_time"], unit="ms") + timedelta(hours=3)
        df['open'] = df['open'].astype('float') 
        df['close'] = df['close'].astype('float') 
        df['high'] = df['high'].astype('float') 
        df['low'] = df['low'].astype('float') 
        df["EMA"] = ema_indicator(df[emaType],emaVal)
        df["FIB_0_500"] = calculate_fib(df,fibVal, 0.5)
        long_signal = df["EMA"][limit-1] > df["FIB_0_500"][limit-1]   
        short_signal = df["EMA"][limit-1] < df["FIB_0_500"][limit-1]

    ### Bandı ve Giriş Bilgilerini Ayarla
    if (position == "") and (long_signal or short_signal):

        bantReferans = (((df["FIB_1"][limit-1] / df["FIB_0"][limit-1]) - 1) / 7)

        if (bantReferans >= bantMinimumOran):
            start = True
            startTime =  df["openTime"][limit-1]

            shortStopFiyat = df["FIB_0_572"][limit-1]
            longKarFiyat = df["FIB_0_772"][limit-1]
            longGirisFiyat = df["FIB_0_572"][limit-1]
            referansOrtaFiyat = df["FIB_0_500"][limit-1]                 
            shortGirisFiyat = df["FIB_0_428"][limit-1]           
            shortKarFiyat = df["FIB_0_228"][limit-1]
            longStopFiyat = df["FIB_0_428"][limit-1]   

            debugMsg = ""
            debugMsg += str(toplamIslemSayisi + 1) + ". Signal\n"
            debugMsg += "\n"  
            debugMsg += "Trade Band\t: % " + str(round(bantReferans * 100, 3)) + "\n"
            debugMsg += "Pivot Price\t: " + str(round(referansOrtaFiyat,7)) + "\n"
            debugMsg += "\n"
            debugMsg += "LONG Order Price\t: " + str(round(longGirisFiyat, 7)) + "\n"
            debugMsg += "LONG TP\t: " + str(round(longKarFiyat, 7)) + "\n"
            debugMsg += "LONG SL\t: " + str(round(longStopFiyat,7)) + "\n"
            debugMsg += "\n"
            debugMsg += "SHORT Order Price\t: " + str(round(shortGirisFiyat,7)) + "\n"
            debugMsg += "SHORT TP\t: " + str(round(shortKarFiyat,7)) + "\n"
            debugMsg += "SHORT SL\t: " + str(round(shortStopFiyat,7)) + "\n"                                      
            debugMsg += "\n"  
            debugMsg += "Refrence Bands\n" 
            debugMsg += "\n"  
            debugMsg += "FIB 1.000 : " + str(df["FIB_1"][limit-1]) + "\n"
            debugMsg += "FIB 0.772 : " + str(df["FIB_0_772"][limit-1]) + "\n"
            debugMsg += "FIB 0.572 : " + str(df["FIB_0_572"][limit-1]) + "\n"
            debugMsg += "FIB 0.500 : " + str(df["FIB_0_500"][limit-1]) + "\n"
            debugMsg += "FIB 0.428 : " + str(df["FIB_0_428"][limit-1]) + "\n"
            debugMsg += "FIB 0.228 : " + str(df["FIB_0_228"][limit-1]) + "\n"
            debugMsg += "FIB 0.000 : " + str(df["FIB_0"][limit-1]) + "\n" 
            debugMsg += "\n"
            debugMsg += "EMA(" + str(emaVal) + ") -> " + str(round(df["EMA"][limit-1],3)) + "\n" 
            debugMsg += "\n" 
        else:
            start = False 

### LONG İŞLEM ###
    # LONG İşlem Aç
    if start and (df["high"][limit-1] >= longGirisFiyat and longGirisFiyat >= df["low"][limit-1]) and position == "" and long_signal:
        islemBitti = False
        toplamIslemSayisi = toplamIslemSayisi + 1
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee
        position = "Long"  
        islemFiyati = longGirisFiyat
        hedefFiyati = longKarFiyat
        stopFiyati = shortGirisFiyat
        karOrani = (longKarFiyat / longGirisFiyat) - 1 
        debugMsg += warn + " LONG Position Open\n" 
        debugMsg += "Order Time\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
        send_message_to_telegram(channelAtsiz, debugMsg)
        debugMsg = ""  

    # LONG İşlem Kar Al
    if start and (position == "Long") and (df["high"][limit-1] >= hedefFiyati and hedefFiyati >= df["low"][limit-1]):
        islemKar = cuzdan * karOrani * kaldirac
        islemKarOrani = (islemKar / cuzdan) * 100
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee

        debugMsg += str(toplamIslemSayisi) + " Signal\n"
        debugMsg += "\n"
        debugMsg += warn + " LONG Position Close Take Profit\n"
        debugMsg += "Order Time\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
        debugMsg += "Order Profit\t: % " + str(round(islemKarOrani,3)) + "\n"

        islemBitti = True
        start = False
        toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

    # LONG İşlem Stop Ol
    if start and (position == "Long") and (df["high"][limit-1] >= stopFiyati and stopFiyati >= df["low"][limit-1]) and short_signal:
        islemKar = cuzdan * (((stopFiyati - islemFiyati) / islemFiyati)) * kaldirac
        islemKarOrani = (islemKar / cuzdan) * 100
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee

        debugMsg += str(toplamIslemSayisi) + " Signal\n"
        debugMsg += "\n"
        debugMsg += warn + " LONG Position Close Stop Loss\n"
        debugMsg += "Order Time\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "Order SL\t: " + str(round(stopFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
        debugMsg += "Order Profit\t: % -" + str(round(islemKarOrani,3)) + "\n"

        islemBitti = True
        start = False
        toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

### SHORT İŞLEM ###
    # SHORT İşlem Aç
    if start and (df["low"][limit-1] <= shortGirisFiyat and shortGirisFiyat <= df["high"][limit-1]) and position == "" and short_signal:
        islemBitti = False
        toplamIslemSayisi = toplamIslemSayisi + 1
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee
        position = "Short"  
        islemFiyati = shortGirisFiyat
        hedefFiyati = shortKarFiyat
        stopFiyati = longGirisFiyat
        karOrani = (shortGirisFiyat / shortKarFiyat) - 1 

        debugMsg += warn + " SHORT Position Open\n" 
        debugMsg += "Order Time\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
        send_message_to_telegram(channelAtsiz, debugMsg)
        debugMsg = ""  

    # SHORT İşlem Kar Al
    if start and (position == "Short") and (df["low"][limit-1] <= hedefFiyati and hedefFiyati <= df["high"][limit-1]):
        islemKar = cuzdan * karOrani * kaldirac
        islemKarOrani = (islemKar / cuzdan) * 100
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee

        debugMsg += str(toplamIslemSayisi) + " Signal\n"
        debugMsg += "\n"
        debugMsg += warn + " SHORT Position Close Take Profit\n"
        debugMsg += "Order Time\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
        debugMsg += "Order Profit\t: % " + str(round(islemKarOrani,3)) + "\n"

        islemBitti = True
        start = False
        toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

    # SHORT İşlem Stop Ol
    if start and (position == "Short") and (df["low"][limit-1] <= stopFiyati and stopFiyati <= df["high"][limit-1]) and long_signal:
        islemKar = cuzdan * (((islemFiyati - stopFiyati) / islemFiyati)) * kaldirac
        islemKarOrani = (islemKar / cuzdan) * 100
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee

        debugMsg += str(toplamIslemSayisi) + " Signal\n"
        debugMsg += "\n"
        debugMsg += warn + " SHORT Position Close Stop Loss\n"
        debugMsg += "Order Time\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "Order SL\t: " + str(round(stopFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
        debugMsg += "Order Profit\t: % -" + str(round(islemKarOrani,3)) + "\n"

        islemBitti = True
        start = False
        toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

    if (cuzdan + 10) < toplamFee:
        debugMsg = warn + warn + warn + "\nCüzdanda Para Kalmadı\n" + warn + warn + warn
        send_message_to_telegram(channelAtsiz, debugMsg)
        debugMsg = "" 
        quit()   
     
    if islemBitti == True:     
        debugMsg += "\n"
        debugMsg += "Report\n"
        debugMsg += "\n"
        debugMsg += "Strategy : " + str(symbol) + " " + str(kaldirac) + " " + str(interval) + " FIB " + str(fibVal) + " EMA" + str(emaVal) + " " + str(emaType) + "\n"
        debugMsg += "Invest\t: " + str(round(baslangicPara,7)) + "\n"
        debugMsg += "ROI\t: " + str(round(toplamKar,7)) + "\n"
        debugMsg += "Total Fee\t: " + str(round(toplamFee,3)) + "\n"
        debugMsg += "Fund\t: " + str(round(cuzdan,7)) + "\n"
        debugMsg += "ROI\t: % " + str(round((cuzdan / baslangicPara) * 100),3) + "\n"
        debugMsg += "\n"
        debugMsg += "Total Orders\t: " + str(toplamIslemSayisi) + "\n"
        debugMsg += "TP Orders\t: " + str(toplamKarliIslemSayisi) + "\n"
        debugMsg += "SL Orders\t\t: " + str(toplamZararKesIslemSayisi) + "\n"
        debugMsg += "Gain Orders\t: % " + str(round((toplamKarliIslemSayisi / toplamIslemSayisi) * 100,1)) + "\n"
        debugMsg += "Lose Orders\t\t: % " + str(round((toplamZararKesIslemSayisi / toplamIslemSayisi) * 100,1)) + "\n"
        send_message_to_telegram(channelAtsiz, debugMsg)
        debugMsg = "" 
              
        islemBitti = False
        position = ""   
        start = False         
        islemKar = 0
        islemFee = 0
        islemFiyati = 0
        hedefFiyati = 0

        while datetime.now().minute % timeFrame != 0: 
            time.sleep(1)

    time.sleep(0.1) 