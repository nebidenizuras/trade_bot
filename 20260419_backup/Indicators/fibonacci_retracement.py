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
FIB = []

'''
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
'''  

def calculate_fib(df, period, fibVal): 
    global counter
    FIB = []
    counter = 0
    
    for k in range (period):
        FIB.append('NaN')       
        k = k + 1

    for i in df['close']:
        if (counter + period) < len(df): 
            df2 = df.iloc[counter : counter + period, : ]
            maxr = df2['high'].max()
            minr = df2['low'].min()
            ranr = maxr - minr 
            
            FIB.append(minr + fibVal * ranr)
            counter = counter + 1
        else: 
            break     
     
    return pd.Series(FIB) 

#calculate_fib(data, 10)
#print(data)