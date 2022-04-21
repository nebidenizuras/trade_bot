'''
Bu stratejide işleme giriş bandı Fibonacci kanalına göre belirlenmektedir.
'''

from operator import index
import pandas_ta as tb
import pandas as pd
from Indicators.fibonacci_retracement import calculate_fib
import array as arr
from binance.client import Client  
import pandas as pd 
import user_api_key 
import time   
from telegram_bot import send_message
from datetime import datetime 
from datetime import timedelta

client = Client(user_api_key.key_id,user_api_key.secret_key_id) 

kaldirac = 1
start = False

# Martingale Katsayılar
martingaleKatsayilar = [0, 1, 1.4, 1, 1.4, 1.9, 2.5, 3.3, 4.4] # 16,9 katsayı 
#martingaleKatsayilar = [0, 1, 2.33, 3.1, 4.15, 5.55, 7.4, 9.85, 13.1, 17.45, 23.3, 31.1, 41.45] # 12 Pozisyon Hiç Efektif Değil
maxPozisyonSayisi = 1
katSayilarToplami = 0.01 # + 1 katsayı fee için
for i in range (maxPozisyonSayisi + 1):
    katSayilarToplami = katSayilarToplami + martingaleKatsayilar[i]

pozisyonİslemFiyatları = 0
pozisyonBuyuklugu = 0
bantMinimumOran = 0.002
bantReferans = 0.002
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

fibPeriod = 5
emaBuy = 2
emaSell = 3

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
islemSayisi = 0

# Parite Bilgileri
timeFrame = 15
interval = '15m' 
limit = 10
symbol = "MTLUSDT"

df = ['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
      'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
      'taker_buy_quote_asset_volume', 'ignore']

