'''
- EMA'lar open hesaplanır. 2 Open 2 Close 34 Open hesaplanır
- GMT'de çalışır
'''
from datetime import datetime   
from datetime import timedelta
from time import sleep    

from binance.client import Client  
from user_api_key import key_id, secret_key_id

import pandas as pd 

from telegram_bot import warn, send_message_to_telegram, channel_00

import operator
from operator import index
import array as arr

from data_manager import get_symbol_list, get_calculated_hype_symbol_list
import threading

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

long_signal = False
short_signal = False

# Order Amount Calculation
toplamIslemSayisi = 0
toplamKarliIslemSayisi = 0
toplamZararKesIslemSayisi = 0

# Parite Bilgileri
symbol = "BTCUSDT"
interval = "5m"
timeFrame = 5
candle_count = 1

df = ['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 
      'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
      'taker_buy_quote_asset_volume', 'ignore']

send_message_to_telegram(channel_00, "TMT Grid Strategy Is Started...\n")

def signal_update():
    global candle_count
    global currentPrice
    global long_signal
    global short_signal

    candles = client.get_klines(symbol=symbol, interval=interval, limit=candle_count) 
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

    long_signal = True
    short_signal = False       

signal_update()

mutex = threading.Lock()


############################################################################################################
# Parite Bilgileri
symbolNew = ""
isYenilemeZamani = False

symbolList = get_symbol_list("USDT", "Future")

def do_work_hype_coin_scanning(): 
    global symbolList
    global symbolNew

    market = "Future"
    interval = '1m' 
    candleTime = ""
    searchList = {}

    searchList, candleTime  = get_calculated_hype_symbol_list(market, interval, symbolList)
    mutex.acquire()
    symbolNew = list(searchList.keys())[0]
    mutex.release()

    if(datetime.now().minute == 0):
        symbolList = get_symbol_list("USDT", "Future")

#do_work_hype_coin_scanning()
 
############################################################################################################



while(True):
    try:
        # Tarama yap yeni coin varsa bul
        if (isYenilemeZamani == False ) and (datetime.now().second == 1):
            isYenilemeZamani = True
            t = threading.Thread(target=do_work_hype_coin_scanning)
            t.start()
        elif (datetime.now().second != 1):
            isYenilemeZamani = False

        if (islemBitti == False) and (start == False) and (position == ""):   
            mutex.acquire()         
            if(symbolNew != symbol):            
                symbol = symbolNew
                isYenilemeZamani = False
                IsEMAUpdate = True
                signal_update()
            mutex.release()

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
        if (start == False) and (position == "") and (long_signal == True) and (currentPrice > emaSellPrice):
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
            debugMsg += "EMA(" + str(emaBuy) + ")    -> " + str(round(emaBuyPrice,4)) + "\n" 
            debugMsg += "EMA(" + str(emaSell) + ")   -> " + str(round(emaSellPrice,4)) + "\n"
            debugMsg += "EMA(" + str(emaSignal) + ") -> " + str(round(emaSignalPrice,4)) + "\n"
            debugMsg += "\n"  
            send_message_to_telegram(id_channel_00, debugMsg)
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
            debugMsg += "Order Profit\t\t: % " + str(round(zararOran * 100,3)) + "\n" 

            islemBitti = True
            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1

    # SHORT İŞLEM
        # Short İşlem Aç
        if (start == False) and (position == "") and (short_signal == True) and (currentPrice < emaSellPrice):
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
            send_message_to_telegram(id_channel_00, debugMsg)
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
            debugMsg += "Order Profit\t\t: % " + str(round(zararOran * 100,3)) + "\n" 

            islemBitti = True
            toplamZararKesIslemSayisi = toplamZararKesIslemSayisi + 1 

        if islemBitti == True:  
            debugMsg += "\n"
            debugMsg += "Report\n"
            debugMsg += "\n"
            debugMsg += "Strategy : " + str(symbol) + " " + str(kaldirac) + "x " + str(interval) + " EMA" + str(emaBuy) + " " + str(emaBuyType) + " EMA" + str(emaSell) + " " + str(emaSellType) + " EMA" + str(emaSignal) + " " + str(emaSignalType) + "\n"
            debugMsg += "Invest\t\t: " + str(round(baslangicPara,7)) + "\n"
            debugMsg += "ROI\t\t: " + str(round(toplamKar,7)) + "\n"
            debugMsg += "Total Fee\t: " + str(round(toplamFee,3)) + "\n"
            debugMsg += "Fund\t\t: " + str(round(cuzdan,7)) + "\n"
            debugMsg += "ROI\t\t: % " + str(round((toplamKar / baslangicPara) * 100,3)) + "\n"
            debugMsg += "\n"
            debugMsg += "Total Orders\t: " + str(toplamIslemSayisi) + "\n"
            debugMsg += "TP Orders\t: " + str(toplamKarliIslemSayisi) + "\n"
            debugMsg += "SL Orders\t: " + str(toplamZararKesIslemSayisi) + "\n"
            debugMsg += "Gain Orders\t: % " + str(round((toplamKarliIslemSayisi / toplamIslemSayisi) * 100,1)) + "\n"
            debugMsg += "Lose Orders\t: % " + str(round((toplamZararKesIslemSayisi / toplamIslemSayisi) * 100,1)) + "\n"        
            send_message_to_telegram(channel_00, debugMsg)
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
            send_message_to_telegram(channel_00, debugMsg)
            debugMsg = "" 
            quit() 

        sleep(0.5)
    except Exception as e:
        debugMsg = "Error : " + str(e) + "\n\n\n"
        debugMsg += warn + "\nSistem Durduruluyor...\n" + warn
        send_message_to_telegram(channel_00, debugMsg)
        debugMsg = ""
        quit()