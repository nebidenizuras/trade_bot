'''
- EMA 3 Close > EMA 8 close ise long gir, short'a dönerse kapat
- EMA 3 Close < EMA 8 close ise short gir, long'a dönerse kapat
'''

from operator import index
from numpy import short
import pandas_ta as tb
import pandas as pd
import csv
import os
from Indicators.fibonacci_retracement import calculate_fib
import array as arr
from datetime import timedelta
from data_manager import get_historical_data_symbol
import time

tic = time.perf_counter()

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

debugMsg = ""
position = ""
start = False
startTime = 0
stopTime = 0

# Sinyal Değerleri
emaBuy = 3
emaBuyType = "close"
emaSell = 8 
emaSellType = "close"

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

symbol = "BTCDOMUSDT"
interval = "1m"

#csvName = "Historical_Data/" + coin + "_" + timeFrame + ".csv"
csvName = symbol + "_" + interval + ".csv"
logFileName = "LogFile_" +  symbol + "_" + interval + ".txt"

if os.path.isfile(logFileName):
    os.remove(logFileName)
logFileObject = open(logFileName, 'a', encoding="utf-8")

print("Data is preparing......")

attributes = ["openTime","open","high","low","close","volume","closeTime","2","3","4","5","6"]
df = pd.read_csv(csvName, names = attributes)

df['open'] = df['open'].astype('float')
df['close'] = df['close'].astype('float')
df['high'] = df['high'].astype('float')
df['low'] = df['low'].astype('float')
df["openTime"] = pd.to_datetime(df["openTime"],unit= "ms") + timedelta(hours=3)
df["closeTime"] = pd.to_datetime(df["closeTime"],unit= "ms") + timedelta(hours=3)
df["EMABUY"] = tb.ema(df[emaBuyType],emaBuy)
df["EMASELL"] = tb.ema(df[emaSellType],emaSell)

print("Strategy Back Test is starting......")

for i in range(df.shape[0]):
    if i > (emaSell * 3): 
        ema_sell_price = df["EMASELL"][i]
        ema_buy_price = df["EMABUY"][i]

        long_signal = (ema_buy_price > ema_sell_price)
        short_signal = (ema_buy_price < ema_sell_price)

        ### Giriş Bilgilerini Ayarla
        if (start == False) and (position == "") and ((long_signal == True) or (short_signal == True)): 
            start = True
            startTime =  df["openTime"][i]
            debugMsg += "---------------------------------------\n" 
            debugMsg += "Sinyal Oluştu ->\n" + str(symbol) + " " + str(interval) + "\n"
            debugMsg += str(toplamIslemSayisi + 1) + ". İşlem Sinyali : "
            if long_signal:
                debugMsg += "LONG\n"
            elif short_signal:
                debugMsg += "SHORT\n"
            debugMsg += "\n"
            debugMsg += "EMA(" + str(emaBuy) + ")  -> " + str(df["EMABUY"][i]) + "\n" 
            debugMsg += "EMA(" + str(emaSell) + ") -> " + str(df["EMASELL"][i]) + "\n"
            debugMsg += "\n"  

    # LONG İŞLEM
        # Long İşlem Aç
        if (start == True) and (position == "") and (long_signal == True):
            position = "Long"    

            toplamIslemSayisi = toplamIslemSayisi + 1                                    
            islemFiyati = df["open"][i] 
            islemBuyuklugu = cuzdan * kaldirac  
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee       

            debugMsg += "İşlem Giriş Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Giriş Fiyatı\t: " + str(islemFiyati) + "\n"
            debugMsg += "İşlem Büyüklüğü\t: " + str(islemBuyuklugu) + "\n"
            debugMsg += "İşlem Giriş Fee\t: " + str(islemFee) + "\n"
            debugMsg += "\n"  

        # Long İşlem Kapat
        if (start == True) and (position == "Long") and (short_signal == True):
            hedefFiyati = ema_sell_price
            karOrani = ((hedefFiyati - islemFiyati) / islemFiyati)
            islemKar = cuzdan * karOrani * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Çıkış Fiyatı\t: " + str(hedefFiyati) + "\n"
            debugMsg += "İşlem Çıkış Fee\t: " + str(islemFee) + "\n" 
            debugMsg += "İşlem Kar\t\t: " + str(islemKar) + "\n"         
            debugMsg += "\n"          

            if(islemKar > 0):
                toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            else:
                toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

            position = ""   
            start = False 
            islemKar = 0
            islemFee = 0
            islemFiyati = 0
            hedefFiyati = 0

    # SHORT İŞLEM
        # Short İşlem Aç
        if (start == True) and (position == "") and (short_signal == True):
            position = "Short"    

            toplamIslemSayisi = toplamIslemSayisi + 1                                    
            islemFiyati = df["open"][i] 
            islemBuyuklugu = cuzdan * kaldirac  
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee              
                      
            debugMsg += "İşlem Giriş Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Giriş Fiyatı\t: " + str(islemFiyati) + "\n"
            debugMsg += "İşlem Büyüklüğü\t: " + str(islemBuyuklugu) + "\n"
            debugMsg += "İşlem Giriş Fee\t: " + str(islemFee) + "\n"
            debugMsg += "\n"  

        # Short İşlem Kapat
        if (start == True) and (position == "Short") and (long_signal == True):
            hedefFiyati = ema_buy_price
            karOrani = ((islemFiyati - hedefFiyati) / islemFiyati)
            islemKar = cuzdan * karOrani * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Çıkış Fiyatı\t: " + str(hedefFiyati) + "\n"
            debugMsg += "İşlem Çıkış Fee\t: " + str(islemFee) + "\n" 
            debugMsg += "İşlem Kar\t\t: " + str(islemKar) + "\n"         
            debugMsg += "\n"          

            if(islemKar > 0):
                toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            else:
                toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

            position = ""   
            start = False 
            islemKar = 0
            islemFee = 0
            islemFiyati = 0
            hedefFiyati = 0  
         
        #print(debugMsg)    
        logFileObject.write(debugMsg)
        debugMsg = ""

        if (cuzdan + 10) < toplamFee:
            print("PARA BITTI")
            quit()   

debugMsg = "****************************************\n"
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
debugMsg += "****************************************\n"

print(debugMsg)
logFileObject.write(debugMsg)
logFileObject.close()

toc = time.perf_counter()
print(f"Backtest is finished in {toc - tic:0.8f} seconds")