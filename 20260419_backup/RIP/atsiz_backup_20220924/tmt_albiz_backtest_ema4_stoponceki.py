'''
- EMA'lar open hesaplanır. 2 Open 2 Close 34 Open hesaplanır
- EMA 2 Open > EMA 2 close ise ve EMA34 long ise long gir
- EMA 2 Open < EMA 2 close ise ve EMA34 short ise long gir
  8'i yukarı kırdığı anda eğer ema 3-5'de ema 8 üzeri ise stop ol, yoksa belirli kar al çık yeniden gir.
- GMT'de çalışır
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
from telegram_bot import warn


islemFiyati = 0
hedefFiyati = 0
islemBuyuklugu = 0

#ATTRIBUTES
kaldirac = 1
feeOrani = 0.0004 # percent
karOrani = 0.002 # percent

baslangicPara = 100
cuzdan = baslangicPara

islemFee = 0
islemKar = 0

toplamFee = 0
toplamKar = 0

startTime = 0
stopTime = 0

debugMsg = ""
position = ""

start = False
islemBitti = False

ema_buy_price = 0.0
ema_sell_price = 0.0
current_price = 0.0
long_stop_price = 0.0
short_stop_price = 0.0

long_signal = False
short_signal = False

# Sinyal Değerleri
emaLong = 1   
emaLongType = "close"
emaShort = 8    
emaShortType = "close"
emaHigh = 1   
emaHighType = "high"
emaLow = 1    
emaLowType = "low"

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

# Parite Bilgileri
symbol = "KNCUSDT"
interval = "1m"
#timeFrame = 1
#limit = emaShort * 4

get_historical_data_symbol("Future", symbol, "17 Sep, 2022", "18 Sep, 2022", interval)

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
df["EMALong"] = tb.ema(df[emaLongType],emaLong)
df["EMAShort"] = tb.ema(df[emaShortType],emaShort)
df["EMAHigh"] = tb.ema(df[emaHighType],emaHigh)
df["EMALow"] = tb.ema(df[emaLowType],emaLow)


print("Strategy Back Test is starting......")

for i in range(df.shape[0]):
    if i > emaShort * 4:
        ema_sell_price = df["EMAShort"][i-1]
        ema_buy_price = df["EMALong"][i-1]
        #long_stop_price = df["EMALow"][i-2]
        #short_stop_price = df["EMAHigh"][i-2]
        long_stop_price = (df["EMALow"][i-2] * (1 - karOrani))
        short_stop_price = (df["EMAHigh"][i-2] * (1 + karOrani))

        long_signal = (ema_buy_price > ema_sell_price)
        short_signal = (ema_buy_price < ema_sell_price)

        ### Giriş Bilgilerini Ayarla
        if (start == False) and (position == "") and ((long_signal == True) or (short_signal == True)): 
            start = True
            startTime =  df["openTime"][i]

            debugMsg = ""
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
            islemFiyati = df["open"][i-1]
            hedefFiyati = islemFiyati * (1 + karOrani)
            islemBuyuklugu = cuzdan * kaldirac
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee            

            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][i-1]) + "\n"
            debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "LONG TP Price\t\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(islemBuyuklugu,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,4)) + "\n"
            debugMsg += "\n" 
            debugMsg += "\n"
            debugMsg += "Reference Bands\n" 
            debugMsg += "EMA(" + str(emaHigh) + ") High -> " + str(round(short_stop_price,4)) + "\n"
            debugMsg += "EMA(" + str(emaLong) + ") Long -> " + str(round(ema_buy_price,4)) + "\n" 
            debugMsg += "EMA(" + str(emaShort) + ") Short -> " + str(round(ema_sell_price,4)) + "\n"
            debugMsg += "EMA(" + str(emaLow) + ") Low -> " + str(round(long_stop_price,4)) + "\n"
            debugMsg += "\n"  

        # Long İşlem Kar Al
        elif (start == True) and (position == "Long") and (df["high"][i-1] >= hedefFiyati):
            islemKar = cuzdan * (((hedefFiyati - islemFiyati) / islemFiyati)) * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemBuyuklugu = cuzdan * kaldirac
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee

            debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
            debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal LONG Close Take Profit\n"
            debugMsg += "\n"
            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][i-1]) + "\n"
            debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "LONG Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(islemBuyuklugu,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t\t: % " + str(round(karOrani * 100,3)) + "\n"                
        
            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            islemBitti = True       

        # Long İşlem Stop Ol
        elif (start == True) and (position == "Long") and (long_stop_price >= df["low"][i-1]):
            hedefFiyati = long_stop_price

            islemKar = cuzdan * (((hedefFiyati - islemFiyati) / islemFiyati)) * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemBuyuklugu = cuzdan * kaldirac
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee

            debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
            debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal LONG Close Stop Loss\n"            
            debugMsg += "\n"
            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][i-1]) + "\n"
            debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "LONG Order SL\t\t: " + str(round(hedefFiyati,7)) + "\n"            
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(islemBuyuklugu,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t\t: % " + str(round(karOrani * 100,3)) + "\n"                

            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
            islemBitti = True

    # SHORT İŞLEM
        # Short İşlem Aç
        if (start == True) and (position == "") and (short_signal == True):
            position = "Short"  

            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFiyati = df["open"][i-1]
            hedefFiyati = islemFiyati * (1 - karOrani) 
            islemBuyuklugu = cuzdan * kaldirac
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee     

            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][i-1]) + "\n"
            debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "SHORT TP Price\t\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(islemBuyuklugu,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,4)) + "\n"
            debugMsg += "\n" 
            debugMsg += "\n"
            debugMsg += "Reference Bands\n" 
            debugMsg += "EMA(" + str(emaHigh) + ") High -> " + str(round(short_stop_price,4)) + "\n"
            debugMsg += "EMA(" + str(emaLong) + ") Long -> " + str(round(ema_buy_price,4)) + "\n" 
            debugMsg += "EMA(" + str(emaShort) + ") Short -> " + str(round(ema_sell_price,4)) + "\n"
            debugMsg += "EMA(" + str(emaLow) + ") Low -> " + str(round(long_stop_price,4)) + "\n"
            debugMsg += "\n"  

        # Short İşlem Kar Al
        elif (start == True) and (position == "Short") and (df["low"][i-1] <= hedefFiyati):
            islemKar = cuzdan * (((islemFiyati - hedefFiyati) / islemFiyati)) * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemBuyuklugu = cuzdan * kaldirac
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee

            debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
            debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal SHORT Close Take Profit\n"
            debugMsg += "\n"
            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "SHORT Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(islemBuyuklugu,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t\t: % " + str(round(karOrani * 100,3)) + "\n"                
        
            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            islemBitti = True  

        # Short İşlem Stop Ol
        elif (start == True)  and (position == "Short") and (short_stop_price <= df["high"][i-1]):
            hedefFiyati = short_stop_price

            islemKar = cuzdan * (((islemFiyati - hedefFiyati) / islemFiyati)) * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemBuyuklugu = cuzdan * kaldirac
            islemFee = islemBuyuklugu * feeOrani
            toplamFee += islemFee

            debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
            debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal SHORT Close Stop Loss\n"            
            debugMsg += "\n"
            debugMsg += "Order Time\t\t\t: " + str(df["openTime"][i-1]) + "\n"
            debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
            debugMsg += "SHORT Order SL\t\t: " + str(round(hedefFiyati,7)) + "\n"            
            debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
            debugMsg += "Order Fee\t\t\t: " + str(round(islemFee,7)) + "\n"
            debugMsg += "Order Profit\t\t: % " + str(round(karOrani * 100,3)) + "\n"                

            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
            islemBitti = True  

        if islemBitti == True:  
            islemBitti = False
            position = ""   
            start = False         
            islemKar = 0
            islemFee = 0
            islemFiyati = 0
            hedefFiyati = 0 
         
        #print(debugMsg)    
        logFileObject.write(debugMsg)

        if (cuzdan < 0):
            debugMsg = ""
            debugMsg += "\n"
            debugMsg = "****************************************\n"
            debugMsg += "\n"
            debugMsg += "Report\n"
            debugMsg += "\n"
            debugMsg += "Strategy\t: " + str(symbol) + " (" + str(kaldirac) + "x) (" + str(interval) + ") (EMA" + str(emaLong) + " " + str(emaLongType) + ") (EMA" + str(emaShort) + " " + str(emaShortType) + ") (EMA" + str(emaHigh) + " " + str(emaHighType) + ") (EMA" + str(emaLow) + " " + str(emaLowType) +  ")\n"
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
            debugMsg += "****************************************\n"
            print(debugMsg)
            logFileObject.write(debugMsg)
            logFileObject.close()

            print("PARA BITTI")
            quit()   
     
debugMsg = "****************************************\n"
debugMsg += "\n"
debugMsg += "Report\n"
debugMsg += "\n"
debugMsg += "Strategy\t: " + str(symbol) + " (" + str(kaldirac) + "x) (" + str(interval) + ") (EMA" + str(emaLong) + " " + str(emaLongType) + ") (EMA" + str(emaShort) + " " + str(emaShortType) + ") (EMA" + str(emaHigh) + " " + str(emaHighType) + ") (EMA" + str(emaLow) + " " + str(emaLowType) +  ")\n"
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
debugMsg += "****************************************\n"

print(debugMsg)
logFileObject.write(debugMsg)
logFileObject.close()