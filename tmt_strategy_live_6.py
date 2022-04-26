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
from telegram_bot import *
from datetime import datetime 
from datetime import timedelta
from ta.trend import ema_indicator

client = Client(key_id, secret_key_id) 

islemFiyati = 0
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

position = ""
start = False
startTime = 0
stopTime = 0
islemBitti = False

# Sinyal Değerleri
emaBuy = 5     # 8 open
emaBuyType = "open"
emaSell = 13     # 2 close
emaSellType = "open"
emaSignal = 144 # 233 close
emaSignalType = "open"

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

# Parite Bilgileri
symbol = "MTLUSDT"
interval = "5m"
timeFrame = 5
limit = emaSignal * 2

df = ['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
      'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
      'taker_buy_quote_asset_volume', 'ignore']

while(True):
    long_signal = False 
    short_signal = False
    islemBitti = False
    limit = emaSignal * 2
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
    df["EMABUY"] = ema_indicator(df[emaBuyType],emaBuy)
    df["EMASELL"] = ema_indicator(df[emaSellType],emaSell)
    df["EMASIGNAL"] = ema_indicator(df[emaSignalType],emaSignal)     

    long_signal = (df["EMABUY"][limit-1] > df["EMASELL"][limit-1]) and (df["EMABUY"][limit-1] > df["EMASIGNAL"][limit-1]) and (df["EMASELL"][limit-1] > df["EMASIGNAL"][limit-1]) #and (df["close"][limit-1] >= df["EMASIGNAL"][limit-1])
    short_signal = (df["EMABUY"][limit-1] < df["EMASELL"][limit-1]) and (df["EMABUY"][limit-1] < df["EMASIGNAL"][limit-1]) and (df["EMASELL"][limit-1] < df["EMASIGNAL"][limit-1]) #and (df["close"][limit-1] <= df["EMASIGNAL"][limit-1])       

    ### Giriş Bilgilerini Ayarla
    if start == False and (position == "") and (long_signal or short_signal):        
        startTime =  df["openTime"][limit-1]
        debugMsg = ""
        debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
        debugMsg += warn + str(toplamIslemSayisi + 1) + ". Signal "
        if long_signal:
            debugMsg += "LONG\n"
        elif short_signal:
            debugMsg += "SHORT\n"
        debugMsg += "\n"

