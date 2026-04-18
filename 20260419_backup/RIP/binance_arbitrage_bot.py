from binance.client import Client  
import pandas as pd 
import user_api_key 
import time 

client = Client(user_api_key.key_id,user_api_key.secret_key_id) 

symbolList = ["BTCUSDT","XRPUSDT","XRPBTC"]  
interval = '1m' 
limit = 1
priceList = {'BTCUSDT':0, 'XRPUSDT':0, 'XRPBTC':0}
mainMoney = 100

while 1:
    for symbol in symbolList:
        candles = client.get_klines(symbol=symbol, interval=interval, limit=limit) 
        df = pd.DataFrame(candles, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
                                            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
                                            'taker_buy_quote_asset_volume', 'ignore']) 
        ## Clean data 
        df = df[['open_time', 'open', 'high', 'low', 'close', 'close_time', 'volume']] 
        
    
        df['open_time'] = pd.to_datetime(df["open_time"], unit="ms")
        df['close_time'] = pd.to_datetime(df["close_time"], unit="ms")
        df['open'] = df['open'].astype('float') 
        df['close'] = df['close'].astype('float') 
        df['high'] = df['high'].astype('float') 
        df['low'] = df['low'].astype('float') 
        df['volume'] = df['volume'].astype('float')
        serverTime = client.get_server_time() 
        serverTime = time.strftime('%m.%d.%Y %H:%M:%S',time.gmtime(serverTime['serverTime']/1000.))  

        priceList[symbol] = df['high'][0] 

    xrpCount = mainMoney / priceList.get("XRPUSDT")
    btcCount = xrpCount * priceList.get("XRPBTC") 
    lastMoney = btcCount * priceList.get("BTCUSDT")

    print("************************************")
    print("USDT/XRP -> XRP/BTC -> BTC/USDT")
    print("*** " + serverTime + " ***")
    print("Ana Para : " + str(mainMoney))
    print("Son Para : " + str(lastMoney))
    print("************************************")

    time.sleep(10)
