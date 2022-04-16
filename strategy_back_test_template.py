from this import s
import colorama
from colorama import Fore, Back, Style
from zmq import BACKLOG
import pandas as pd
import winsound

import datetime as dt

import pandas_ta as ta # it is used for some indicators

from ta.trend import SMAIndicator
from ta.trend import EMAIndicator
from ta.trend import MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from Indicators import super_trend, super_trend_1,super_trend_2,super_trend_3

### Warning Sound
duration = 1000  # milliseconds
freq = 440  # Hz

### Trade Variables
IsLongPosition = False
IsShortPosition = False
IsPositionExist= False

CurrentMoney = 100
FirstMoney = CurrentMoney
LowestMoney = CurrentMoney
HighestMoney = CurrentMoney

NumberOfStoploss = 0
NumberOfTransactions = 0
NumberOfWinTransaction = 0
NumberOfLossTransaction = 0

LongPositionEnterTime = 0 
LongPositionEnterPrice = 0
LongPositionExitPrice = 0

ShortPositionEnterTime = 0
ShortPositionEnterPrice = 0
ShortPositionExitPrice = 0

TakeProfitPrice = 0

Commission = 0.04
Leverage = 1
StopLossPercent = 6
TakeProfitPercent = 8
WinRate = 0

FilePath = "Historical_Data/"
FileName = "BTCUSDT_1d.csv"
HistoricalDataFileCsv = FilePath + FileName

# For reading timestamp data as date/time
"""
closeTime = print(df["closeTime"])

def calculate_time(timestamp):
    return dt.fromtimestamp(timestamp/1000) # /1000 for ms

for data in closeTime:
    print(calculate_time(data))
"""


print("BACKTEST PREPARING...")
# Data List
# [Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore]
attributes = ["openTime","open","high","low","close","volume","closeTime","qav","nat","tbbav","tbqav","ignore"]
df = pd.read_csv(HistoricalDataFileCsv, names = attributes)

df['open'] = df['open'].astype('float')
df['close'] = df['close'].astype('float')
#print(df['close'])
df['high'] = df['high'].astype('float')
df['low'] = df['low'].astype('float')
df["openTime"] = pd.to_datetime(df["openTime"],unit= "ms")


rsi = RSIIndicator(df["close"],14)
macd = MACD(df["close"])
bb = BollingerBands(df["close"])

df["RSI"] = rsi.rsi()
df["MACD"] = macd.macd()
df["MACD_signal"] = macd.macd_signal()
df["MACD_diff"] = macd.macd_diff()

df["BB_UpperBand"] = bb.bollinger_hband()
df["BB_LowerBand"] = bb.bollinger_lband()
df["BB_MidBand"] = bb.bollinger_mavg()
df["BB_BandWidth"] = bb.bollinger_wband()
df["BB_'%'B"] = bb.bollinger_pband()
df["BB_üst_band_kesti_mi"] = bb.bollinger_hband_indicator()
df["BB_alt_band_kesti_mi"] = bb.bollinger_lband_indicator()

super_trend_1.supertrend1(df)
super_trend_2.supertrend2(df)
super_trend_3.supertrend3(df)

df = df[['openTime', 'open', 'high', 'low', 'close', "RSI", "MACD", "MACD_signal", "MACD_diff", 
"BB_üst_band_kesti_mi","BB_alt_band_kesti_mi", "in_uptrend","uptrend1" ,"uptrend2","uptrend3"]]

print("BACKTEST STARTING...")

