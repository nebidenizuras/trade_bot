'''
- EMA 3 Close > EMA 8 close ise long gir, short'a dönerse kapat
- EMA 3 Close < EMA 8 close ise short gir, long'a dönerse kapat
'''

import pandas_ta as tb
import pandas as pd

import os

from datetime import timedelta
import time

from telegram_bot import warn

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

symbol = "APEUSDT"
interval = "15m"

#csvName = "Historical_Data/" + coin + "_" + timeFrame + ".csv"
csvName = symbol + "_" + interval + ".csv"
logFileName = "LogFile_" +  symbol + "_" + interval + ".txt"

if os.path.isfile(logFileName):
    os.remove(logFileName)
logFileObject = open(logFileName, 'a', encoding="utf-8")

print("Data is preparing......\n")

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

print("Strategy Back Test is starting......\n")

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
            debugMsg = "---------------------------------------\n" 
            debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
            debugMsg += warn +  " " + str(toplamIslemSayisi + 1) + ". Signal "
            if long_signal:
                debugMsg += "LONG\n"
            elif short_signal:
                debugMsg += "SHORT\n"
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

            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(islemBuyuklugu,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,4)) + "\n"
            debugMsg += "\n" 
            debugMsg += "\n"
            debugMsg += "Reference Bands\n" 
            debugMsg += "EMA(" + str(emaBuy) + ") -> " + str(round(ema_buy_price,4)) + "\n" 
            debugMsg += "EMA(" + str(emaSell) + ") -> " + str(round(ema_sell_price,4)) + "\n"
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

            debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
            if (islemKar > 0):
                toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
                debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal LONG Close Take Profit\n"
            else:
                toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
                debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal LONG Close Stop Loss\n"            
            debugMsg += "\n"
            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            if (islemKar > 0):
                debugMsg += "LONG Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
            else:
                debugMsg += "LONG Order SL\t\t: " + str(round(hedefFiyati,7)) + "\n"            
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t\t: % " + str(round(karOrani * 100,3)) + "\n"

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
                      
            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(islemBuyuklugu,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,4)) + "\n"
            debugMsg += "\n" 
            debugMsg += "\n"
            debugMsg += "Reference Bands\n" 
            debugMsg += "EMA(" + str(emaBuy) + ") -> " + str(round(ema_buy_price,4)) + "\n" 
            debugMsg += "EMA(" + str(emaSell) + ") -> " + str(round(ema_sell_price,4)) + "\n"
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

            debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
            if (islemKar > 0):
                toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
                debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal SHORT Close Take Profit\n"
            else:
                toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
                debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal SHORT Close Stop Loss\n"            
            debugMsg += "\n"
            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            if (islemKar > 0):
                debugMsg += "SHORT Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
            else:
                debugMsg += "SHORT Order SL\t\t: " + str(round(hedefFiyati,7)) + "\n"            
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t\t: % " + str(round(karOrani * 100,3)) + "\n"  

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
debugMsg += "\n"
debugMsg += "Report\n"
debugMsg += "\n"
debugMsg += "Strategy\t: " + str(symbol) + " (" + str(kaldirac) + "x) (" + str(interval) + ") EMA" + str(emaBuy) + " " + str(emaBuyType) + " EMA" + str(emaSell) + " " + str(emaSellType) + "\n"
debugMsg += "Invest\t\t: " + str(round(baslangicPara,7)) + "\n"
debugMsg += "ROI\t\t: " + str(round(toplamKar,7)) + "\n"
debugMsg += "Total Fee\t: " + str(round(toplamFee,3)) + "\n"
debugMsg += "Fund\t\t: " + str(round(cuzdan,7)) + "\n"
debugMsg += "ROI\t\t: % " + str(round((toplamKar / baslangicPara) * 100,3)) + "\n"
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