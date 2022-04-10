import pandas as pd 
import csv

counter = 0
FIB_1 = []
FIB_0_786 = []
FIB_0_618 = []
FIB_0_500 = []
FIB_0_382 = []
FIB_0_236 = []
FIB_0 = []

#csvName = "Historical_Data/BTCUSDT_1d.csv"

#attributes = ["openTime","open","high","low","close","volume","closeTime","2","3","4","5","6"]
#data = pd.read_csv(csvName, names = attributes)

def calculate_fib(df, period): 
    global counter

    for k in range (period):
        FIB_1.append('NaN')
        FIB_0_500.append('NaN')
        FIB_0.append('NaN')
        k = k + 1

    for i in df['close']:
        if (counter + period) < len(df): 
            df2 = df.iloc[counter : counter + period, : ]
            maxr = df2['high'].max()
            minr = df2['low'].min()
            ranr = maxr - minr 

            FIB_1.append(maxr)
            FIB_0_500.append(minr + 0.5 * ranr)
            FIB_0.append(minr)
            counter = counter + 1
        else: 
            break     
    
    df['FIB_1'] = pd.Series(FIB_1) 
    df['FIB_0_500'] = pd.Series(FIB_0_500)
    df['FIB_0'] = pd.Series(FIB_0)
    df["openTime"] = pd.to_datetime(df["openTime"],unit= "ms")
    df["closeTime"] = pd.to_datetime(df["closeTime"],unit= "ms")
    

#calculate_fib(data, 10)
#print(data)