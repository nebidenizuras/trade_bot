'''
- Bu stratejide işleme giriş bandı Fibonacci kanalına göre belirlenmektedir.
- EMA8 değeri FIB 0.5 üzerinde ise, long işleme değmişsem long girerim (FIB 0.572)
  FIB 0.772 de kar alırım
- EMA8 değeri FIB 0.5 altında ise, short işleme değmişsem short girerim (FIB 0.428)
  FIB 0.228 de kar alırım
'''

from operator import index
from ta.trend import ema_indicator
import pandas as pd
import csv
import os
from Indicators.fibonacci_retracement import calculate_fib
import array as arr
from datetime import timedelta

kaldirac = 1
start = False
islemBitti = False

bantMinimumOran = 0.002
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
stopFiyatı = 0

islemFee = 0
toplamFee = 0

islemKar = 0
toplamKar = 0

#ATTRIBUTES
feeOrani = 0.0004 # percent
position = ""
baslangicPara = 111
cuzdan = baslangicPara

startTime = 0
stopTime = 0

fibVal = 8
emaVal = 5

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

coin = "APEUSDT"
timeFrame = "15m"
#csvName = "Historical_Data/" + coin + "_" + timeFrame + ".csv"
csvName = coin + "_" + timeFrame + ".csv"
logFileName = "LogFile_" +  coin + "_" + timeFrame + ".txt"

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
df["EMA"] = ema_indicator(df["close"],emaVal)
df["FIB_1"] = calculate_fib(df,fibVal, 1)
df["FIB_0_772"] = calculate_fib(df,fibVal, 0.772)
df["FIB_0_572"] = calculate_fib(df,fibVal, 0.572)
df["FIB_0_500"] = calculate_fib(df,fibVal, 0.5)
df["FIB_0_428"] = calculate_fib(df,fibVal, 0.428)
df["FIB_0_228"] = calculate_fib(df,fibVal, 0.228)
df["FIB_0"] = calculate_fib(df,fibVal, 0)  

print("Strategy Back Test is starting......")

