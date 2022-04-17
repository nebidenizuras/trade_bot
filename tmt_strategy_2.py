'''
Bu stratejide işleme giriş bandı Fibonacci kanalına göre belirlenmektedir.
'''

from operator import index
import pandas_ta as tb
import pandas as pd
import csv
import os
from Indicators.fibonacci_retracement import calculate_fib
import array as arr

kaldirac = 1
start = False

# Martingale Katsayılar
martingaleKatsayilar = [0, 1, 1.4, 1, 1.4, 1.9, 2.5, 3.3, 4.4] # 16,9 katsayı 
#martingaleKatsayilar = [0, 1, 2.33, 3.1, 4.15, 5.55, 7.4, 9.85, 13.1, 17.45, 23.3, 31.1, 41.45] # 12 Pozisyon Hiç Efektif Değil
maxPozisyonSayisi = 1
katSayilarToplami = 0.1 # + 0.1 katsayı fee için
for i in range (maxPozisyonSayisi + 1):
    katSayilarToplami = katSayilarToplami + martingaleKatsayilar[i]

pozisyonİslemFiyatları = 0
pozisyonBuyuklugu = 0
bantMinimumOran = 0.002
bantReferans = 0
cikisOrani = 3 * bantReferans
girisOrani = bantReferans / 2
referansOrtaFiyat = 0
ustGirisFiyat = 0
altGirisFiyat = 0
ustCikisFiyat = 0
altCikisFiyat = 0
islemSirasi = ["","","","","","","","",""]
pozisyonAdetSayaci = arr.array('i', [0,0,0,0,0,0,0,0,0])

#ATTRIBUTES
fee = 0.0004 # percent
position = ""
baslangicPara = 111
cuzdan = baslangicPara

startTime = 0
stopTime = 0

fibVal = 5
emaBuy = 2
emaSell = 3

# Order Amount Calculation
toplamIslemSayisi = 0
islemSayisi = 0

coin = "MTLUSDT"
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
df["openTime"] = pd.to_datetime(df["openTime"],unit= "ms")
df["closeTime"] = pd.to_datetime(df["closeTime"],unit= "ms")
df["EMABUY"] = tb.ema(df["close"],emaBuy)
df["EMASELL"] = tb.ema(df["close"],emaSell)
df["FIB_1"] = calculate_fib(df,fibVal, 1)
df["FIB_0_500"] = calculate_fib(df,fibVal, 0.5)
df["FIB_0"] = calculate_fib(df,fibVal, 0)  

print("Strategy Back Test is starting......")