for i in range(df.shape[0]):    
    if i > 200:
        # LONG EVENT
        if df["uptrend1"][i-1] and df["uptrend2"][i-1] and df["uptrend3"][i-1] and IsPositionExist == False:
            if CurrentMoney > 5:
                LongPositionEnterPrice = df["open"][i]
                LongPositionEnterTime = df["openTime"][i]
                #takeProfitFiyat = longEnterFiyat + longEnterFiyat*tp/100
                CurrentMoney = CurrentMoney - ((CurrentMoney/100) * Commission * Leverage)
                IsPositionExist = True
                IsLongPosition = True
                print(str(df["openTime"][i]) +"      BUY EVENT : " + str(LongPositionEnterPrice) )
            else: 
                print("First Money Finished.")
                print (NumberOfTransactions)
                print("Lowest Money: ", LowestMoney)
                print("Highest Money: ", HighestMoney)
                quit()

        #SHORT EVENT
        if (not(df["uptrend1"][i-1] or df["uptrend2"][i-1] or df["uptrend3"][i-1])) and IsPositionExist == False:
            if CurrentMoney > 5:
                ShortPositionEnterPrice = df["open"][i]
                ShortPositionEnterTime = df["openTime"][i]
                #takeProfitFiyat = shortEnterFiyat - shortEnterFiyat*tp/100
                CurrentMoney = CurrentMoney - ((CurrentMoney/100) * Commission * Leverage)
                IsPositionExist = True
                IsShortPosition = True
                print(str(df["openTime"][i]) +"      SHORT EVENT : "+ str(ShortPositionEnterPrice))
            else: 
                print("First Money Finished.")
                print (NumberOfTransactions)
                print("Lowest Money: ", LowestMoney)
                print("Highest Money: ", HighestMoney)
                quit()

        # STOP LOSS
        if False: #(not (df["uptrend1"][i-1] and df["uptrend2"][i-1] and df["uptrend3"][i-1])) and pozisyondaMi==True: #and ((float(df["low"][i]) - longEnterFiyat) / longEnterFiyat) *100 * -1 >= stopLoss:
            #longExitFiyat = longEnterFiyat - (longEnterFiyat / 100 ) * stopLoss
            CurrentMoney = CurrentMoney + CurrentMoney*((float(df["open"][i]) - LongPositionEnterPrice) / LongPositionEnterPrice) *Leverage
            CurrentMoney = CurrentMoney - ((CurrentMoney / 100) * Commission * Leverage)
            if CurrentMoney < LowestMoney:
                LowestMoney = CurrentMoney
            if CurrentMoney > LowestMoney:
                LowestMoney = LowestMoney
            if HighestMoney < CurrentMoney:
                HighestMoney = CurrentMoney
            if HighestMoney > CurrentMoney:
                HighestMoney = HighestMoney
            NumberOfTransactions = NumberOfTransactions + 1
            NumberOfLossTransaction = NumberOfLossTransaction + 1
            WinRate = (NumberOfWinTransaction / NumberOfTransactions) * 100
            IsPositionExist = False
            NumberOfStoploss = NumberOfStoploss + 1
            print(Fore.RED)
            print( str(df["openTime"][i]) + "    STOP EVENT   ANA PARA : " + str(CurrentMoney))
            print(Style.RESET_ALL)
            print("-----------------------------------------------------")
            print("-----------------------------------------------------")
        
        # LIKIT OLMA 
        if IsPositionExist:
            if IsLongPosition :
                if ((float(df["low"][i]) - LongPositionEnterPrice) / LongPositionEnterPrice) * 100 * -1 >= 100:
                    IsPositionExist = False
                    IsLongPosition = False
                    NumberOfStoploss = NumberOfStoploss + 1 
                    CurrentMoney = 0
                    LowestMoney = 0
                    print("Liquidation event")
                    print("*****************************************************") 
                    print (NumberOfTransactions)
                    print("Lowest Money: ", LowestMoney)
                    print("Highest Money: ", HighestMoney)
                    quit()
            if IsShortPosition:
                if ((ShortPositionEnterPrice - float(df["low"][i])) / ShortPositionEnterPrice) * 100 * -1 >= 100:
                    IsPositionExist = False
                    IsShortPosition = False
                    NumberOfStoploss = NumberOfStoploss + 1 
                    CurrentMoney = 0
                    LowestMoney = 0
                    print("Liquidation event")
                    print("*****************************************************") 
                    print (NumberOfTransactions)
                    print("Lowest Money: ", LowestMoney)
                    print("Highest Money: ", HighestMoney)
                    quit()        
                
        # LONG TAKE PROFIT        
        if  (not (df["uptrend1"][i-1] and df["uptrend2"][i-1] and df["uptrend3"][i-1])) and IsPositionExist and IsLongPosition:#df["high"][i] >= takeProfitFiyat and pozisyondaMi and df["openTime"][i] != longEnterZaman:
            #longExitFiyat = df["ClosingEma"][i-1]
            TakeProfitPercent= (df["open"][i] - LongPositionEnterPrice) / LongPositionEnterPrice *100
            CurrentMoney = CurrentMoney + TakeProfitPercent*CurrentMoney*Leverage/100
            CurrentMoney = CurrentMoney - ((CurrentMoney / 100) * Commission * Leverage)

            if CurrentMoney < LowestMoney:
                LowestMoney = CurrentMoney
            if CurrentMoney > LowestMoney:
                LowestMoney = LowestMoney
            if HighestMoney < CurrentMoney:
                HighestMoney = CurrentMoney
            if HighestMoney > CurrentMoney:
                HighestMoney = HighestMoney
            NumberOfTransactions = NumberOfTransactions + 1
            #if longExitFiyat > longEnterFiyat:
            NumberOfWinTransaction = NumberOfWinTransaction + 1
            #else: loss = loss + 1
            WinRate = (NumberOfWinTransaction / NumberOfTransactions) * 100
            IsPositionExist = False
            IsLongPosition = False
            print( str(df["openTime"][i]) + "    TAKE PROFIT : " + str(df["open"][i])+    "\nCurrent Money : " + str(CurrentMoney))
            print("-----------------------------------------------------")
            print("-----------------------------------------------------")
            
        #SHORT TAKE PROFIT    
        if  (df["uptrend1"][i-1] or df["uptrend2"][i-1] or df["uptrend3"][i-1]) and IsPositionExist and IsShortPosition:#df["high"][i] >= takeProfitFiyat and pozisyondaMi and df["openTime"][i] != longEnterZaman:
            #longExitFiyat = df["ClosingEma"][i-1]
            TakeProfitPercent= (ShortPositionEnterPrice - df["open"][i] ) / ShortPositionEnterPrice *100
            CurrentMoney = CurrentMoney + TakeProfitPercent*CurrentMoney*Leverage/100
            CurrentMoney = CurrentMoney - ((CurrentMoney / 100) * Commission * Leverage)

            if CurrentMoney < LowestMoney:
                LowestMoney = CurrentMoney
            if CurrentMoney > LowestMoney:
                LowestMoney = LowestMoney
            if HighestMoney < CurrentMoney:
                HighestMoney = CurrentMoney
            if HighestMoney > CurrentMoney:
                HighestMoney = HighestMoney
            NumberOfTransactions = NumberOfTransactions + 1
            #if longExitFiyat > longEnterFiyat:
            NumberOfWinTransaction = NumberOfWinTransaction + 1
            #else: loss = loss + 1
            WinRate = (NumberOfWinTransaction / NumberOfTransactions) * 100
            IsPositionExist = False
            IsShortPosition = False
            print( str(df["openTime"][i]) + "    TAKE PROFIT : " +str(df["open"][i]) + "\nCurrent Money: " + str(CurrentMoney))
            print("-----------------------------------------------------")
            print("-----------------------------------------------------")    
        
        
print(Fore.BLACK)
print(Back.WHITE)
print("*****************************************************") 
print("*****************************************************")  
print("*****************************************************")          
print("BACKTEST FINISHED. RESULTS: ")
print(HistoricalDataFileCsv)
print("-----------------------------------------------------")
print("First Money: ", FirstMoney)
print("Lowest Money: ", LowestMoney)
print("Highest Money: ", HighestMoney)
print("Current Money: ", CurrentMoney)
print("*****************************************************") 
txt = "Profit Ratio: %{profit:.2f}"
print(txt.format(profit=(CurrentMoney - FirstMoney)/FirstMoney*100))
print("*****************************************************") 
print("Number Of Transactions: ", NumberOfTransactions)
print("Win: ", NumberOfWinTransaction, " Loss: ", NumberOfLossTransaction, " Win Rate: " , WinRate)
print("-----------------------------------------------------")
print(Style.RESET_ALL)
winsound.Beep(freq, duration)