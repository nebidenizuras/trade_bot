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

import array as arr
from operator import index
import pandas as pd
import csv
import os

from data_manager import get_historical_data_symbol

from telegram_bot import warn

from datetime import timedelta
import time

tic = time.perf_counter()

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

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

# Parite Bilgileri
symbol = "GMTUSDT"
interval = "4h"

get_historical_data_symbol("Future", symbol, "1 January, 2022", "11 May, 2022", interval)

#csvName = "Historical_Data/" + symbol + "_" + interval + ".csv"
csvName = symbol + "_" + interval + ".csv"
logFileName = "LogFile_" +  symbol + "_" + interval + ".txt"

if os.path.isfile(logFileName):
    os.remove(logFileName)
logFileObject = open(logFileName, 'a', encoding="utf-8")

print("Data is preparing...\n")

attributes = ["openTime","open","high","low","close","volume","closeTime","2","3","4","5","6"]
df = pd.read_csv(csvName, names = attributes)

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

print("Strategy Back Test is starting...\n")

for i in range(df.shape[0]):
    if i > (fibVal * 2):        

        fib_1_000_price = round(df["FIB_1"][i],7)
        fib_0_772_price = round(df["FIB_0_772"][i],7)
        fib_0_572_price = round(df["FIB_0_572"][i],7)
        fib_0_500_price = round(df["FIB_0_500"][i],7)
        fib_0_428_price = round(df["FIB_0_428"][i],7)
        fib_0_228_price = round(df["FIB_0_228"][i],7)
        fib_0_000_price = round(df["FIB_0"][i],7)
        ema_price = round(df["EMA"][i],4)

        open_price = round(df['open'][i],7)
        high_price = round(df['high'][i],7)
        low_price = round(df['low'][i],7)
        close_price = round(df['close'][i],7)

        long_signal = ema_price > fib_0_500_price  
        short_signal = ema_price < fib_0_500_price

        ### Bandı ve Giriş Bilgilerini Ayarla
        if (position == "") and (long_signal or short_signal):

            bantReferans = (((df["FIB_1"][i] / df["FIB_0"][i]) - 1) / 7)

            if (bantReferans >= bantMinimumOran):
                start = True
                startTime =  df["openTime"][i]

                referansOrtaFiyat = fib_0_500_price

                longKarFiyat = fib_0_772_price
                longGirisFiyat = fib_0_572_price
                longStopFiyat = fib_0_428_price
                shortStopFiyat = fib_0_572_price              
                shortGirisFiyat = fib_0_428_price          
                shortKarFiyat = fib_0_228_price                

                debugMsg = ""
                debugMsg += "---------------------------------------\n" 
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
    
        # LONG İşleme Gir
        if (start == True) and (high_price >= longGirisFiyat >= low_price) and (position == "") and (long_signal == True):
            islemBitti = False
            position = "Long"  

            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee
            islemFiyati = longGirisFiyat
            hedefFiyati = longKarFiyat
            stopFiyati = shortGirisFiyat
            islemBuyuklugu = cuzdan * kaldirac
            karOrani = (longKarFiyat / longGirisFiyat) - 1 

            debugMsg += warn + " LONG Position Open\n"
            debugMsg += "Order Time\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "\n"

        # LONG Kar Al
        if (start == True) and (position == "Long") and (high_price >= hedefFiyati >= low_price):
            islemKar = cuzdan * karOrani * kaldirac
            toplamKar += islemKar
            islemKarOrani = (islemKar / cuzdan) * 100
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += str(toplamIslemSayisi) + " Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " LONG Position Close Take Profit\n"
            debugMsg += "Order Time\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t: % " + str(round(islemKarOrani,3)) + "\n"

            islemBitti = True
            start = False
            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            #print(debugMsg)    
            logFileObject.write(debugMsg)

        # LONG Stop Ol
        if (start == True) and (position == "Long") and (((high_price >= stopFiyati >= low_price) and (short_signal == True)) or (low_price <= fib_0_000_price)):
            islemKar = cuzdan * (((stopFiyati - islemFiyati) / islemFiyati)) * kaldirac
            islemKarOrani = (islemKar / cuzdan) * 100
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += str(toplamIslemSayisi) + " Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " LONG Position Close Stop Loss\n"
            debugMsg += "Order Time\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order SL\t: " + str(round(stopFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t: % " + str(round(islemKarOrani,3)) + "\n"               

            islemBitti = True
            start = False
            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
            #print(debugMsg)    
            logFileObject.write(debugMsg)

        # SHORT İşleme Gir
        if (start == True) and (low_price <= shortGirisFiyat <= high_price) and (position == "") and (short_signal == True):
            islemBitti = False
            position = "Short"  

            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee
            islemFiyati = shortGirisFiyat
            hedefFiyati = shortKarFiyat
            stopFiyati = longGirisFiyat
            islemBuyuklugu = cuzdan * kaldirac
            karOrani = (shortGirisFiyat / shortKarFiyat) - 1 

            debugMsg += warn + " SHORT Position Open\n"
            debugMsg += "Order Time\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "\n"            

        # SHORT Kar Al
        if (start == True) and (position == "Short") and (low_price <= hedefFiyati <= high_price):
            islemKar = cuzdan * karOrani * kaldirac
            toplamKar += islemKar
            islemKarOrani = (islemKar / cuzdan) * 100
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += str(toplamIslemSayisi) + " Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " SHORT Position Close Take Profit\n"
            debugMsg += "Order Time\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t: % " + str(round(islemKarOrani,3)) + "\n"     

            islemBitti = True
            start = False
            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            #print(debugMsg)    
            logFileObject.write(debugMsg)

        # SHORT Stop Ol
        if (start == True) and (position == "Short") and (((low_price <= stopFiyati <= high_price) and (long_signal == True)) or (high_price >= fib_1_000_price)):
            islemKar = cuzdan * (((islemFiyati - stopFiyati) / islemFiyati)) * kaldirac
            islemKarOrani = (islemKar / cuzdan) * 100
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee
            
            debugMsg += str(toplamIslemSayisi) + " Signal\n"
            debugMsg += "\n"
            debugMsg += warn + " SHORT Position Close Stop Loss\n"
            debugMsg += "Order Time\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order SL\t: " + str(round(stopFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t: % " + str(round(islemKarOrani,3)) + "\n"          
            
            islemBitti = True
            start = False        
            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1   
            #print(debugMsg)    
            logFileObject.write(debugMsg)

        if (islemBitti == True):
            islemBitti = False
            position = ""   
            start = False 
            islemKar = 0
            islemFee = 0
            islemFiyati = 0
            hedefFiyati = 0  

        if cuzdan < 10:
            print("\nCüzdanda Para Kalmadı\n")
            quit()   
     
debugMsg = ""
debugMsg += "\n"
debugMsg += "****************************************\n"
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
debugMsg += "\n"
debugMsg += "****************************************\n"


print(debugMsg)
logFileObject.write(debugMsg)
logFileObject.close()

toc = time.perf_counter()
print(f"Backtest is finished in {toc - tic:0.8f} seconds")