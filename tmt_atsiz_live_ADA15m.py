'''
- Bu stratejide işleme giriş bandı Fibonacci kanalına göre belirlenmektedir.
- EMA değeri FIB 0.5 üzerinde ise, long işleme değmişsem long girerim (FIB 0.572)
  FIB 0.772 de kar alırım
- EMA değeri FIB 0.5 altında ise, short işleme değmişsem short girerim (FIB 0.428)
  FIB 0.228 de kar alırım
- Stop noktaları diğer yön işlemin açıldığı yer ve eması 0.5'e uyumlu ise
- EMA3 ile sinyal yapılır.
'''

from Indicators.fibonacci_retracement import calculate_fib
from ta.trend import ema_indicator

from binance.client import Client  
from user_api_key import key_id, secret_key_id

import pandas as pd

from data_manager import get_current_time, get_current_price_of_symbol

from telegram_bot import warn, send_message_to_telegram, channel_03

from datetime import datetime
from datetime import timedelta
from time import sleep

client = Client(key_id, secret_key_id)

#ATTRIBUTES
kaldirac = 1
feeOrani = 0.0004 # percent
bantMinimumOran = 0.0020

baslangicPara = 100
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
islemBuyuklugu = 0
karOrani = 0

islemFiyati = 0
hedefFiyati = 0
stopFiyati = 0

islemFee = 0
toplamFee = 0

islemKar = 0
toplamKar = 0

startTime = 0
stopTime = 0

position = ""
start = False
islemBitti = False

# Sinyal Değerleri
fibVal = 5
emaVal = 3
emaType = "close" # "open" or "close"

fib_1_000_price = 0.0
fib_0_772_price = 0.0
fib_0_572_price = 0.0
fib_0_500_price = 0.0
fib_0_428_price = 0.0
fib_0_228_price = 0.0
fib_0_000_price = 0.0
ema_price = 0.0
open_price = 0.0
high_price = 0.0
low_price = 0.0
close_price = 0.0
current_price = 0.0
previous_price = 0.0

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

# Parite Bilgileri
timeFrame = 15
symbol = "ADAUSDT"
interval = "15m"
limit = emaVal * 5

current_price = get_current_price_of_symbol(symbol, 'Future')
previous_price = current_price

