'''
- EMA'lar open hesaplanır. 2 Open 2 Close 34 Open hesaplanır
- EMA 2 Open > EMA 2 close ise ve EMA34 long ise long gir
- EMA 2 Open < EMA 2 close ise ve EMA34 short ise long gir
  8'i yukarı kırdığı anda eğer ema 3-5'de ema 8 üzeri ise stop ol, yoksa belirli kar al çık yeniden gir.
- GMT'de çalışır
'''
from datetime import datetime   
from datetime import timedelta
from time import sleep    

from binance.client import Client  
from user_api_key import key_id, secret_key_id

import pandas as pd 

from telegram_bot import warn, send_message_to_telegram, channelAlbiz

from ta.trend import ema_indicator

client = Client(key_id, secret_key_id) 

islemFiyati = 0
hedefFiyati = 0
islemBuyuklugu = 0

#ATTRIBUTES
kaldirac = 1
feeOrani = 0.0004 # percent
karOrani = 0.0022 # percent

baslangicPara = 111
cuzdan = baslangicPara

islemFee = 0
islemKar = 0

toplamFee = 0
toplamKar = 0

startTime = 0
stopTime = 0

position = ""
start = False
islemBitti = False

emaBuyPrice = 0.0
emaSellPrice = 0.0
emaSignalPrice = 0.0
currentPrice = 0.0

IsEMAUpdate = False

long_signal = False
short_signal = False

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
symbol = "APEUSDT"
interval = "5m"
timeFrame = 5
limit = emaSignal * 2

df = ['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
      'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
      'taker_buy_quote_asset_volume', 'ignore']

def signal_update():
    global emaBuyPrice
    global emaSellPrice
    global emaSignalPrice
    global currentPrice
    global long_signal
    global short_signal
    global IsEMAUpdate

    IsEMAUpdate = True
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

    emaBuyPrice = df["EMABUY"][limit-1]
    emaSellPrice = df["EMASELL"][limit-1]
    emaSignalPrice = df["EMASIGNAL"][limit-1]
    currentPrice = df["close"][limit-1]

    long_signal = (emaBuyPrice > emaSellPrice) and (emaBuyPrice > emaSignalPrice) and (emaSellPrice > emaSignalPrice) #and (currentPrice >= emaSignalPrice)
    short_signal = (emaBuyPrice < emaSellPrice) and (emaBuyPrice < emaSignalPrice) and (emaSellPrice < emaSignalPrice) #and (currentPrice <= emaSignalPrice)       

signal_update()

while(True):
    if(IsEMAUpdate == False) and (datetime.now().minute % timeFrame == 0) and (datetime.now().second == 1):
        IsEMAUpdate = True
        signal_update()
    else:       
        if (datetime.now().minute % timeFrame != 0):
            IsEMAUpdate = False
        
        limit = 2
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
        currentPrice = df["close"][limit-1]

    ### Giriş Bilgilerini Ayarla
    if (start == False) and (position == "") and ((long_signal == True) or (short_signal == True)):        
        startTime =  df["openTime"][limit-1]
        debugMsg = ""
        debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
        debugMsg += warn +  " " + str(toplamIslemSayisi + 1) + ". Signal "
        if long_signal:
            debugMsg += "LONG\n"
        elif short_signal:
            debugMsg += "SHORT\n"
        debugMsg += "\n"

### LONG İŞLEM ###
    # Long İşlem Aç
    if (start == False) and (position == "") and (long_signal == True):
        start = True
        position = "Long"    

        toplamIslemSayisi = toplamIslemSayisi + 1
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee
        islemFiyati = currentPrice
        hedefFiyati = islemFiyati * (1 + karOrani)
        islemBuyuklugu = cuzdan * kaldirac

        debugMsg += "Order Time\t\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "LONG Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t\t: " + str(round(islemFee,4)) + "\n"
        debugMsg += "\n" 
        debugMsg += "\n"
        debugMsg += "Reference Bands\n" 
        debugMsg += "EMA(" + str(emaBuy) + ") -> " + str(round(emaBuyPrice,4)) + "\n" 
        debugMsg += "EMA(" + str(emaSell) + ") -> " + str(round(emaSellPrice,4)) + "\n"
        debugMsg += "EMA(" + str(emaSignal) + ") -> " + str(round(emaSignalPrice,4)) + "\n"
        debugMsg += "\n"  
        send_message_to_telegram(channelAlbiz, debugMsg)
        debugMsg = ""  

    # Long İşlem Kar Al
    elif (start == True) and (position == "Long") and (currentPrice >= hedefFiyati):
        islemKar = cuzdan * karOrani * kaldirac
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee

        debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
        debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal LONG Close Take Profit \n"
        debugMsg += "\n"
        debugMsg += "Order Time\t\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "LONG Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t\t: " + str(round(islemFee,7)) + "\n"
        debugMsg += "Order Profit\t\t: % " + str(round(karOrani * 100,3)) + "\n"
      
        islemBitti = True
        toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

    # Long İşlem Stop Ol
    elif (start == True) and (position == "Long") and (currentPrice <= emaSignalPrice):
        hedefFiyati = currentPrice        
        islemKar = cuzdan * (((hedefFiyati - islemFiyati) / islemFiyati)) * kaldirac
        zararOran = islemKar / cuzdan
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee

        debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
        debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal LONG Close Stop Loss\n"
        debugMsg += "\n"
        debugMsg += "Order Time\t\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "LONG Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "LONG Order SL\t\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t\t: " + str(round(islemFee,7)) + "\n"
        debugMsg += "Order Profit\t\t: % -" + str(round(zararOran * 100,3)) + "\n" 

        islemBitti = True
        toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