for i in range(df.shape[0]):
    if i > (fibVal + 2):        
        long_signal = df["EMA"][i] > df["FIB_0_500"][i]   
        short_signal = df["EMA"][i] < df["FIB_0_500"][i]

        ### Bandı ve Giriş Bilgilerini Ayarla
        if (position == "") and (long_signal or short_signal):

            bantReferans = (((df["FIB_1"][i] / df["FIB_0"][i]) - 1) / 7)

            if (bantReferans >= bantMinimumOran):
                start = True
                startTime =  df["openTime"][i]

                shortStopFiyat = df["FIB_1"][i]
                longKarFiyat = df["FIB_0_772"][i]
                longGirisFiyat = df["FIB_0_572"][i]
                referansOrtaFiyat = df["FIB_0_500"][i]                 
                shortGirisFiyat = df["FIB_0_428"][i]           
                shortKarFiyat = df["FIB_0_228"][i]
                longStopFiyat = df["FIB_0"][i]                 

                debugMsg = ""
                debugMsg += "---------------------------------------\n" 
                debugMsg += str(toplamIslemSayisi + 1) + ". İşlem Sinyali Geldi\n"
                debugMsg += "\n"  
                debugMsg += "Al-Sat Bant Aralığı ->\n"
                debugMsg += "İşlem Bant Aralığı\t: % " + str(bantReferans * 100) + "\n"
                debugMsg += "Short Stop Ol Fiyat\t: " + str(shortStopFiyat) + "\n"
                debugMsg += "Long Kar Al Fiyat\t: " + str(longKarFiyat) + "\n"
                debugMsg += "Long Giriş Fiyat\t: " + str(longGirisFiyat) + "\n"
                debugMsg += "Referans Orta Fiyat\t: " + str(referansOrtaFiyat) + "\n"
                debugMsg += "Short Giriş Fiyat\t: " + str(shortGirisFiyat) + "\n"
                debugMsg += "Short Kar Al Fiyat\t: " + str(shortKarFiyat) + "\n"
                debugMsg += "Long Stop Ol Fiyat\t: " + str(longStopFiyat) + "\n"
                debugMsg += "\n"  
                debugMsg += "FIB Değerleri -> \n"
                debugMsg += "FIB_1_000 : " + str(df["FIB_1"][i]) + "\n"
                debugMsg += "FIB_0_500 : " + str(df["FIB_0_500"][i]) + "\n"
                debugMsg += "FIB_0_000 : " + str(df["FIB_0"][i]) + "\n"    
                debugMsg += "\n"
                debugMsg += "EMA(" + str(emaVal) + ") -> " + str(df["EMA"][i]) + "\n" 
                debugMsg += "\n" 
            else:
                start = False   
    
        # LONG İşleme Gir
        if start and (df["high"][i] >= longGirisFiyat and longGirisFiyat >= df["low"][i]) and position == "" and long_signal:
            islemBitti = False
            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee
            position = "Long"  
            islemFiyati = longGirisFiyat
            hedefFiyati = longKarFiyat
            stopFiyatı = longStopFiyat
            islemBuyuklugu = cuzdan * kaldirac
            karOrani = (longKarFiyat / longGirisFiyat) - 1 
            debugMsg += "İşlem Giriş Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Giriş Fiyatı\t: " + str(islemFiyati) + "\n"
            debugMsg += "İşlem Giriş Büyüklüğü\t: " + str(islemBuyuklugu) + "\n"
            debugMsg += "İşlem Giriş Fee\t: " + str(islemFee) + "\n"
            debugMsg += "\n"

        # LONG Kar Al
        if start and (df["high"][i] >= hedefFiyati) and position == "Long":
            islemKar = cuzdan * karOrani * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee
            debugMsg += "!! LONG İşlem Kar Al Oldu. !!\n"
            debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Kar Al Fiyatı\t: " + str(hedefFiyati) + "\n"
            debugMsg += "İşlem Çıkış Fee\t: " + str(islemFee) + "\n" 
            debugMsg += "İşlem Kar\t\t: " + str(islemKar) + "\n"         
            debugMsg += "---------------------------------------\n" 

            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            islemBitti = True
            start = False
            #print(debugMsg)    
            logFileObject.write(debugMsg)

        # LONG Stop Ol
        if start and (df["low"][i] <= stopFiyatı) and position == "Long":
            islemKar = cuzdan * (((stopFiyatı - islemFiyati) / islemFiyati)) * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += "!! LONG İşlem Stop Oldu. !!\n"
            debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Stop Fiyatı\t: " + str(stopFiyatı) + "\n"
            debugMsg += "İşlem Çıkış Fee\t: " + str(islemFee) + "\n" 
            debugMsg += "İşlem Kar\t\t: " + str(islemKar) + "\n"         
            debugMsg += "---------------------------------------\n"                

            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
            islemBitti = True
            start = False
            #print(debugMsg)    
            logFileObject.write(debugMsg)

        # SHORT İşleme Gir
        if start and (df["high"][i] >= shortGirisFiyat and shortGirisFiyat >= df["low"][i]) and position == "" and short_signal:
            islemBitti = False
            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee
            position = "Short"  
            islemFiyati = shortGirisFiyat
            hedefFiyati = shortKarFiyat
            stopFiyatı = shortStopFiyat
            islemBuyuklugu = cuzdan * kaldirac
            karOrani = (shortGirisFiyat / shortKarFiyat) - 1 
            debugMsg += "İşlem Giriş Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Giriş Fiyatı\t: " + str(islemFiyati) + "\n"
            debugMsg += "İşlem Giriş Büyüklüğü\t: " + str(islemBuyuklugu) + "\n"
            debugMsg += "İşlem Giriş Fee\t: " + str(islemFee) + "\n"
            debugMsg += "\n"
            

        # SHORT Kar Al
        if start and (df["low"][i] <= hedefFiyati) and position == "Short":
            islemKar = cuzdan * karOrani * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee
            debugMsg += "!! SHORT İşlem Kar Al Oldu. !!\n"
            debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Kar Al Fiyatı\t: " + str(hedefFiyati) + "\n"
            debugMsg += "İşlem Çıkış Fee\t: " + str(islemFee) + "\n" 
            debugMsg += "İşlem Kar\t\t: " + str(islemKar) + "\n"         
            debugMsg += "\n"   

            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            islemBitti = True
            start = False
            #print(debugMsg)    
            logFileObject.write(debugMsg)

        # SHORT Stop Ol
        if start and (df["high"][i] >= stopFiyatı) and position == "Short":
            islemKar = cuzdan * (((islemFiyati - stopFiyatı) / islemFiyati)) * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOrani * kaldirac
            toplamFee += islemFee

            debugMsg += "!! SHORT İşlem Stop Oldu. !!\n"
            debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Stop Fiyatı\t: " + str(stopFiyatı) + "\n"
            debugMsg += "İşlem Çıkış Fee\t: " + str(islemFee) + "\n" 
            debugMsg += "İşlem Kar\t\t: " + str(islemKar) + "\n"         
            debugMsg += "\n"               
            
            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1   
            islemBitti = True
            start = False        
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
            print("PARA BITTI")
            quit()   
     
debugMsg = ""
debugMsg += "\n"
debugMsg += "****************************************\n"
debugMsg += "Parite : " + coin + "\nZaman Dilimi : " + timeFrame + "\n"
debugMsg += "Strateji -> EMA" + str(emaVal) + " Close Signal\n" 
debugMsg += "Fibonacci -> " + str(fibVal) + "\n"
debugMsg += "İşlem Bandı Minimum\t: % " + str(bantMinimumOran * 100) + "\n"
debugMsg += "Başlangıç Para($)\t: " + str(baslangicPara) + "\n"
debugMsg += "Kar($)\t\t\t: " + str(cuzdan - baslangicPara) + "\n"
debugMsg += "Toplam Ödenen Fee($)\t: " + str(toplamFee) + "\n"
debugMsg += "Son Para($)\t\t: " + str(cuzdan - toplamFee) + "\n"
debugMsg += "Kazanç\t\t\t: % " + str(((cuzdan - baslangicPara - toplamFee) / baslangicPara) * 100) + "\n"
debugMsg += "Kaldıraç\t\t: " + str(kaldirac) + "x\n"
debugMsg += "Toplam İşlem Adet\t: " + str(toplamIslemSayisi) + "\n"
debugMsg += "Karlı İşlem Adet\t: " + str(toplamKarliIslemSayisi) + "\n"
debugMsg += "Stop İşlem Adet\t\t: " + str(toplamZararKesIslemSayisi) + "\n"
debugMsg += "Kar Başarı Oranı\t: % " + str((toplamKarliIslemSayisi / toplamIslemSayisi) * 100) + "\n"
debugMsg += "Zarar Kes Oranı\t\t: % " + str((toplamZararKesIslemSayisi / toplamIslemSayisi) * 100) + "\n"
debugMsg += "****************************************\n"


print(debugMsg)
logFileObject.write(debugMsg)
logFileObject.close()