while(True):
    try:       
        if (position == ""):
            start = False
            long_signal = False
            short_signal = False
            limit = emaVal * 5
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

            fib_1_000_price = round(df["FIB_1"][limit-1],7)
            fib_0_772_price = round(df["FIB_0_772"][limit-1],7)
            fib_0_572_price = round(df["FIB_0_572"][limit-1],7)
            fib_0_500_price = round(df["FIB_0_500"][limit-1],7)
            fib_0_428_price = round(df["FIB_0_428"][limit-1],7)
            fib_0_228_price = round(df["FIB_0_228"][limit-1],7)
            fib_0_000_price = round(df["FIB_0"][limit-1],7)
            ema_price = round(df["EMA"][limit-1],4)

            open_price = round(df['open'][limit-1],7)
            high_price = round(df['high'][limit-1],7)
            low_price = round(df['low'][limit-1],7)
            close_price = round(df['close'][limit-1],7)
            current_price = get_current_price_of_symbol(symbol, 'Future')

            bantReferans = (((fib_1_000_price / fib_0_000_price ) - 1) / 7)
            if (bantReferans >= bantMinimumOran):
                long_signal = ema_price > fib_0_500_price  
                short_signal = ema_price < fib_0_500_price
        elif (position != ""):
            limit = emaVal * 5
            long_signal = False
            short_signal = False      

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

            open_price = round(df['open'][limit-1],7)
            high_price = round(df['high'][limit-1],7)
            low_price = round(df['low'][limit-1],7)
            close_price = round(df['close'][limit-1],7)
            current_price = get_current_price_of_symbol(symbol, 'Future')
           
            ema_price = round(df["EMA"][limit-1],4)

            long_signal = ema_price > fib_0_500_price  
            short_signal = ema_price < fib_0_500_price

        ### Bandı ve Giriş Bilgilerini Ayarla
        if (position == "") and ((long_signal == True) or (short_signal == True)):

            bantReferans = (((fib_1_000_price / fib_0_000_price) - 1) / 7)

            if (bantReferans >= bantMinimumOran):
                start = True

                referansOrtaFiyat = fib_0_500_price

                longKarFiyat = fib_0_772_price
                longGirisFiyat = fib_0_572_price
                longStopFiyat = fib_0_000_price #fib_0_428_price

                shortStopFiyat = fib_1_000_price #fib_0_572_price              
                shortGirisFiyat = fib_0_428_price          
                shortKarFiyat = fib_0_228_price    

                debugMsg = ""
                debugMsg += str(toplamIslemSayisi + 1) + ". Signal\n"
                debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
                debugMsg += "\n"  
                debugMsg += "Candle Time : " + str( df['openTime'][limit-1]) + "\n"  
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
                debugMsg += "FIB 1.000 : " + str(fib_1_000_price) + "\n"
                debugMsg += "FIB 0.772 : " + str(fib_0_772_price) + "\n"
                debugMsg += "FIB 0.572 : " + str(fib_0_572_price) + "\n"
                debugMsg += "FIB 0.500 : " + str(fib_0_500_price) + "\n"
                debugMsg += "FIB 0.428 : " + str(fib_0_428_price) + "\n"
                debugMsg += "FIB 0.228 : " + str(fib_0_228_price) + "\n"
                debugMsg += "FIB 0.000 : " + str(fib_0_000_price) + "\n"
                debugMsg += "\n"
                debugMsg += "EMA(" + str(emaVal) + ") -> " + str(round(ema_price,3)) + "\n"
                debugMsg += "\n"
            else:
                start = False

    ### LONG İŞLEM ###
        # LONG İşlem Aç
        if (start == True) and (position == "") and (long_signal == True) and ((current_price >= longGirisFiyat >= previous_price) or (current_price <= longGirisFiyat <= previous_price)):
            
            islemBitti = False
            position = "Long"  

            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee            
            islemFiyati = current_price #islemFiyati = longGirisFiyat 
            hedefFiyati = longKarFiyat
            stopFiyati = shortGirisFiyat
            islemBuyuklugu = cuzdan * kaldirac            

            debugMsg += warn + " LONG Position Open\n"
            debugMsg += "Order Time\t: " + str(get_current_time()) + "\n"
            debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
            send_message_to_telegram(channel_03, debugMsg)
            debugMsg = ""  

        # LONG İşlem Kar Al
        if (start == True) and (position == "Long") and (current_price >= hedefFiyati):
            hedefFiyati = current_price

            islemKar = cuzdan * (((hedefFiyati - islemFiyati) / islemFiyati)) * kaldirac
            islemKarOrani = (islemKar / cuzdan) * 100
            toplamKar += islemKar            
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += str(toplamIslemSayisi) + " Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " LONG Position Close Take Profit\n"
            debugMsg += "Order Time\t: " + str(get_current_time()) + "\n"
            debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t: % " + str(round(islemKarOrani,3)) + "\n"

            islemBitti = True
            start = False
            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

        # LONG İşlem Stop Ol
        if (start == True) and (position == "Long") and (((current_price <= stopFiyati) and (short_signal == True)) or (current_price <= fib_0_000_price)):
            
            stopFiyati = current_price

            islemKar = cuzdan * (((stopFiyati - islemFiyati) / islemFiyati)) * kaldirac
            islemKarOrani = (islemKar / cuzdan) * 100
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += str(toplamIslemSayisi) + " Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " LONG Position Close Stop Loss\n"
            debugMsg += "Order Time\t: " + str(get_current_time()) + "\n"
            debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order SL\t: " + str(round(stopFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t: % " + str(round(islemKarOrani,3)) + "\n"

            islemBitti = True
            start = False
            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

    ### SHORT İŞLEM ###
        # SHORT İşlem Aç
        if (start == True) and (position == "") and (short_signal == True) and ((previous_price >= shortGirisFiyat >= current_price) or (previous_price <= shortGirisFiyat <= current_price)):
            
            islemBitti = False
            position = "Short"  

            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee
            islemFiyati = current_price #islemFiyati = shortGirisFiyat
            hedefFiyati = shortKarFiyat
            stopFiyati = longGirisFiyat
            islemBuyuklugu = cuzdan * kaldirac
            karOrani = (shortGirisFiyat / shortKarFiyat) - 1

            debugMsg += warn + " SHORT Position Open\n"
            debugMsg += "Order Time\t: " + str(get_current_time()) + "\n"
            debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
            send_message_to_telegram(channel_03, debugMsg)
            debugMsg = ""  

        # SHORT İşlem Kar Al
        if (start == True) and (position == "Short") and (current_price <= hedefFiyati): 
            hedefFiyati = current_price

            islemKar = cuzdan * (((islemFiyati - hedefFiyati) / islemFiyati)) * kaldirac
            islemKarOrani = (islemKar / cuzdan) * 100
            toplamKar += islemKar            
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += str(toplamIslemSayisi) + " Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " SHORT Position Close Take Profit\n"
            debugMsg += "Order Time\t: " + str(get_current_time()) + "\n"
            debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t: % " + str(round(islemKarOrani,3)) + "\n"

            islemBitti = True
            start = False
            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

        # SHORT İşlem Stop Ol
        if (start == True) and (position == "Short") and (((current_price >= stopFiyati) and (long_signal == True)) or (current_price >= fib_1_000_price)):
            
            stopFiyati = current_price

            islemKar = cuzdan * (((islemFiyati - stopFiyati) / islemFiyati)) * kaldirac
            islemKarOrani = (islemKar / cuzdan) * 100
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += str(toplamIslemSayisi) + " Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " SHORT Position Close Stop Loss\n"
            debugMsg += "Order Time\t: " + str(get_current_time()) + "\n"
            debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order SL\t: " + str(round(stopFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t: % " + str(round(islemKarOrani,3)) + "\n"

            islemBitti = True
            start = False
            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
    
        if islemBitti == True:    
            debugMsg += "\n"
            debugMsg += "Report\n"
            debugMsg += "\n"
            debugMsg += "Strategy\t: " + str(symbol) + " (" + str(kaldirac) + "x) (" + str(interval) + ") (FIB " + str(fibVal) + ") (EMA " + str(emaVal) + " " + str(emaType) + ")\n"
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
            send_message_to_telegram(channel_03, debugMsg)
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
            send_message_to_telegram(channel_03, debugMsg)
            debugMsg = ""
            quit()  

        previous_price = current_price
        sleep(0.25) 
    except Exception as e:
        debugMsg = warn + " Error : \n" + str(e) + "\n\n"
        debugMsg += warn + "\nSistem Tekrar Bağlanmayı Deniyor...\n" + warn
        send_message_to_telegram(channel_03, debugMsg)
        debugMsg = ""
        sleep(10)
        client = Client(key_id, secret_key_id)
        continue
        #quit()