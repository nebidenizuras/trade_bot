'''
- Bu stratejide işleme giriş bandı Fibonacci kanalına göre belirlenmektedir.
- EMA8 değeri FIB 0.5 üzerinde ise, long işleme değmişsem long girerim (FIB 0.572)
  FIB 0.772 de kar alırım
- EMA8 değeri FIB 0.5 altında ise, short işleme değmişsem short girerim (FIB 0.428)
  FIB 0.228 de kar alırım
'''


from Indicators.fibonacci_retracement import calculate_fib
from operator import index
import array as arr
from binance.client import Client  
import pandas as pd 
from user_api_key import key_id, secret_key_id
import time   
from telegram_bot import send_message_TMT_TestNet1, warn
from datetime import datetime 
from datetime import timedelta
from ta.trend import ema_indicator

client = Client(key_id, secret_key_id) 

islemFiyati = 0
hedefFiyati = 0
stopFiyati = 0

#ATTRIBUTES
kaldirac = 1
feeOrani = 0.0004 # percent
bantMinimumOran = 0.002

baslangicPara = 111
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
karOrani = 0

islemFiyati = 0
hedefFiyati = 0
stopFiyati = 0

islemFee = 0
toplamFee = 0

islemKar = 0
toplamKar = 0

position = ""
start = False
startTime = 0
stopTime = 0
islemBitti = False

# Sinyal Değerleri
fibVal = 8
emaVal = 8

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

# Parite Bilgileri
timeFrame = 15
symbol = "APEUSDT"
interval = "15m"
limit = fibVal + 2

df = ['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
      'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
      'taker_buy_quote_asset_volume', 'ignore']


startMsg = warn + warn + warn + "\n"
startMsg += "TMT Robot Çalışmaya Başladı\n"
startMsg += "Parite : " + symbol + "\nZaman Dilimi : " + interval + "\n"
startMsg += "Strateji -> EMA" + str(emaVal) +  " Close / Fib " + str(fibVal) + "\n"
startMsg += "Başlangıç Para($)\t: " + str(baslangicPara) + "\n"
startMsg += warn + warn + warn
send_message_TMT_TestNet1(startMsg)
time.sleep(1)

while(True):
    if (position == ""):
        start = False
        long_signal = False 
        short_signal = False
        limit = fibVal + 2
        candles = client.futures_klines(symbol=symbol, interval=interval, limit=limit) 
        df = pd.DataFrame(candles, columns=['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
                                            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                                            'taker_buy_quote_asset_volume', 'ignore']) 
        ## Clean data 
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

        bantReferans = (((df["FIB_1"][limit-1] / df["FIB_0"][limit-1]) - 1) / 7)
        if (bantReferans >= bantMinimumOran):
            long_signal = df["EMA"][limit-1] > df["FIB_0_500"][limit-1]   
            short_signal = df["EMA"][limit-1] < df["FIB_0_500"][limit-1]

    if (start == True):
        limit = fibVal + 2
        candles = client.futures_klines(symbol=symbol, interval=interval, limit=limit) 
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

    ### Bandı ve Giriş Bilgilerini Ayarla
    if (position == "") and (long_signal or short_signal):

        bantReferans = (((df["FIB_1"][limit-1] / df["FIB_0"][limit-1]) - 1) / 7)

        if (bantReferans >= bantMinimumOran):
            start = True
            startTime =  df["openTime"][limit-1]

            shortStopFiyat = df["FIB_1"][limit-1]
            longKarFiyat = df["FIB_0_772"][limit-1]
            longGirisFiyat = df["FIB_0_572"][limit-1]
            referansOrtaFiyat = df["FIB_0_500"][limit-1]                 
            shortGirisFiyat = df["FIB_0_428"][limit-1]           
            shortKarFiyat = df["FIB_0_228"][limit-1]
            longStopFiyat = df["FIB_0"][limit-1]   

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
            debugMsg += "FIB_1_000 : " + str(df["FIB_1"][limit-1]) + "\n"
            debugMsg += "FIB_0_500 : " + str(df["FIB_0_500"][limit-1]) + "\n"
            debugMsg += "FIB_0_000 : " + str(df["FIB_0"][limit-1]) + "\n"    
            debugMsg += "\n"
            debugMsg += "EMA(" + str(emaVal) + ") -> " + str(df["EMA"][limit-1]) + "\n" 
            debugMsg += "\n" 
        else:
            start = False 