### LONG İŞLEM ###
    # Long İşlem Aç
    if start == False and position == "" and long_signal:
        start = True
        toplamIslemSayisi = toplamIslemSayisi + 1
        islemFee = cuzdan * feeOranı * kaldirac
        toplamFee += islemFee
        position = "Long"    
        islemFiyati = df["close"][limit-1]
        hedefFiyati = islemFiyati * (1 + karOrani)
        islemBuyuklugu = cuzdan * kaldirac

        debugMsg += "Order Time\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "LONG Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t: " + str(round(islemFee,4)) + "\n"
        debugMsg += "\n" 
        debugMsg += "\n"
        debugMsg += "Reference Bands\n" 
        debugMsg += "EMA(" + str(emaBuy) + ") -> " + str(round(df["EMABUY"][limit-1],4)) + "\n" 
        debugMsg += "EMA(" + str(emaSell) + ") -> " + str(round(df["EMASELL"][limit-1],4)) + "\n"
        debugMsg += "EMA(" + str(emaSignal) + ") -> " + str(round(df["EMASIGNAL"][limit-1],4)) + "\n"
        debugMsg += "\n"  
        send_message_to_telegram(channelAlbiz, debugMsg)
        debugMsg = ""  

    # Long İşlem Kar Al
    if start == True and (position == "Long") and (df["close"][limit-1] >= hedefFiyati):
        islemKar = cuzdan * karOrani * kaldirac
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOranı * kaldirac
        toplamFee += islemFee

        debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
        debugMsg += warn + str(toplamIslemSayisi) + " Signal LONG Close Take Profit \n"
        debugMsg += "\n"
        debugMsg += "Order Time\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "LONG Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
        debugMsg += "Order Profit\t: % " + str(round(karOrani * 100,3)) + "\n"
      
        islemBitti = True
        toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

    # Long İşlem Stop Ol
    if start and (position == "Long") and df["close"][limit-1] <= df["EMASIGNAL"][limit-1]:
        hedefFiyati = df["close"][limit-1]        
        islemKar = cuzdan * (((hedefFiyati - islemFiyati) / islemFiyati)) * kaldirac
        zararOran = islemKar / cuzdan
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOranı * kaldirac
        toplamFee += islemFee

        debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
        debugMsg += warn + str(toplamIslemSayisi) + " Signal LONG Close Stop Loss\n"
        debugMsg += "\n"
        debugMsg += "Order Time\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "LONG Order SL\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
        debugMsg += "Order Profit\t: % -" + str(round(zararOran * 100,3)) + "\n" 

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
        islemFiyati = df["close"][limit-1]
        hedefFiyati = islemFiyati * (1 - karOrani)
        islemBuyuklugu = cuzdan * kaldirac
        debugMsg += "Order Time\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "SHORT Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t: " + str(round(islemFee,4)) + "\n"
        debugMsg += "\n" 
        debugMsg += "\n"
        debugMsg += "Reference Bands\n" 
        debugMsg += "EMA(" + str(emaBuy) + ") -> " + str(round(df["EMABUY"][limit-1],4)) + "\n" 
        debugMsg += "EMA(" + str(emaSell) + ") -> " + str(round(df["EMASELL"][limit-1],4)) + "\n"
        debugMsg += "EMA(" + str(emaSignal) + ") -> " + str(round(df["EMASIGNAL"][limit-1],4)) + "\n"
        debugMsg += "\n"  
        send_message_to_telegram(channelAlbiz, debugMsg)
        debugMsg = ""  

    # Short İşlem Kar Al
    if start == True and (position == "Short") and (df["close"][limit-1] <= hedefFiyati):
        islemKar = cuzdan * karOrani * kaldirac
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOranı * kaldirac
        toplamFee += islemFee

        debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
        debugMsg += warn + str(toplamIslemSayisi) + " Signal SHORT Close Take Profit \n"
        debugMsg += "\n"
        debugMsg += "Order Time\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "SHORT Order TP\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
        debugMsg += "Order Profit\t: % " + str(round(karOrani * 100,3)) + "\n"     

        islemBitti = True 
        toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

    # Short İşlem Stop Ol
    if start and (position == "Short") and df["close"][limit-1] >= df["EMASIGNAL"][limit-1]:
        hedefFiyati = df["close"][limit-1]

        islemKar = cuzdan * (((islemFiyati - hedefFiyati) / islemFiyati)) * kaldirac
        zararOran = islemKar / cuzdan
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOranı * kaldirac
        toplamFee += islemFee

        debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
        debugMsg += warn + str(toplamIslemSayisi) + " Signal SHORT Close Stop Loss\n"
        debugMsg += "\n"
        debugMsg += "Order Time\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "SHORT Order SL\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t: " + str(round(islemFee,7)) + "\n"
        debugMsg += "Order Profit\t: % -" + str(round(zararOran * 100,3)) + "\n" 

        islemBitti = True
        toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

    if (cuzdan + 10) < toplamFee:
        debugMsg = warn + warn + warn + "\nCüzdanda Para Kalmadı\n" + warn + warn + warn
        send_message_to_telegram(channelAlbiz, debugMsg)
        debugMsg = "" 
        quit()   
     
    if islemBitti == True:  
        debugMsg += "\n"
        debugMsg += "Report\n"
        debugMsg += "\n"
        debugMsg += "Strategy : " + str(symbol) + " " + str(kaldirac) + " " + str(interval) + " EMA" + str(emaBuy) + " " + str(emaBuyType) + " EMA" + str(emaSell) + " " + str(emaSellType) + " EMA" + str(emaSignal) + " " + str(emaSignalType) + "\n"
        debugMsg += "Invest\t: " + str(round(baslangicPara,7)) + "\n"
        debugMsg += "ROI\t: " + str(round(toplamKar,7)) + "\n"
        debugMsg += "Total Fee\t: " + str(round(toplamFee,3)) + "\n"
        debugMsg += "Fund\t: " + str(round(cuzdan,7)) + "\n"
        debugMsg += "ROI\t: % " + str(round((toplamKar / baslangicPara) * 100,3)) + "\n"
        debugMsg += "\n"
        debugMsg += "Total Orders\t: " + str(toplamIslemSayisi) + "\n"
        debugMsg += "TP Orders\t: " + str(toplamKarliIslemSayisi) + "\n"
        debugMsg += "SL Orders\t\t: " + str(toplamZararKesIslemSayisi) + "\n"
        debugMsg += "Gain Orders\t: % " + str(round((toplamKarliIslemSayisi / toplamIslemSayisi) * 100,1)) + "\n"
        debugMsg += "Lose Orders\t\t: % " + str(round((toplamZararKesIslemSayisi / toplamIslemSayisi) * 100,1)) + "\n"        
        send_message_to_telegram(channelAlbiz, debugMsg)
        debugMsg = "" 
              
        islemBitti = False
        position = ""   
        start = False         
        islemKar = 0
        islemFee = 0
        islemFiyati = 0
        hedefFiyati = 0

    time.sleep(0.1) 