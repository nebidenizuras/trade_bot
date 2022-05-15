'''
- Bu stratejide işleme giriş bandı Fibonacci kanalına göre belirlenmektedir.
- EMA değeri FIB 0.5 üzerinde ise, long işleme değmişsem long girerim (FIB 0.572)
  FIB 0.772 de kar alırım. FIB 0.000 da stop olurum.
- EMA değeri FIB 0.5 altında ise, short işleme değmişsem short girerim (FIB 0.428)
  FIB 0.228 de kar alırım. FIB 1.000 da stop olurum.
- FIB5 ve EMA3 ile sinyal yapılır.
- Hedge işlem alırım. İki işlemde bittiyse yeni teknik hesaplama yaparım.
'''

from Indicators.fibonacci_retracement import calculate_fib
from ta.trend import ema_indicator

from binance.client import Client  
from user_api_key import key_id, secret_key_id

import pandas as pd

from data_manager import get_current_time, get_current_price_of_symbol, get_price_precision

from telegram_bot import warn, send_message_to_telegram, channel_02

from datetime import datetime
from datetime import timedelta
from time import sleep

client = Client(key_id, secret_key_id)

# Sistem Bilgileri
leverage = 1
feeOrani = 0.0004 # percent
bantMinimumOran = 0.0020

baslangicPara = 100
cuzdan = baslangicPara
longWallet = cuzdan / 2
shortWallet = cuzdan / 2

islemBuyuklugu = 0

bantReferans = 0
cikisOrani = 3 * bantReferans
girisOrani = bantReferans / 2
referansOrtaFiyat = 0

longGirisFiyat = 0
longKarFiyat = 0
longStopFiyat = 0

shortGirisFiyat = 0
shortKarFiyat = 0
shortStopFiyat = 0

islemFee = 0
toplamFee = 0

islemKar = 0
toplamKar = 0

IsLongPositionExist = False
IsShortPositionExist = False
start = False
islemBitti = False

LongOrderNo = 0
ShortOrderNo = 0

PriceTickSize = 7

# Sinyal Değerleri
fibVal = 5
emaVal = 3
emaType = "close" # "open" or "close"

# Fiyat Değerleri
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
symbol = "APEUSDT"
interval = "15m"
limit = emaVal * 5

PriceTickSize = get_price_precision(symbol, 'Future')
if PriceTickSize < 3:
    PriceTickSize = 3
current_price = get_current_price_of_symbol(symbol, 'Future')
previous_price = current_price