while (1):
    if (position == ""):
        start = False
        long_signal = False 
        short_signal = False
        limit = 10
        candles = client.get_klines(symbol=symbol, interval=interval, limit=limit) 
        df = pd.DataFrame(candles, columns=['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
                                            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                                            'taker_buy_quote_asset_volume', 'ignore']) 
        ## Clean data 
        df = df[['openTime', 'open', 'high', 'low', 'close', 'closeTime']]       
        df['openTime'] = pd.to_datetime(df["openTime"], unit="ms") + timedelta(hours=3)
        df['closeTime'] = pd.to_datetime(df["closeTime"], unit="ms") + timedelta(hours=3)
        df['open'] = df['open'].astype('float') 
        df['close'] = df['close'].astype('float') 
        df['high'] = df['high'].astype('float') 
        df['low'] = df['low'].astype('float') 
        df["EMABUY"] = tb.ema(df["close"],emaBuy)
        df["EMASELL"] = tb.ema(df["close"],emaSell)        
        df["FIB_1"] = calculate_fib(df,fibPeriod, 1)
        df["FIB_0_500"] = calculate_fib(df,fibPeriod, 0.5)
        df["FIB_0"] = calculate_fib(df,fibPeriod, 0)  

        bantReferans = (((df["FIB_1"][limit-1] / df["FIB_0"][limit-1]) - 1) / 7)
        if (bantReferans >= bantMinimumOran):
            long_signal = df["EMABUY"][limit-1] > df["EMASELL"][limit-1]
            short_signal = df["EMABUY"][limit-1] < df["EMASELL"][limit-1]
 
    if (start == True):
        limit = 10
        candles = client.get_klines(symbol=symbol, interval=interval, limit=limit) 
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
        df["EMABUY"] = tb.ema(df["close"],emaBuy)
        df["EMASELL"] = tb.ema(df["close"],emaSell)

        long_signal = df["EMABUY"][limit-1] > df["EMASELL"][limit-1]
        short_signal = df["EMABUY"][limit-1] < df["EMASELL"][limit-1]

    ### Bandı ve Giriş Bilgilerini Ayarla
    if (position == "") and (start == False) and (long_signal or short_signal):
        start = True
        referansOrtaFiyat = df["FIB_0_500"][limit-1]
        startTime =  df["openTime"][limit-1]
        
        cikisOrani = 3 * bantReferans
        girisOrani = bantReferans / 2
        altGirisFiyat = referansOrtaFiyat * (1 + girisOrani)
        ustGirisFiyat = referansOrtaFiyat * (1 - girisOrani)
        altCikisFiyat = altGirisFiyat * (1 - cikisOrani)
        ustCikisFiyat = ustGirisFiyat * (1 + cikisOrani)
        pozisyonBuyuklugu = cuzdan / katSayilarToplami

        debugMsg = "Sinyal Oluştu ->\n" + str(symbol) + " " + str(interval) + "\n"
        debugMsg += "TERS İŞLEM\n"
        debugMsg += "Güncel Cüzdan($) : " + str(cuzdan) + "\n" 
        debugMsg += "---------------------------------------\n" 
        debugMsg += str(toplamIslemSayisi + 1) + ". İşlem Sinyali Geldi\n" 
        debugMsg += str(startTime) + "\n"
        debugMsg += "Al-Sat Bant Aralığı\n"
        debugMsg += "İşlem Aralığı\t: % " + str(bantReferans * 100) + "\n"
        debugMsg += "Üst Çıkış\t: " + str(ustCikisFiyat) + "\n"
        debugMsg += "Üst Giriş\t: " + str(ustGirisFiyat) + "\n"
        debugMsg += "Orta Fiyat\t: " + str(referansOrtaFiyat) + "\n"
        debugMsg += "Alt Giriş\t: " + str(altGirisFiyat) + "\n"
        debugMsg += "Alt Çıkış\t: " + str(altCikisFiyat) + "\n"
        debugMsg += "\n"  
        debugMsg += "FIB Değerleri -> \n"
        debugMsg += "FIB_1.000 : " + str(df["FIB_1"][limit-1]) + "\n"
        debugMsg += "FIB_0.500 : " + str(df["FIB_0_500"][limit-1]) + "\n"
        debugMsg += "FIB_0.000 : " + str(df["FIB_0"][limit-1]) + "\n"    
        debugMsg += "\n" 
        debugMsg += "EMA(" + str(emaBuy) + ") -> " + str(df["EMABUY"][limit-1]) + "\n" 
        debugMsg += "EMA(" + str(emaSell) + ") -> " + str(df["EMASELL"][limit-1]) + "\n" 
        debugMsg += "\n"  

    if start and (df["high"][limit-1] >= ustGirisFiyat and ustGirisFiyat >= df["low"][limit-1]) and islemSayisi < maxPozisyonSayisi and position != "Long" and long_signal: #long gir
        islemSayisi = islemSayisi + 1
        cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * fee * kaldirac)
        islemSirasi[islemSayisi] = "Long"
        position = "Long"     
        debugMsg += str(islemSayisi) + ".Pozisyon " + str(position) + "\n"
        debugMsg += "İşlem Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Fiyatı\t: " + str(ustGirisFiyat) + "\n"
        debugMsg += "İşlem Büyüklüğü\t: " + str(pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * kaldirac) + "\n"
        debugMsg += "\n"  
        send_message(debugMsg)
        debugMsg = ""

    if start and (df["low"][limit-1] <= altGirisFiyat and altGirisFiyat <= df["high"][limit-1]) and islemSayisi < maxPozisyonSayisi and position != "Short" and short_signal: #short gir
        islemSayisi = islemSayisi + 1        
        cuzdan = cuzdan - (pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * fee * kaldirac)
        islemSirasi[islemSayisi] = "Short"
        position = "Short"            
        debugMsg += str(islemSayisi) + ".Pozisyon : " + str(position) + "\n"
        debugMsg += "İşlem Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Fiyatı\t: " + str(altGirisFiyat) + "\n"
        debugMsg += "İşlem Büyüklüğü\t: " + str(pozisyonBuyuklugu * martingaleKatsayilar[islemSayisi] * kaldirac) + "\n"
        debugMsg += "\n"  
        send_message(debugMsg)
        debugMsg = ""

    if start and (df["high"][limit-1] >= ustCikisFiyat or df["low"][limit-1] <= altCikisFiyat) and (position != ""): # tüm islemleri kapat
        kumulatifKar = 0.0 
        stopTime =  df["closeTime"][limit-1]      
        pozisyonAdetSayaci[islemSayisi] = pozisyonAdetSayaci[islemSayisi] + 1

        if (df["high"][limit-1] >= ustCikisFiyat): #Üst bantta kapatıyoruz
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

        elif (df["low"][limit-1] <= altCikisFiyat): #Alt bantta kapatıyoruz
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
        
        if (kumulatifKar > 0):
            toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

        cuzdan = cuzdan + kumulatifKar   

        debugMsg += "\n"
        debugMsg += "Başlangıç Mum Zamanı\t: " + str(startTime) + "\n"
        debugMsg += "Bitiş Mum Zamanı\t\t: " + str(stopTime) + "\n"
        debugMsg += "Toplam İşlem Sayısı\t\t: " + str(islemSayisi) + "\n"
        debugMsg += "İşlem Kazancı\t\t: " + str(kumulatifKar) + "\n"
        debugMsg += "---------------------------------------\n"           
        debugMsg += "\n"

        start = False     
        position = ""
        islemSayisi = 0
        toplamIslemSayisi = toplamIslemSayisi + 1

        if cuzdan < 10:
            debugMsg += "Kasa Bitti, İşlemler Durdu"
            send_message(debugMsg)
            debugMsg = ""
            quit()   
     
        debugMsg += "\n"
        debugMsg += "****************************************\n"
        debugMsg += "TERS İŞLEM\n"
        debugMsg += "Parite : " + symbol + "\nZaman Dilimi : " + interval + "\n"
        debugMsg += "Strateji -> EMA" + str(emaBuy) +  " Close / EMA" + str(emaSell) + " Close Signal\n" 
        debugMsg += "Fibonacci -> " + str(fibPeriod) + "\n"
        debugMsg += "İşlem Bandı Minimum\t: % " + str(bantMinimumOran * 100) + "\n"
        debugMsg += "Başlangıç Para($)\t: " + str(baslangicPara) + "\n"
        debugMsg += "Kar($)\t\t\t: " + str(cuzdan - baslangicPara) + "\n"
        debugMsg += "Son Para($)\t\t: " + str(cuzdan) + "\n"
        debugMsg += "Kazanç\t\t\t: % " + str(((cuzdan - baslangicPara) / baslangicPara) * 100) + "\n"
        debugMsg += "Kaldıraç\t\t: " + str(kaldirac) + "x\n"
        debugMsg += "Maks Pozisyon Sayısı\t: " + str(maxPozisyonSayisi) + "\n"
        debugMsg += "****************************************\n"
        debugMsg += "Pozisyon Ağırlıkları\n" 
        debugMsg += "Toplam İşlem Adet\t\t: " + str(toplamIslemSayisi) + "\n"
        debugMsg += "Karlı İşlem Adet\t\t\t: " + str(toplamKarliIslemSayisi) + "\n"
        debugMsg += "Kar Başarı Oranı\t\t: % " + str((toplamKarliIslemSayisi / toplamIslemSayisi) * 100) + "\n"
        for i in range(maxPozisyonSayisi):
            debugMsg += str(i+1) + " Pozisyonla Kapanan İşlem\t: " + str(pozisyonAdetSayaci[i+1]) + "\tOran : % " + str(pozisyonAdetSayaci[i+1] / toplamIslemSayisi * 100) + "\n"
        debugMsg += "****************************************\n"
        send_message(debugMsg)
        debugMsg = ""

        # Aynı mum içinde tekrar tekrar işlem yapmasın diye bir sonraki mum açılışını bekle
        # Wait 1 second until we are synced up with the 'every 15 minutes' clock            
        #while datetime.now().minute not in {0, 15, 30, 45}: 
        while datetime.now().minute % timeFrame != 0: 
            time.sleep(10)

    time.sleep(10)   