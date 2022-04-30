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


islemFiyatı = 0
hedefFiyati = 0
islemBuyuklugu = 0

#ATTRIBUTES
kaldirac = 1
feeOranı = 0.0004 # percent
karOrani = 0.0022 # percent

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
emaBuy = 5
emaBuyType = "open"
emaSell = 13    
emaSellType = "open"
emaSignal = 144 
emaSignalType = "open"

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

symbol = "APEUSDT"
interval = "5m"

#get_historical_data_symbol("Future", symbol, "20 April, 2022", "24 April, 2022", interval)

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
df["EMASIGNAL"] = tb.ema(df[emaSignalType],emaSignal)

print("Strategy Back Test is starting......")

for i in range(df.shape[0]):
    if i > emaSignal * 3: #(df.shape[0] - (2 * 5 * 12 * 24)):
        long_signal = (df["EMABUY"][i] > df["EMASELL"][i]) and (df["EMABUY"][i] > df["EMASIGNAL"][i]) and (df["EMASELL"][i] > df["EMASIGNAL"][i])
        short_signal = (df["EMABUY"][i] < df["EMASELL"][i]) and (df["EMABUY"][i] < df["EMASIGNAL"][i]) and (df["EMASELL"][i] < df["EMASIGNAL"][i])       

        ### Giriş Bilgilerini Ayarla
        if (position == "") and (long_signal or short_signal):
            start = True
            startTime =  df["openTime"][i]
            debugMsg = ""
            debugMsg += "---------------------------------------\n" 
            debugMsg += "Sinyal Oluştu ->\n" + str(symbol) + " " + str(interval) + "\n"
            debugMsg += str(toplamIslemSayisi + 1) + ". İşlem Sinyali : "
            if long_signal:
                debugMsg += "LONG\n"
            elif short_signal:
                debugMsg += "SHORT\n"
            debugMsg += "\n"
            debugMsg += "EMA(" + str(emaBuy) + ") -> " + str(df["EMABUY"][i]) + "\n" 
            debugMsg += "EMA(" + str(emaSell) + ") -> " + str(df["EMASELL"][i]) + "\n"
            debugMsg += "EMA(" + str(emaSignal) + ") -> " + str(df["EMASIGNAL"][i]) + "\n"
            debugMsg += "\n"  

    # LONG İŞLEM
        # Long İşlem Aç
        if start and position == "" and long_signal:
            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFee = cuzdan * feeOranı * kaldirac
            toplamFee += islemFee
            position = "Long"    
            islemFiyatı = df["open"][i]
            hedefFiyati = islemFiyatı * (1 + karOrani)
            islemBuyuklugu = cuzdan * kaldirac
            debugMsg += "İşlem Giriş Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Giriş Fiyatı\t: " + str(islemFiyatı) + "\n"
            debugMsg += "İşlem Hedef Fiyatı\t: " + str(hedefFiyati) + "\n"
            debugMsg += "İşlem Büyüklüğü\t: " + str(islemBuyuklugu) + "\n"
            debugMsg += "İşlem Giriş Fee\t: " + str(islemFee) + "\n"
            debugMsg += "\n"  

        # Long İşlem Kar Al
        if start and (position == "Long") and (df["high"][i] > hedefFiyati):
            islemKar = cuzdan * karOrani * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOranı * kaldirac
            toplamFee += islemFee

            debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Kar Al Fiyatı\t: " + str(hedefFiyati) + "\n"
            debugMsg += "İşlem Çıkış Fee\t: " + str(islemFee) + "\n" 
            debugMsg += "İşlem Kar\t\t: " + str(islemKar) + "\n"         
            debugMsg += "\n"          

            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            position = ""   
            start = False 
            islemKar = 0
            islemFee = 0
            islemFiyatı = 0
            hedefFiyati = 0

        # Long İşlem Stop Ol
        if start and (position == "Long") and short_signal:
            hedefFiyati = df["open"][i]

            islemKar = cuzdan * (((hedefFiyati - islemFiyatı) / islemFiyatı)) * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOranı * kaldirac
            toplamFee += islemFee

            debugMsg += "!! LONG İşlem Stop Oldu !!\n"
            debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Stop Fiyatı\t: " + str(hedefFiyati) + "\n"
            debugMsg += "İşlem Çıkış Fee\t: " + str(islemFee) + "\n" 
            debugMsg += "İşlem Kar\t\t: " + str(islemKar) + "\n"         
            debugMsg += "\n"          

            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
            position = ""   
            start = False 
            islemKar = 0
            islemFee = 0
            islemFiyatı = 0
            hedefFiyati = 0    

    # SHORT İŞLEM
        # Short İşlem Aç
        if start and position == "" and short_signal:
            toplamIslemSayisi = toplamIslemSayisi + 1
            islemFee = cuzdan * feeOranı * kaldirac
            toplamFee += islemFee
            position = "Short"    
            islemFiyatı = df["open"][i]
            hedefFiyati = islemFiyatı * (1 - karOrani)
            islemBuyuklugu = cuzdan * kaldirac
            debugMsg += "İşlem Giriş Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Giriş Fiyatı\t: " + str(islemFiyatı) + "\n"
            debugMsg += "İşlem Hedef Fiyatı\t: " + str(hedefFiyati) + "\n"
            debugMsg += "İşlem Büyüklüğü\t: " + str(islemBuyuklugu) + "\n"
            debugMsg += "İşlem Giriş Fee\t: " + str(islemFee) + "\n"
            debugMsg += "\n"  

        # Short İşlem Kar Al
        if start and (position == "Short") and (df["low"][i] < hedefFiyati):
            islemKar = cuzdan * karOrani * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOranı * kaldirac
            toplamFee += islemFee

            debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Kar Al Fiyatı\t: " + str(hedefFiyati) + "\n"
            debugMsg += "İşlem Çıkış Fee\t: " + str(islemFee) + "\n" 
            debugMsg += "İşlem Kar\t\t: " + str(islemKar) + "\n"         
            debugMsg += "\n"          

            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1
            position = ""   
            start = False 
            islemKar = 0
            islemFee = 0
            islemFiyatı = 0
            hedefFiyati = 0

        # Short İşlem Stop Ol
        if start and (position == "Short") and long_signal:
            hedefFiyati = df["open"][i]

            islemKar = cuzdan * (((islemFiyatı - hedefFiyati) / islemFiyatı)) * kaldirac
            toplamKar += islemKar
            cuzdan = cuzdan + islemKar
            islemFee = cuzdan * feeOranı * kaldirac
            toplamFee += islemFee

            debugMsg += "!! SHORT İşlem Stop Oldu !!\n"
            debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Stop Fiyatı\t: " + str(hedefFiyati) + "\n"
            debugMsg += "İşlem Çıkış Fee\t: " + str(islemFee) + "\n" 
            debugMsg += "İşlem Kar\t\t: " + str(islemKar) + "\n"         
            debugMsg += "\n"          

            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1
            position = ""   
            start = False 
            islemKar = 0
            islemFee = 0
            islemFiyatı = 0
            hedefFiyati = 0    
         
        #print(debugMsg)    
        logFileObject.write(debugMsg)

        if (cuzdan + 10) < toplamFee:
            print("PARA BITTI")
            quit()   
     
