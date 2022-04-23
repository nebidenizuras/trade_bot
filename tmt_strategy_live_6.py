'''
- EMA'lar open hesaplanır. 2 Open 2 Close 34 Open hesaplanır
- EMA 2 Open > EMA 2 close ise ve EMA34 long ise long gir
- EMA 2 Open < EMA 2 close ise ve EMA34 short ise long gir
  8'i yukarı kırdığı anda eğer ema 3-5'de ema 8 üzeri ise stop ol, yoksa belirli kar al çık yeniden gir.
- GMT'de çalışır
'''

from operator import index
import array as arr
from binance.client import Client  
import pandas as pd 
from user_api_key import key_id, secret_key_id
import time   
from telegram_bot import send_message_TMT_TestNet2, warn
from datetime import datetime 
from datetime import timedelta
from ta.trend import ema_indicator

client = Client(key_id, secret_key_id) 

islemFiyatı = 0
hedefFiyatı = 0
islemBuyuklugu = 0

#ATTRIBUTES
kaldirac = 1
feeOranı = 0.0004 # percent
karOrani = 0.0033 # percent

baslangicPara = 111
cuzdan = baslangicPara

islemFee = 0
islemKar = 0

toplamFee = 0
toplamKar = 0

position = ""
start = False
startTime = 0
stopTime = 0
islemBitti = False

# Sinyal Değerleri
emaBuy = 2
emaSell = 2
emaSignal = 34

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

# Parite Bilgileri
symbol = "MTLUSDT"
interval = "15m"
limit = emaSignal + 10

df = ['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
      'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
      'taker_buy_quote_asset_volume', 'ignore']


startMsg = warn + warn + warn + "\n"
startMsg += "TMT Robot Çalışmaya Başladı\n"
startMsg += "Parite : " + symbol + "\nZaman Dilimi : " + interval + "\n"
startMsg += "Strateji -> EMA" + str(emaBuy) +  " Open / EMA" + str(emaSell) + " Close / EMA" + str(emaSignal) + " Open\n"
startMsg += "Başlangıç Para($)\t: " + str(baslangicPara) + "\n"
startMsg += "Hedef Kar Oranı\t\t: % " + str(karOrani * 100) + "\n"
startMsg += warn + warn + warn
send_message_TMT_TestNet2(startMsg)
time.sleep(1)

while(True):
    long_signal = False 
    short_signal = False
    islemBitti = False
    limit = emaSignal + 2
    candles = client.futures_klines(symbol=symbol, interval=interval, limit=limit) 
    df = pd.DataFrame(candles, columns=['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
                                        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                                        'taker_buy_quote_asset_volume', 'ignore']) 
    ## Clean data 
    df = df[['openTime', 'open', 'high', 'low', 'close', 'closeTime']]       
    df['open'] = df['open'].astype('float')
    df['close'] = df['close'].astype('float')
    df['high'] = df['high'].astype('float')
    df['low'] = df['low'].astype('float')
    df["openTime"] = pd.to_datetime(df["openTime"],unit= "ms") + timedelta(hours=3)
    df["closeTime"] = pd.to_datetime(df["closeTime"],unit= "ms") + timedelta(hours=3)
    df["EMABUY"] = ema_indicator(df["close"],emaBuy)
    df["EMASELL"] = ema_indicator(df["open"],emaSell)
    df["EMASIGNAL"] = ema_indicator(df["open"],emaSignal)     

    long_signal = (df["EMABUY"][limit-1] > df["EMASELL"][limit-1]) and (df["EMABUY"][limit-1] > df["EMASIGNAL"][limit-1]) and (df["EMASELL"][limit-1] > df["EMASIGNAL"][limit-1]) #and (df["close"][limit-1] >= df["EMASIGNAL"][limit-1])
    short_signal = (df["EMABUY"][limit-1] < df["EMASELL"][limit-1]) and (df["EMABUY"][limit-1] < df["EMASIGNAL"][limit-1]) and (df["EMASELL"][limit-1] < df["EMASIGNAL"][limit-1]) #and (df["close"][limit-1] <= df["EMASIGNAL"][limit-1])       

    ### Giriş Bilgilerini Ayarla
    if start == False and (position == "") and (long_signal or short_signal):        
        startTime =  df["openTime"][limit-1]
        debugMsg = ""
        debugMsg += "---------------------------------------\n" 
        debugMsg += "Sinyal Oluştu -> " + str(symbol) + " " + str(interval) + "\n"
        debugMsg += str(toplamIslemSayisi + 1) + ". İşlem Sinyali : "
        if long_signal:
            debugMsg += "LONG\n"
        elif short_signal:
            debugMsg += "SHORT\n"
        debugMsg += "\n"
        debugMsg += "EMA(" + str(emaBuy) + ") -> " + str(df["EMABUY"][limit-1]) + "\n" 
        debugMsg += "EMA(" + str(emaSell) + ") -> " + str(df["EMASELL"][limit-1]) + "\n"
        debugMsg += "EMA(" + str(emaSignal) + ") -> " + str(df["EMASIGNAL"][limit-1]) + "\n"
        debugMsg += "\n"  

