from calendar import c
from operator import index
from numpy import true_divide
import pandas_ta as tb
import pandas as pd
from ta.trend import ADXIndicator
import csv
import math
from statistics import mean


kaldirac = 1 
rsiAltLimit  = 30
rsiUstLimit = 70
start = False


# Martingale Katsayılar
martingaleKatsayilar = [0, 1, 1.4, 1, 1.4, 1.9, 2.5, 3.3, 4.4] # 16,9 katsayı 
pozisyonİslemFiyatları = 0
pozisyonBuyuklugu = 0
bantReferans = 0.005
cikisOrani = 3 * bantReferans
girisOrani = bantReferans / 2
referansOrtaFiyat = 0
ustGirisFiyat = 0
altGirisFiyat = 0
ustCikisFiyat = 0
altCikisFiyat = 0
islemSirasi = ["","","","","","","","",""]

#ATTRIBUTES
fee = 0.0004 # percent
position = ""
baslangicPara = 100
cuzdan = baslangicPara

startTime = 0
stopTime = 0

# Order Amount Calculation
toplamIslemSayisi = 0
islemSayisi = 0

csvName = "Historical_Data/BTCUSDT_5m.csv"

attributes = ["openTime","open","high","low","close","volume","1","2","3","4","5","6"]
df = pd.read_csv(csvName, names = attributes)

df['open'] = df['open'].astype('float')
df['close'] = df['close'].astype('float')
df['high'] = df['high'].astype('float')
df['low'] = df['low'].astype('float')
df["openTime"] = pd.to_datetime(df["openTime"],unit= "ms")
df["RSI"] = tb.rsi(df["close"],14)

print("rsi_martingale_strategy is starting......")