# SHORT İŞLEM
    # Short İşlem Aç
    if (start == False) and (position == "") and (short_signal == True):
        start = True
        position = "Short"  

        toplamIslemSayisi = toplamIslemSayisi + 1
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee        
        islemFiyati = currentPrice
        hedefFiyati = islemFiyati * (1 - karOrani)
        islemBuyuklugu = cuzdan * kaldirac

        debugMsg += "Order Time\t\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "SHORT Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t\t: " + str(round(islemFee,4)) + "\n"
        debugMsg += "\n" 
        debugMsg += "\n"
        debugMsg += "Reference Bands\n" 
        debugMsg += "EMA(" + str(emaBuy) + ") -> " + str(round(emaBuyPrice,4)) + "\n" 
        debugMsg += "EMA(" + str(emaSell) + ") -> " + str(round(emaSellPrice,4)) + "\n"
        debugMsg += "EMA(" + str(emaSignal) + ") -> " + str(round(emaSignalPrice,4)) + "\n"
        debugMsg += "\n"  
        send_message_to_telegram(channelAlbiz, debugMsg)
        debugMsg = ""  

    # Short İşlem Kar Al
    elif (start == True) and (position == "Short") and (currentPrice <= hedefFiyati):
        islemKar = cuzdan * karOrani * kaldirac
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee

        debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
        debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal SHORT Close Take Profit \n"
        debugMsg += "\n"
        debugMsg += "Order Time\t\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "SHORT Order TP\t\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t\t: " + str(round(islemFee,7)) + "\n"
        debugMsg += "Order Profit\t\t: % " + str(round(karOrani * 100,3)) + "\n"     

        islemBitti = True 
        toplamKarliIslemSayisi = toplamKarliIslemSayisi + 1

    # Short İşlem Stop Ol
    elif (start == True) and (position == "Short") and (currentPrice >= emaSignalPrice):
        hedefFiyati = currentPrice
        islemKar = cuzdan * (((islemFiyati - hedefFiyati) / islemFiyati)) * kaldirac
        zararOran = islemKar / cuzdan
        toplamKar += islemKar
        cuzdan = cuzdan + islemKar
        islemFee = cuzdan * feeOrani * kaldirac
        toplamFee += islemFee

        debugMsg += "Run -> " + str(symbol) + " " + str(interval) + "\n"
        debugMsg += warn + " " + str(toplamIslemSayisi) + " Signal SHORT Close Stop Loss\n"
        debugMsg += "\n"
        debugMsg += "Order Time\t\t: " + str(df["openTime"][limit-1]) + "\n"
        debugMsg += "SHORT Order Price\t: " + str(round(islemFiyati,7)) + "\n"
        debugMsg += "SHORT Order SL\t\t: " + str(round(hedefFiyati,7)) + "\n"
        debugMsg += "Order LOT/FIAT\t\t: " + str(round(cuzdan * kaldirac,7)) + "\n"
        debugMsg += "Order Fee\t\t: " + str(round(islemFee,7)) + "\n"
        debugMsg += "Order Profit\t\t: % -" + str(round(zararOran * 100,3)) + "\n" 

        islemBitti = True
        toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1 
     
    if islemBitti == True:  
        debugMsg += "\n"
        debugMsg += "Report\n"
        debugMsg += "\n"
        debugMsg += "Strategy : " + str(symbol) + " " + str(kaldirac) + "x " + str(interval) + " EMA" + str(emaBuy) + " " + str(emaBuyType) + " EMA" + str(emaSell) + " " + str(emaSellType) + " EMA" + str(emaSignal) + " " + str(emaSignalType) + "\n"
        debugMsg += "Invest\t: " + str(round(baslangicPara,7)) + "\n"
        debugMsg += "ROI\t: " + str(round(toplamKar,7)) + "\n"
        debugMsg += "Total Fee\t: " + str(round(toplamFee,3)) + "\n"
        debugMsg += "Fund\t: " + str(round(cuzdan,7)) + "\n"
        debugMsg += "ROI\t: % " + str(round((toplamKar / baslangicPara) * 100,3)) + "\n"
        debugMsg += "\n"
        debugMsg += "Total Orders\t: " + str(toplamIslemSayisi) + "\n"
        debugMsg += "TP Orders\t: " + str(toplamKarliIslemSayisi) + "\n"
        debugMsg += "SL Orders\t: " + str(toplamZararKesIslemSayisi) + "\n"
        debugMsg += "Gain Orders\t: % " + str(round((toplamKarliIslemSayisi / toplamIslemSayisi) * 100,1)) + "\n"
        debugMsg += "Lose Orders\t: % " + str(round((toplamZararKesIslemSayisi / toplamIslemSayisi) * 100,1)) + "\n"        
        send_message_to_telegram(channelAlbiz, debugMsg)
        debugMsg = "" 
              
        islemBitti = False
        position = ""   
        start = False         
        islemKar = 0
        islemFee = 0
        islemFiyati = 0
        hedefFiyati = 0


    if (cuzdan + 10) < toplamFee:
        debugMsg = warn + warn + warn + "\nCüzdanda Para Kalmadı\n" + warn + warn + warn
        send_message_to_telegram(channelAlbiz, debugMsg)
        debugMsg = "" 
        quit() 

    sleep(0.1) 