### LONG İŞLEM ###
    # Long İşlem Aç
    if start == False and position == "" and long_signal:
        start = True
        toplamIslemSayisi = toplamIslemSayisi + 1
        islemFee = cuzdan * feeOranı * kaldirac
        toplamFee += islemFee
        position = "Long"    
        islemFiyatı = df["close"][limit-1]
        hedefFiyatı = islemFiyatı * (1 + karOrani)
        islemBuyuklugu = cuzdan * kaldirac
        debugMsg += "İşlem Giriş Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Giriş Fiyatı\t: " + str(islemFiyatı) + "\n"
        debugMsg += "İşlem Hedef Fiyatı\t: " + str(hedefFiyatı) + "\n"
        debugMsg += "İşlem Büyüklüğü ($)\t: " + str(islemBuyuklugu) + "\n"
        debugMsg += "İşlem Giriş Fee ($)\t: " + str(islemFee) + "\n"
        send_message_TMT_TestNet2(debugMsg)
        debugMsg = ""  

    # Long İşlem Kar Al
    if start == True and (position == "Long") and (df["close"][limit-1] >= hedefFiyatı):
        islemKar = cuzdan * karOrani * kaldirac
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOranı * kaldirac
        toplamFee += islemFee

        debugMsg += warn + " LONG İşlem Kar İle Kapandı.\n"
        debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Kar Al Fiyatı\t: " + str(hedefFiyatı) + "\n"
        debugMsg += "İşlem Çıkış Fee ($)\t: " + str(islemFee) + "\n" 
        debugMsg += "İşlem Kar ($)\t\t: " + str(islemKar) + "\n"
        debugMsg += "---------------------------------------\n"          

        islemBitti = True
        toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

    # Long İşlem Stop Ol
    if start and (position == "Long") and df["close"][limit-1] <= df["EMASIGNAL"][limit-1]:
        hedefFiyatı = df["close"][limit-1]

        islemKar = cuzdan * (((hedefFiyatı - islemFiyatı) / islemFiyatı)) * kaldirac
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOranı * kaldirac
        toplamFee += islemFee

        debugMsg += warn + " LONG İşlem Stop Oldu.\n"
        debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Stop Fiyatı\t: " + str(hedefFiyatı) + "\n"
        debugMsg += "İşlem Çıkış Fee ($)\t: " + str(islemFee) + "\n" 
        debugMsg += "İşlem Kar ($)\t\t: " + str(islemKar) + "\n"   
        debugMsg += "---------------------------------------\n"          

        islemBitti = True
        toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