for i in range(df.shape[0]):
    if i > 100:
        long_signal = df["RSI"][i-2] <= rsiAltLimit
        short_signal = df["RSI"][i-2] >= rsiUstLimit

        ### Bandı ve Giriş Bilgilerini Ayarla
        #if ((long_signal and position == "") or (short_signal and position == "")) and (start == False):
        if (position == "") and (start == False) and (49 <= df["RSI"][i-2]) and (df["RSI"][i-2] <= 51):
            start = True
            referansOrtaFiyat = df["close"][i-2]
            startTime =  df["openTime"][i-2]
            altGirisFiyat = referansOrtaFiyat * (1 - girisOrani)
            ustGirisFiyat = referansOrtaFiyat * (1 + girisOrani)
            altCikisFiyat = altGirisFiyat * (1 - cikisOrani)
            ustCikisFiyat = ustGirisFiyat * (1 + cikisOrani)
            pozisyonBuyuklugu = cuzdan / 20            

        if start and (df["high"][i-1] >= ustGirisFiyat) and islemSayisi < 8 and position != "Long": #long gir
            islemSayisi = islemSayisi + 1
            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * fee * kaldirac)
            islemSirasi[islemSayisi] = "Long"
            position = "Long"          

        if start and (df["low"][i-1] <= altGirisFiyat) and islemSayisi < 8 and position != "Short": #short gir
            islemSayisi = islemSayisi + 1        
            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * fee * kaldirac)
            islemSirasi[islemSayisi] = "Short"
            position = "Short"            

        if start and (df["high"][i] >= ustCikisFiyat or df["low"][i] <= altCikisFiyat): # tüm islemleri kapat
            kumulatifKar = 0.0 
            stopTime =  df["openTime"][i]           
            if (df["high"][i] >= ustCikisFiyat): #Üst bantta kapatıyoruz
                if islemSirasi[1] == "Long": # karlı yönde kapattık
                    counter = 1
                    while counter <= islemSayisi:
                        if counter % 2 == 1:
                            kumulatifKar = kumulatifKar + (pozisyonBuyuklugu * martingaleKatsayilar[counter] * cikisOrani)  
                            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * (1+cikisOrani) * fee * kaldirac)
                        if counter % 2 == 0:
                            kumulatifKar = kumulatifKar - (pozisyonBuyuklugu * martingaleKatsayilar[counter] * cikisOrani)  
                            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * (1-cikisOrani) * fee * kaldirac)   
                        counter = counter + 1
                elif islemSirasi[1] == "Short": # batmadık ama az kar ettik
                    counter = 1
                    while counter <= islemSayisi:
                        if counter % 2 == 1:
                            kumulatifKar = kumulatifKar - (pozisyonBuyuklugu * martingaleKatsayilar[counter] * cikisOrani) 
                            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * (1-cikisOrani) * fee * kaldirac) 
                        if counter % 2 == 0:
                            kumulatifKar = kumulatifKar + (pozisyonBuyuklugu * martingaleKatsayilar[counter] * cikisOrani) 
                            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * (1+cikisOrani) * fee * kaldirac)
                        counter = counter + 1

            elif (df["low"][i] <= altCikisFiyat): #Alt bantta kapatıyoruz
                if islemSirasi[1] == "Long": # batmadık ama az kar ettik 
                    counter = 1
                    while counter <= islemSayisi:
                        if counter % 2 == 1:
                            kumulatifKar = kumulatifKar - (pozisyonBuyuklugu * martingaleKatsayilar[counter] * cikisOrani)  
                            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * (1-cikisOrani) * fee * kaldirac) 
                        if counter % 2 == 0:
                            kumulatifKar = kumulatifKar + (pozisyonBuyuklugu * martingaleKatsayilar[counter] * cikisOrani)   
                            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * (1+cikisOrani) * fee * kaldirac)                          
                        counter = counter + 1
                elif islemSirasi[1] == "Short": # karlı yönde kapattık
                    counter = 1
                    while counter <= islemSayisi:
                        if counter % 2 == 1:
                            kumulatifKar = kumulatifKar + (pozisyonBuyuklugu * martingaleKatsayilar[counter] * cikisOrani)  
                            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * (1+cikisOrani) * fee * kaldirac)
                        if counter % 2 == 0:
                            kumulatifKar = kumulatifKar - (pozisyonBuyuklugu * martingaleKatsayilar[counter] * cikisOrani) 
                            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * (1-cikisOrani) * fee * kaldirac)     
                        counter = counter + 1
            cuzdan = cuzdan + kumulatifKar   

            debugMsg = ""
            debugMsg += "---------------------------------------\n"
            debugMsg += "Başlangıç Zamanı   : " + str(startTime) + "\n"
            debugMsg += "Bitiş Zamanı       : " + str(stopTime) + "\n"
            debugMsg += "Toplam İşlem Sayısı: " + str(islemSayisi) + "\n"
            debugMsg += "İşlem Kazancı      : " + str(kumulatifKar) + "\n"
            debugMsg += "Al-Sat Bant Aralığı\n"
            debugMsg += "Üst Çıkış          : " + str(ustCikisFiyat) + "\n"
            debugMsg += "Üst Giriş          : " + str(ustGirisFiyat) + "\n"
            debugMsg += "Referans Orta Fiyat: "+ str(referansOrtaFiyat) + "\n"
            debugMsg += "Alt Çıkış          : " + str(altCikisFiyat) + "\n"
            debugMsg += "Alt Giriş          : " + str(altGirisFiyat) + "\n"
            debugMsg += "---------------------------------------\n"           
            print(debugMsg)                 
            start = False     
            position = ""
            islemSayisi = 0
            toplamIslemSayisi = toplamIslemSayisi + 1

        if cuzdan < 10:
            print("PARA BITTI")
            quit()   
     
lastDebugMsg = ""
lastDebugMsg += "****************************************\n"
lastDebugMsg += "Strateji RSI 30 veya 70 de iken işleme giriş\n"
lastDebugMsg += "İşleme Giriş Bant Genişliği  : % " + str(bantReferans*100) + "\n"
lastDebugMsg += "Başlangıç Para               : " + str(baslangicPara) + "\n"
lastDebugMsg += "Kar                          : " + str(cuzdan - baslangicPara) + "\n"
lastDebugMsg += "Son Para                     : " + str(cuzdan) + "\n"
lastDebugMsg += "Kazanç                       : % " + str(((cuzdan - baslangicPara) / baslangicPara) * 100) + "\n"
lastDebugMsg += "Toplam İşlem Adet            : " + str(toplamIslemSayisi) + "\n"
lastDebugMsg += "Kaldıraç                     : " + str(kaldirac) + "x\n"
lastDebugMsg += "****************************************\n"
print(lastDebugMsg)