### LONG İŞLEM ###
    # LONG İşlem Aç
    if start and (df["high"][limit-1] >= longGirisFiyat and longGirisFiyat >= df["low"][limit-1]) and position == "" and long_signal:
        islemBitti = False
        toplamIslemSayisi = toplamIslemSayisi + 1
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee
        position = "Long"  
        islemFiyati = longGirisFiyat
        hedefFiyati = longKarFiyat
        stopFiyati = longStopFiyat
        karOrani = (longKarFiyat / longGirisFiyat) - 1 
        debugMsg += "İşlem Giriş Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Giriş Fiyatı\t: " + str(islemFiyati) + "\n"
        debugMsg += "İşlem Hedef Fiyatı\t: " + str(hedefFiyati) + "\n"
        debugMsg += "İşlem Büyüklüğü ($)\t: " + str(cuzdan * kaldirac) + "\n"
        debugMsg += "İşlem Giriş Fee ($)\t: " + str(islemFee) + "\n"
        send_message_TMT_TestNet1(debugMsg)
        debugMsg = ""  

    # LONG İşlem Kar Al
    if start and (position == "Long") and (df["high"][limit-1] >= hedefFiyati and hedefFiyati >= df["low"][limit-1]):
        islemKar = cuzdan * karOrani * kaldirac
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee

        debugMsg += warn + " LONG İşlem Kar İle Kapandı.\n"
        debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Kar Al Fiyatı\t: " + str(hedefFiyati) + "\n"
        debugMsg += "İşlem Çıkış Fee ($)\t: " + str(islemFee) + "\n" 
        debugMsg += "İşlem Kar ($)\t\t: " + str(islemKar) + "\n"
        debugMsg += "---------------------------------------\n"          

        islemBitti = True
        start = False
        toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

    # LONG İşlem Stop Ol
    if start and (position == "Long") and (df["high"][limit-1] >= stopFiyati and stopFiyati >= df["low"][limit-1]):
        islemKar = cuzdan * (((stopFiyati - islemFiyati) / islemFiyati)) * kaldirac
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee

        debugMsg += warn + " LONG İşlem Stop Oldu.\n"
        debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Stop Fiyatı\t: " + str(stopFiyati) + "\n"
        debugMsg += "İşlem Çıkış Fee ($)\t: " + str(islemFee) + "\n" 
        debugMsg += "İşlem Kar ($)\t\t: " + str(islemKar) + "\n"   
        debugMsg += "---------------------------------------\n"          

        islemBitti = True
        start = False
        toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

### SHORT İŞLEM ###
    # SHORT İşlem Aç
    if start and (df["low"][limit-1] <= shortGirisFiyat and shortGirisFiyat <= df["high"][limit-1]) and position == "" and short_signal:
        islemBitti = False
        toplamIslemSayisi = toplamIslemSayisi + 1
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee
        position = "Short"  
        islemFiyati = shortGirisFiyat
        hedefFiyati = shortKarFiyat
        stopFiyati = shortStopFiyat
        karOrani = (shortGirisFiyat / shortKarFiyat) - 1 
        debugMsg += "İşlem Giriş Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Giriş Fiyatı\t: " + str(islemFiyati) + "\n"
        debugMsg += "İşlem Hedef Fiyatı\t: " + str(hedefFiyati) + "\n"
        debugMsg += "İşlem Büyüklüğü ($)\t: " + str(cuzdan * kaldirac) + "\n"
        debugMsg += "İşlem Giriş Fee ($)\t: " + str(islemFee) + "\n"
        send_message_TMT_TestNet1(debugMsg)
        debugMsg = ""  

    # SHORT İşlem Kar Al
    if start and (position == "Short") and (df["low"][limit-1] <= hedefFiyati and hedefFiyati <= df["high"][limit-1]):
        islemKar = cuzdan * karOrani * kaldirac
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee

        debugMsg += warn + " LONG İşlem Kar İle Kapandı.\n"
        debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Kar Al Fiyatı\t: " + str(hedefFiyati) + "\n"
        debugMsg += "İşlem Çıkış Fee ($)\t: " + str(islemFee) + "\n" 
        debugMsg += "İşlem Kar ($)\t\t: " + str(islemKar) + "\n"
        debugMsg += "---------------------------------------\n"          

        islemBitti = True
        start = False
        toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

    # SHORT İşlem Stop Ol
    if start and (position == "Short") and (df["low"][limit-1] <= stopFiyati and stopFiyati <= df["high"][limit-1]):
        islemKar = cuzdan * (((islemFiyati - stopFiyati) / islemFiyati)) * kaldirac
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee

        debugMsg += warn + " LONG İşlem Stop Oldu.\n"
        debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Stop Fiyatı\t: " + str(stopFiyati) + "\n"
        debugMsg += "İşlem Çıkış Fee ($)\t: " + str(islemFee) + "\n" 
        debugMsg += "İşlem Kar ($)\t\t: " + str(islemKar) + "\n"   
        debugMsg += "---------------------------------------\n"          

        islemBitti = True
        start = False
        toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

    if (cuzdan + 10) < toplamFee:
        debugMsg = warn + warn + warn + "\nCüzdanda Para Kalmadı\n" + warn + warn + warn
        send_message_TMT_TestNet1(debugMsg)
        debugMsg = "" 
        quit()   
     
    if islemBitti == True:     
        debugMsg += "\n"
        debugMsg += "****************************************\n"
        debugMsg += "GENEL ÖZET\n"
        debugMsg += "Parite : " + symbol + "\nZaman Dilimi : " + interval + "\n"
        debugMsg += "Strateji -> EMA" + str(emaVal) +  " Open / Fib " + str(fibVal) +"\n"
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
        send_message_TMT_TestNet1(debugMsg)
        debugMsg = "" 
              
        islemBitti = False
        position = ""   
        start = False         
        islemKar = 0
        islemFee = 0
        islemFiyati = 0
        hedefFiyati = 0

        while datetime.now().minute % timeFrame != 0: 
            time.sleep(3)

    time.sleep(1) 