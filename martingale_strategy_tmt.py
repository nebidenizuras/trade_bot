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
katSayilarToplami = 1 # + 1 katsayı fee için
for i in range (maxPozisyonSayisi + 1):
    katSayilarToplami = katSayilarToplami + martingaleKatsayilar[i]

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
pozisyonAdetSayaci = arr.array('i', [0,0,0,0,0,0,0,0,0])

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

csvName = "Historical_Data/LUNAUSDT_15m.csv"
logFileName = "LogFile_" + "LUNAUSDT_15m" + ".txt"

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
df["EMA5"] = tb.ema(df["close"],5)
df["EMA8"] = tb.ema(df["close"],8)
calculate_fib(df,13)

print("Strategy Back Test is starting......")

for i in range(df.shape[0]):
    if i > 50:
        long_signal = df["EMA5"][i-2] > df["EMA8"][i-2]
        short_signal = df["EMA5"][i-2] < df["EMA8"][i-2]

        ### Bandı ve Giriş Bilgilerini Ayarla
        if (position == "") and (start == False) and (long_signal or short_signal):
            start = True
            referansOrtaFiyat = df["FIB_0_500"][i-2]
            startTime =  df["openTime"][i-2]
            altGirisFiyat = referansOrtaFiyat * (1 - girisOrani)
            ustGirisFiyat = referansOrtaFiyat * (1 + girisOrani)
            altCikisFiyat = altGirisFiyat * (1 - cikisOrani)
            ustCikisFiyat = ustGirisFiyat * (1 + cikisOrani)
            pozisyonBuyuklugu = cuzdan / katSayilarToplami

            debugMsg = ""
            debugMsg += "---------------------------------------\n" 
            debugMsg += str(toplamIslemSayisi) + ". İşlem Sinyali Geldi\n" 
            debugMsg += "Al-Sat Bant Aralığı\n"
            debugMsg += "Üst Çıkış           : " + str(ustCikisFiyat) + "\n"
            debugMsg += "Üst Giriş           : " + str(ustGirisFiyat) + "\n"
            debugMsg += "Referans Orta Fiyat : " + str(referansOrtaFiyat) + "\n"
            debugMsg += "Alt Çıkış           : " + str(altCikisFiyat) + "\n"
            debugMsg += "Alt Giriş           : " + str(altGirisFiyat) + "\n"
            debugMsg += "\n"  
            debugMsg += "FIB Değerleri -> FIB_1 : " + str(df["FIB_1"][i-2]) + ", FIB_0_500 : " + str(df["FIB_0_500"][i-2]) + ", FIB_0 : " + str(df["FIB_0"][i-2]) + "\n"    
            debugMsg += "EMA 5 -> " + str(df["EMA5"][i-2]) + ", EMA8 -> " + str(df["EMA8"][i-2]) + "\n"
            debugMsg += "\n"  

        if start and (df["high"][i-1] >= ustGirisFiyat) and islemSayisi < maxPozisyonSayisi and position != "Long" and long_signal: #long gir
            islemSayisi = islemSayisi + 1
            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * fee * kaldirac)
            islemSirasi[islemSayisi] = "Long"
            position = "Long"     
            debugMsg += str(islemSayisi) + ".Pozisyon " + str(position) + "\n"
            debugMsg += "İşlem Zamanı : " + str(df["openTime"][i-1]) + "\n"
            debugMsg += "İşlem Fiyatı : " + str(ustGirisFiyat) + "\n"
            debugMsg += "İşlem Büyüklüğü : " + str(pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * kaldirac) + "\n"
            debugMsg += "\n"  

        if start and (df["low"][i-1] <= altGirisFiyat) and islemSayisi < maxPozisyonSayisi and position != "Short" and short_signal: #short gir
            islemSayisi = islemSayisi + 1        
            cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * fee * kaldirac)
            islemSirasi[islemSayisi] = "Short"
            position = "Short"            
            debugMsg += str(islemSayisi) + ".Pozisyon : " + str(position) + "\n"
            debugMsg += "İşlem Zamanı : " + str(df["openTime"][i-1]) + "\n"
            debugMsg += "İşlem Fiyatı : " + str(altGirisFiyat) + "\n"
            debugMsg += "İşlem Büyüklüğü : " + str(pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * kaldirac) + "\n"
            debugMsg += "\n"  

        if start and (df["high"][i] >= ustCikisFiyat or df["low"][i] <= altCikisFiyat) and (position != ""): # tüm islemleri kapat
            kumulatifKar = 0.0 
            stopTime =  df["closeTime"][i]      
            pozisyonAdetSayaci[islemSayisi] = pozisyonAdetSayaci[islemSayisi] + 1

            if (df["high"][i] >= ustCikisFiyat): #Üst bantta kapatıyoruz

                debugMsg += "Long Yön İşlem Hedefi Geldi.Tüm İşlemler Üst Hedef Bantta Kapatılıyor.\n"
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

                debugMsg += "Short Yön İşlem Hedefi Geldi. Tüm İşlemler Alt Hedef Bantta Kapatılıyor.\n"
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
            debugMsg += "Başlangıç Zamanı    : " + str(startTime) + "\n"
            debugMsg += "Bitiş Zamanı        : " + str(stopTime) + "\n"
            debugMsg += "Toplam İşlem Sayısı : " + str(islemSayisi) + "\n"
            debugMsg += "İşlem Kazancı       : " + str(kumulatifKar) + "\n"
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
lastDebugMsg += "Strateji -> EMA 5 Close  / EMA 8 Close Signal\n" 
lastDebugMsg += "EMA 5 > EMA 8 = BUY -  EMA 5 < EMA 8 = SELL - Fibonacci 13\n"
lastDebugMsg += "İşleme Giriş Bant Genişliği  : % " + str(bantReferans*100) + "\n"
lastDebugMsg += "Başlangıç Para($)            : " + str(baslangicPara) + "\n"
lastDebugMsg += "Kar($)                       : " + str(cuzdan - baslangicPara) + "\n"
lastDebugMsg += "Son Para($)                  : " + str(cuzdan) + "\n"
lastDebugMsg += "Kazanç                       : % " + str(((cuzdan - baslangicPara) / baslangicPara) * 100) + "\n"
lastDebugMsg += "Kaldıraç                     : " + str(kaldirac) + "x\n"
lastDebugMsg += "Maks Pozisyon Sayısı         : " + str(maxPozisyonSayisi) + "\n"
lastDebugMsg += "****************************************\n"
lastDebugMsg += "Pozisyon Ağırlıkları\n" 
lastDebugMsg += "Toplam İşlem Adet          : " + str(toplamIslemSayisi) + "\n"
lastDebugMsg += "1 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[1]) + "\t Oran : %" + str(pozisyonAdetSayaci[1] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "2 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[2]) + "\t Oran : %" + str(pozisyonAdetSayaci[2] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "3 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[3]) + "\t Oran : %" + str(pozisyonAdetSayaci[3] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "4 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[4]) + "\t Oran : %" + str(pozisyonAdetSayaci[4] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "5 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[5]) + "\t Oran : %" + str(pozisyonAdetSayaci[5] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "6 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[6]) + "\t Oran : %" + str(pozisyonAdetSayaci[6] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "7 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[7]) + "\t Oran : %" + str(pozisyonAdetSayaci[7] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "8 Pozisyonla Kapanan İşlem : " + str(pozisyonAdetSayaci[8]) + "\t Oran : %" + str(pozisyonAdetSayaci[8] / toplamIslemSayisi * 100) + "\n"
lastDebugMsg += "****************************************\n"

print(lastDebugMsg)
logFileObject.write(lastDebugMsg)
logFileObject.close()