for i in range(df.shape[0]):
    if i > (fibVal + 2):
        long_signal = df["EMABUY"][i] > df["EMASELL"][i]
        short_signal = df["EMABUY"][i] < df["EMASELL"][i]

        ### Bandı ve Giriş Bilgilerini Ayarla
        if (position == "") and (long_signal or short_signal):

            bantReferans = (((df["FIB_1"][i] / df["FIB_0"][i]) - 1) / 7)

            if (bantReferans >= bantMinimumOran):
                start = True
                referansOrtaFiyat = df["FIB_0_500"][i]
                startTime =  df["openTime"][i]

                cikisOrani = 3 * bantReferans
                girisOrani = bantReferans / 2

                altGirisFiyat = referansOrtaFiyat * (1 - girisOrani)
                ustGirisFiyat = referansOrtaFiyat * (1 + girisOrani)
                altCikisFiyat = altGirisFiyat * (1 - cikisOrani)
                ustCikisFiyat = ustGirisFiyat * (1 + cikisOrani)
                pozisyonBuyuklugu = cuzdan / katSayilarToplami

                debugMsg = ""
                debugMsg += "---------------------------------------\n" 
                debugMsg += str(toplamIslemSayisi + 1) + ". İşlem Sinyali Geldi\n"
                debugMsg += "\n"  
                debugMsg += "Al-Sat Bant Aralığı ->\n"
                debugMsg += "İşlem Bant Aralığı  : %" + str(bantReferans * 100) + "\n"
                debugMsg += "Üst Çıkış           : " + str(ustCikisFiyat) + "\n"
                debugMsg += "Üst Giriş           : " + str(ustGirisFiyat) + "\n"
                debugMsg += "Referans Orta Fiyat : " + str(referansOrtaFiyat) + "\n"
                debugMsg += "Alt Giriş           : " + str(altGirisFiyat) + "\n"
                debugMsg += "Alt Çıkış           : " + str(altCikisFiyat) + "\n"
                debugMsg += "\n"  
                debugMsg += "FIB Değerleri -> \n"
                debugMsg += "FIB_1_000 : " + str(df["FIB_1"][i]) + "\n"
                debugMsg += "FIB_0_500 : " + str(df["FIB_0_500"][i]) + "\n"
                debugMsg += "FIB_0_000 : " + str(df["FIB_0"][i]) + "\n"    
                debugMsg += "\n"
                debugMsg += "EMA(" + str(emaBuy) + ") -> " + str(df["EMABUY"][i]) + "\n" 
                debugMsg += "EMA(" + str(emaSell) + ") -> " + str(df["EMASELL"][i]) + "\n"
                debugMsg += "\n" 
            else:
                start = False   

        if start and (df["high"][i] >= ustGirisFiyat and ustGirisFiyat >= df["low"][i]) and islemSayisi < maxPozisyonSayisi and position != "Long" and long_signal: #long gir
            islemSayisi = islemSayisi + 1
            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * fee * kaldirac)
            islemSirasi[islemSayisi] = "Long"
            position = "Long"     
            debugMsg += str(islemSayisi) + ".Pozisyon " + str(position) + "\n"
            debugMsg += "İşlem Mum Zamanı : " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Fiyatı     : " + str(ustGirisFiyat) + "\n"
            debugMsg += "İşlem Büyüklüğü  : " + str(pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * kaldirac) + "\n"
            debugMsg += "\n"  

        if start and (df["low"][i] <= altGirisFiyat and altGirisFiyat <= df["high"][i]) and islemSayisi < maxPozisyonSayisi and position != "Short" and short_signal: #short gir
            islemSayisi = islemSayisi + 1        
            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * fee * kaldirac)
            islemSirasi[islemSayisi] = "Short"
            position = "Short"            
            debugMsg += str(islemSayisi) + ".Pozisyon : " + str(position) + "\n"
            debugMsg += "İşlem Mum Zamanı : " + str(df["openTime"][i]) + "\n"
            debugMsg += "İşlem Fiyatı     : " + str(altGirisFiyat) + "\n"
            debugMsg += "İşlem Büyüklüğü  : " + str(pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * kaldirac) + "\n"
            debugMsg += "\n"  

        if start and (df["high"][i] >= ustCikisFiyat or df["low"][i] <= altCikisFiyat) and (position != ""): # tüm islemleri kapat
            kumulatifKar = 0.0 
            stopTime =  df["closeTime"][i]      
            pozisyonAdetSayaci[islemSayisi] = pozisyonAdetSayaci[islemSayisi] + 1

            if (df["high"][i] >= ustCikisFiyat): #Üst bantta kapatıyoruz

                debugMsg += "Long Yön İşlem Hedefi Geldi.\nTüm İşlemler Üst Hedef Bantta Kapatılıyor.\n"
                debugMsg += "İşlem Kapatma Fiyatı : " + str(ustCikisFiyat) + "\n"

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

                debugMsg += "Short Yön İşlem Hedefi Geldi.\nTüm İşlemler Alt Hedef Bantta Kapatılıyor.\n"
                debugMsg += "İşlem Kapatma Fiyatı : " + str(altCikisFiyat) + "\n"

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

            debugMsg += "\n"
            debugMsg += "Başlangıç Mum Zamanı : " + str(startTime) + "\n"
            debugMsg += "Bitiş Mum Zamanı     : " + str(stopTime) + "\n"
            debugMsg += "Toplam İşlem Sayısı  : " + str(islemSayisi) + "\n"
            debugMsg += "İşlem Kazancı($)     : " + str(kumulatifKar) + "\n"
            debugMsg += "---------------------------------------\n"           
            #print(debugMsg)    
            logFileObject.write(debugMsg)

            start = False     
            position = ""
            islemSayisi = 0
            toplamIslemSayisi = toplamIslemSayisi + 1

        if cuzdan < 10:
            print("PARA BITTI")
            quit()   
     
lastDebugMsg = ""
lastDebugMsg += "\n"
lastDebugMsg += "****************************************\n"
lastDebugMsg += "Parite : " + coin + "\nZaman Dilimi : " + timeFrame + "\n"
lastDebugMsg += "Strateji -> EMA" + str(emaBuy) +  " Close / EMA" + str(emaSell) + " Close Signal\n" 
lastDebugMsg += "Fibonacci -> " + str(fibVal) + "\n"
lastDebugMsg += "İşlem Bandı Minimum          : %" + str(bantMinimumOran * 100) + "\n"
lastDebugMsg += "Başlangıç Para($)            : " + str(baslangicPara) + "\n"
lastDebugMsg += "Kar($)                       : " + str(cuzdan - baslangicPara) + "\n"
lastDebugMsg += "Son Para($)                  : " + str(cuzdan) + "\n"
lastDebugMsg += "Kazanç                       : % " + str(((cuzdan - baslangicPara) / baslangicPara) * 100) + "\n"
lastDebugMsg += "Kaldıraç                     : " + str(kaldirac) + "x\n"
lastDebugMsg += "Maks Pozisyon Sayısı         : " + str(maxPozisyonSayisi) + "\n"
lastDebugMsg += "****************************************\n"
lastDebugMsg += "Pozisyon Ağırlıkları\n" 
lastDebugMsg += "Toplam İşlem Adet          : " + str(toplamIslemSayisi) + "\n"
lastDebugMsg += "1 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[1]) + "\tOran : %" + str(pozisyonAdetSayaci[1] / toplamIslemSayisi * 100) + "\n"
'''
lastDebugMsg += "2 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[2]) + "\t\tOran : %" + str(pozisyonAdetSayaci[2] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "3 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[3]) + "\t\tOran : %" + str(pozisyonAdetSayaci[3] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "4 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[4]) + "\t\tOran : %" + str(pozisyonAdetSayaci[4] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "5 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[5]) + "\t\tOran : %" + str(pozisyonAdetSayaci[5] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "6 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[6]) + "\t\tOran : %" + str(pozisyonAdetSayaci[6] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "7 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[7]) + "\t\tOran : %" + str(pozisyonAdetSayaci[7] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "8 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[8]) + "\t\tOran : %" + str(pozisyonAdetSayaci[8] / toplamIslemSayisi * 100) + "\n"
'''
lastDebugMsg += "****************************************\n"

print(lastDebugMsg)
logFileObject.write(lastDebugMsg)
logFileObject.close()