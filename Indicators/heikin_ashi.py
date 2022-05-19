import pandas as pd 

def calculate_heikin_ashi(df): 

    df = pd.DataFrame(df, columns=["open", "high", "low", "close", "volume"])
    dfHA = df.copy()

    # Calculate Heikin Ashi
    for i in range(len(dfHA.index) - 1):
        if i > 0:
            dfHA['open'][i] = (float(dfHA['open'][i-1]) + float(dfHA['close'][i-1])) / 2 
        dfHA['close'][i] = (float(df['close'][i]) + float(df['open'][i]) + float(df['low'][i]) + float(df['high'][i])) / 4
        dfHA['high'][i] = max(dfHA['high'][i], dfHA['open'][i], dfHA['close'][i])
        dfHA['low'][i] = min(dfHA['low'][i], dfHA['open'][i], dfHA['close'][i])
    
    return dfHA