while(True):
    try:       
        if (IsLongPositionExist == False) and (IsShortPositionExist == False):
            longWallet = cuzdan / 2
            shortWallet = cuzdan / 2
            start = False
            IsLongPositionExist = False
            IsShortPositionExist = False
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

            fib_1_000_price = round(df["FIB_1"][limit-1], PriceTickSize)
            fib_0_772_price = round(df["FIB_0_772"][limit-1], PriceTickSize)
            fib_0_572_price = round(df["FIB_0_572"][limit-1], PriceTickSize)
            fib_0_500_price = round(df["FIB_0_500"][limit-1], PriceTickSize)
            fib_0_428_price = round(df["FIB_0_428"][limit-1], PriceTickSize)
            fib_0_228_price = round(df["FIB_0_228"][limit-1], PriceTickSize)
            fib_0_000_price = round(df["FIB_0"][limit-1], PriceTickSize)
            ema_price = round(df["EMA"][limit-1], PriceTickSize)

            open_price = round(df['open'][limit-1], PriceTickSize)
            high_price = round(df['high'][limit-1], PriceTickSize)
            low_price = round(df['low'][limit-1], PriceTickSize)
            close_price = round(df['close'][limit-1], PriceTickSize)
            current_price = get_current_price_of_symbol(symbol, 'Future')

            bantReferans = (((fib_1_000_price / fib_0_000_price ) - 1) / 7)
            if (bantReferans >= bantMinimumOran):
                long_signal = ema_price > fib_0_500_price  
                short_signal = ema_price < fib_0_500_price
        else:
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

            open_price = round(df['open'][limit-1], PriceTickSize)
            high_price = round(df['high'][limit-1], PriceTickSize)
            low_price = round(df['low'][limit-1], PriceTickSize)
            close_price = round(df['close'][limit-1], PriceTickSize)
            current_price = get_current_price_of_symbol(symbol, 'Future')
           
            ema_price = round(df["EMA"][limit-1], PriceTickSize)

            long_signal = ema_price > fib_0_500_price  
            short_signal = ema_price < fib_0_500_price

        ### Bandı ve Giriş Bilgilerini Ayarla
        if (IsLongPositionExist == False) and (IsShortPositionExist == False) and ((long_signal == True) or (short_signal == True)):

            bantReferans = (((fib_1_000_price / fib_0_000_price) - 1) / 7)

            if (bantReferans >= bantMinimumOran):
                start = True

                referansOrtaFiyat = fib_0_500_price

                longGirisFiyat = fib_0_572_price
                longKarFiyat = fib_0_772_price                
                longStopFiyat = fib_0_000_price

                shortGirisFiyat = fib_0_428_price   
                shortKarFiyat = fib_0_228_price  
                shortStopFiyat = fib_1_000_price      

                debugMsg = ""
                debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
                debugMsg += "\n"  
                debugMsg += "Candle Time : " + str( df['openTime'][limit-1]) + "\n"  
                debugMsg += "\n"  
                debugMsg += "Trade Band\t: % " + str(round(bantReferans * 100, 3)) + "\n"
                debugMsg += "Pivot Price\t: " + str(round(referansOrtaFiyat, PriceTickSize)) + "\n"
                debugMsg += "\n"
                debugMsg += "LONG Order Price\t: " + str(round(longGirisFiyat, PriceTickSize)) + "\n"
                debugMsg += "LONG TP\t: " + str(round(longKarFiyat, PriceTickSize)) + "\n"
                debugMsg += "LONG SL\t: " + str(round(longStopFiyat, PriceTickSize)) + "\n"
                debugMsg += "\n"
                debugMsg += "SHORT Order Price\t: " + str(round(shortGirisFiyat, PriceTickSize)) + "\n"
                debugMsg += "SHORT TP\t: " + str(round(shortKarFiyat, PriceTickSize)) + "\n"
                debugMsg += "SHORT SL\t: " + str(round(shortStopFiyat, PriceTickSize)) + "\n"                                      
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
                debugMsg += "EMA(" + str(emaVal) + ") -> " + str(round(ema_price, PriceTickSize)) + "\n"
                debugMsg += "\n"
            else:
                start = False

    
        ### LONG İŞLEM AÇ ###
        if (start == True) and (IsLongPositionExist == False) and (long_signal == True) and ((current_price >= longGirisFiyat >= previous_price) or (current_price <= longGirisFiyat <= previous_price)):
            
            islemBitti = False
            IsLongPositionExist = True

            toplamIslemSayisi = toplamIslemSayisi + 1
            islemBuyuklugu = longWallet * leverage           
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee           
            LongOrderNo = toplamIslemSayisi

            debugMsg += str(LongOrderNo) + ". Signal\n"
            debugMsg += warn + " LONG Position Open\n"
            debugMsg += "Order Time\t: " + str(get_current_time()) + "\n"
            debugMsg += "Order Price\t: " + str(round(longGirisFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order TP\t: " + str(round(longKarFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order SL\t: " + str(round(longStopFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(islemBuyuklugu, PriceTickSize)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee, PriceTickSize)) + "\n"
            send_message_to_telegram(channel_02, debugMsg)
            debugMsg = ""  

        ### SHORT İŞLEM AÇ ###
        if (start == True) and (IsShortPositionExist == False) and (short_signal == True) and ((previous_price >= shortGirisFiyat >= current_price) or (previous_price <= shortGirisFiyat <= current_price)):
            
            islemBitti = False
            IsShortPositionExist = True

            toplamIslemSayisi = toplamIslemSayisi + 1
            islemBuyuklugu = shortWallet * leverage
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee
            ShortOrderNo = toplamIslemSayisi

            debugMsg += str(ShortOrderNo) + ". Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " SHORT Position Open\n"
            debugMsg += "Order Time\t: " + str(get_current_time()) + "\n"
            debugMsg += "Order Price\t: " + str(round(shortGirisFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order TP\t: " + str(round(shortKarFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order SL\t: " + str(round(shortStopFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(islemBuyuklugu, PriceTickSize)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee, PriceTickSize)) + "\n"
            send_message_to_telegram(channel_02, debugMsg)
            debugMsg = ""  

        ### LONG İŞLEM KAR AL ###
        if (start == True) and (IsLongPositionExist == True) and (current_price >= longKarFiyat):

            islemKar = longWallet * (((longKarFiyat - longGirisFiyat) / longGirisFiyat)) * leverage
            islemKarOrani = (islemKar / longWallet) * 100
            toplamKar += islemKar            
            longWallet += islemKar
            cuzdan += islemKar
            islemBuyuklugu = longWallet * leverage
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee            

            debugMsg += str(LongOrderNo) + " Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " LONG Position Close Take Profit\n"
            debugMsg += "Order Time\t: " + str(get_current_time()) + "\n"
            debugMsg += "Order Price\t: " + str(round(longGirisFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order TP\t: " + str(round(longKarFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(islemBuyuklugu, PriceTickSize)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee, PriceTickSize)) + "\n"
            debugMsg += "Order Profit\t: % " + str(round(islemKarOrani, 3)) + "\n"
            send_message_to_telegram(channel_02, debugMsg)
            debugMsg = ""

            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            IsLongPositionExist = False

            if (IsShortPositionExist == False):
                islemBitti = True            
                start = False            

        ### SHORT İŞLEM KAR AL ###
        if (start == True) and (IsShortPositionExist == True) and (current_price <= shortKarFiyat): 

            islemKar = shortWallet * (((shortGirisFiyat - shortKarFiyat) / shortGirisFiyat)) * leverage
            islemKarOrani = (islemKar / shortWallet) * 100
            toplamKar += islemKar            
            shortWallet += islemKar
            cuzdan += islemKar
            islemBuyuklugu = shortWallet * leverage
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee

            debugMsg += str(ShortOrderNo) + " Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " SHORT Position Close Take Profit\n"
            debugMsg += "Order Time\t: " + str(get_current_time()) + "\n"
            debugMsg += "Order Price\t: " + str(round(shortGirisFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order TP\t: " + str(round(shortKarFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(islemBuyuklugu, PriceTickSize)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee, PriceTickSize)) + "\n"
            debugMsg += "Order Profit\t: % " + str(round(islemKarOrani, 3)) + "\n"
            send_message_to_telegram(channel_02, debugMsg)
            debugMsg = ""

            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            IsShortPositionExist = False

            if (IsLongPositionExist == False):
                islemBitti = True            
                start = False  

        ### LONG İŞLEM STOP OL ###
        if (start == True) and (IsLongPositionExist == True) and (current_price <= longStopFiyat):
            
            islemKar = longWallet * (((longStopFiyat - longGirisFiyat) / longGirisFiyat)) * leverage
            islemKarOrani = (islemKar / longWallet) * 100
            toplamKar += islemKar
            longWallet += islemKar
            cuzdan += islemKar
            islemBuyuklugu = longWallet * leverage
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee

            debugMsg += str(LongOrderNo) + " Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " LONG Position Close Stop Loss\n"
            debugMsg += "Order Time\t: " + str(get_current_time()) + "\n"
            debugMsg += "Order Price\t: " + str(round(longGirisFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order SL\t: " + str(round(longStopFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(islemBuyuklugu, PriceTickSize)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee, PriceTickSize)) + "\n"
            debugMsg += "Order Profit\t: % " + str(round(islemKarOrani, 3)) + "\n"
            send_message_to_telegram(channel_02, debugMsg)
            debugMsg = ""

            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
            IsLongPositionExist = False

            if (IsShortPositionExist == False):
                islemBitti = True            
                start = False          

        ### SHORT İŞLEM STOP OL ###
        if (start == True) and (IsShortPositionExist == True) and (current_price >= shortStopFiyat):

            islemKar = shortWallet * (((shortGirisFiyat - shortStopFiyat) / shortGirisFiyat)) * leverage
            islemKarOrani = (islemKar / shortWallet) * 100
            toplamKar += islemKar
            shortWallet += islemKar
            cuzdan += islemKar
            islemBuyuklugu = shortWallet * leverage
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee

            debugMsg += str(ShortOrderNo) + " Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " SHORT Position Close Stop Loss\n"
            debugMsg += "Order Time\t: " + str(get_current_time()) + "\n"
            debugMsg += "Order Price\t: " + str(round(shortGirisFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order SL\t: " + str(round(shortStopFiyat, PriceTickSize)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(islemBuyuklugu, PriceTickSize)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee, PriceTickSize)) + "\n"
            debugMsg += "Order Profit\t: % " + str(round(islemKarOrani, 3)) + "\n"
            send_message_to_telegram(channel_02, debugMsg)
            debugMsg = ""

            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
            IsShortPositionExist = False

            if (IsLongPositionExist == False):
                islemBitti = True            
                start = False    

        if islemBitti == True:    
            sleep(2)
            debugMsg += "\n"
            debugMsg += "Report\n"
            debugMsg += "\n"
            debugMsg += "Strategy\t: " + str(symbol) + " (" + str(leverage) + "x) (" + str(interval) + ") (FIB " + str(fibVal) + ") (EMA " + str(emaVal) + " " + str(emaType) + ")\n"
            debugMsg += "Invest\t\t: " + str(round(baslangicPara, PriceTickSize)) + "\n"
            debugMsg += "ROI\t\t: " + str(round(toplamKar, PriceTickSize)) + "\n"
            debugMsg += "Total Fee\t: " + str(round(toplamFee, 3)) + "\n"
            debugMsg += "Fund\t\t: " + str(round(cuzdan, PriceTickSize)) + "\n"
            debugMsg += "ROI\t\t: % " + str(round((toplamKar / baslangicPara) * 100, 3)) + "\n"
            debugMsg += "Net ROI\t\t: % " + str(round((((cuzdan-toplamFee) - baslangicPara) / baslangicPara) * 100, 3)) + "\n"
            debugMsg += "\n"
            debugMsg += "Total Orders\t: " + str(toplamIslemSayisi) + "\n"
            debugMsg += "TP Orders\t: " + str(toplamKarliIslemSayisi) + "\n"
            debugMsg += "SL Orders\t: " + str(toplamZararKesIslemSayisi) + "\n"
            debugMsg += "Gain Orders\t: % " + str(round((toplamKarliIslemSayisi / toplamIslemSayisi) * 100, 1)) + "\n"
            debugMsg += "Lose Orders\t: % " + str(round((toplamZararKesIslemSayisi / toplamIslemSayisi) * 100, 1)) + "\n"
            send_message_to_telegram(channel_02, debugMsg)
            debugMsg = ""
                
            islemBitti = False
            start = False        
            islemKar = 0
            islemFee = 0
            islemFiyati = 0
            hedefFiyati = 0

        if (cuzdan + 10) < toplamFee:
            debugMsg = warn + warn + warn + "\nCüzdanda Para Kalmadı\n" + warn + warn + warn
            send_message_to_telegram(channel_02, debugMsg)
            debugMsg = ""
            quit()  

        previous_price = current_price
        sleep(0.1) 
    except Exception as e:
        debugMsg = warn + " Error : \n" + str(e) + "\n\n"
        debugMsg += warn + "\nSistem Tekrar Bağlanmayı Deniyor...\n" + warn
        send_message_to_telegram(channel_02, debugMsg)
        debugMsg = ""
        sleep(10)
        client = Client(key_id, secret_key_id)
        continue
        #quit()