# SHORT İŞLEM
    # Short İşlem Aç
    if start == False and position == "" and short_signal:
        start = True
        toplamIslemSayisi = toplamIslemSayisi + 1
        islemFee = cuzdan * feeOranı * kaldirac
        toplamFee += islemFee
        position = "Short"    
        islemFiyatı = df["close"][limit-1]
        hedefFiyatı = islemFiyatı * (1 - karOrani)
        islemBuyuklugu = cuzdan * kaldirac
        debugMsg += "İşlem Giriş Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Giriş Fiyatı\t: " + str(islemFiyatı) + "\n"
        debugMsg += "İşlem Hedef Fiyatı\t: " + str(hedefFiyatı) + "\n"
        debugMsg += "İşlem Büyüklüğü ($)\t: " + str(islemBuyuklugu) + "\n"
        debugMsg += "İşlem Giriş Fee ($)\t: " + str(islemFee) + "\n"
        send_message_TMT_TestNet2(debugMsg)
        debugMsg = ""  

    # Short İşlem Kar Al
    if start == True and (position == "Short") and (df["close"][limit-1] <= hedefFiyatı):
        islemKar = cuzdan * karOrani * kaldirac
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOranı * kaldirac
        toplamFee += islemFee

        debugMsg += warn + " SHORT İşlem Kar İle Kapandı.\n"
        debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Kar Al Fiyatı\t: " + str(hedefFiyatı) + "\n"
        debugMsg += "İşlem Çıkış Fee ($)\t: " + str(islemFee) + "\n" 
        debugMsg += "İşlem Kar ($)\t\t: " + str(islemKar) + "\n"         
        debugMsg += "---------------------------------------\n"          

        islemBitti = True 
        toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

    # Short İşlem Stop Ol
    if start and (position == "Short") and df["close"][limit-1] >= df["EMASIGNAL"][limit-1]:
        hedefFiyatı = df["close"][limit-1]

        islemKar = cuzdan * (((islemFiyatı - hedefFiyatı) / islemFiyatı)) * kaldirac
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOranı * kaldirac
        toplamFee += islemFee

        debugMsg += warn + " SHORT İşlem Stop Oldu.\n"
        debugMsg += "İşlem Çıkış Zamanı\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "İşlem Stop Fiyatı\t: " + str(hedefFiyatı) + "\n"
        debugMsg += "İşlem Çıkış Fee ($)\t: " + str(islemFee) + "\n" 
        debugMsg += "İşlem Kar ($)\t\t: " + str(islemKar) + "\n"         
        debugMsg += "---------------------------------------\n"          

        islemBitti = True
        toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

    if (cuzdan + 10) < toplamFee:
        debugMsg = warn + warn + warn + "\nCüzdanda Para Kalmadı\n" + warn + warn + warn
        send_message_TMT_TestNet2(debugMsg)
        debugMsg = "" 
        quit()   
     
    if islemBitti == True:     
        debugMsg += "\n"
        debugMsg += "****************************************\n"
        debugMsg += "GENEL ÖZET\n"
        debugMsg += "Parite : " + symbol + "\nZaman Dilimi : " + interval + "\n"
        debugMsg += "Strateji -> EMA" + str(emaBuy) +  " Open / EMA" + str(emaSell) + " Close / EMA" + str(emaSignal) + " Open\n"
        debugMsg += "Başlangıç Para($)\t: " + str(baslangicPara) + "\n"
        debugMsg += "Kar($)\t\t\t: " + str(cuzdan - baslangicPara) + "\n"
        debugMsg += "Toplam Ödenen Fee($)\t: " + str(toplamFee) + "\n"
        debugMsg += "Son Para($)\t\t: " + str(cuzdan - toplamFee) + "\n"
        debugMsg += "Kazanç\t\t\t: % " + str(((cuzdan - baslangicPara - toplamFee) / baslangicPara) * 100) + "\n"
        debugMsg += "Kaldıraç\t\t: " + str(kaldirac) + "x\n"
        debugMsg += "Hedef Kar Oranı\t: % " + str(karOrani * 100) + "\n"
        debugMsg += "Toplam İşlem Adet\t: " + str(toplamIslemSayisi) + "\n"
        debugMsg += "Karlı İşlem Adet\t: " + str(toplamKarliIslemSayisi) + "\n"
        debugMsg += "Stop İşlem Adet\t\t: " + str(toplamZararKesIslemSayisi) + "\n"
        debugMsg += "Kar Başarı Oranı\t: % " + str((toplamKarliIslemSayisi / toplamIslemSayisi) * 100) + "\n"
        debugMsg += "Zarar Kes Oranı\t\t: % " + str((toplamZararKesIslemSayisi / toplamIslemSayisi) * 100) + "\n"
        debugMsg += "****************************************\n"
        send_message_TMT_TestNet2(debugMsg)
        debugMsg = "" 
              
        islemBitti = False
        position = ""   
        start = False         
        islemKar = 0
        islemFee = 0
        islemFiyatı = 0
        hedefFiyatı = 0

    time.sleep(1) 