debugMsg = ""
debugMsg += "\n"
debugMsg += "****************************************\n"
debugMsg += "Parite : " + symbol + "\nZaman Dilimi : " + interval + "\n"
debugMsg += "Strateji -> EMA" + str(emaBuy) +  " Open / EMA" + str(emaSell) + " Close / EMA" + str(emaSignal) + " Open\n"
debugMsg += "Başlangıç Para($)\t: " + str(baslangicPara) + "\n"
debugMsg += "Kar($)\t\t\t: " + str(cuzdan - baslangicPara) + "\n"
debugMsg += "Toplam Ödenen Fee($)\t: " + str(toplamFee) + "\n"
debugMsg += "Son Para($)\t\t: " + str(cuzdan - toplamFee) + "\n"
debugMsg += "Kazanç\t\t\t: % " + str(((cuzdan - baslangicPara - toplamFee) / baslangicPara) * 100) + "\n"
debugMsg += "Kaldıraç\t\t: " + str(kaldirac) + "x\n"
debugMsg += "Kar Oranı\t\t: % " + str(((cuzdan - baslangicPara - toplamFee) / baslangicPara)) + "\n"
debugMsg += "Toplam İşlem Adet\t: " + str(toplamIslemSayisi) + "\n"
debugMsg += "Karlı İşlem Adet\t: " + str(toplamKarliIslemSayisi) + "\n"
debugMsg += "Stop İşlem Adet\t\t: " + str(toplamZararKesIslemSayisi) + "\n"
debugMsg += "Kar Başarı Oranı\t: % " + str((toplamKarliIslemSayisi / toplamIslemSayisi) * 100) + "\n"
debugMsg += "Zarar Kes Oranı\t\t: % " + str((toplamZararKesIslemSayisi / toplamIslemSayisi) * 100) + "\n"
debugMsg += "****************************************\n"

print(debugMsg)
logFileObject.write(debugMsg)
logFileObject.close()