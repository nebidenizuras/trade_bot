from time import sleep   
from telegram_bot import warn, send_message_to_telegram, channelTarama
from datetime import datetime 
from data_manager import get_symbol_list, get_calculated_hype_symbol_list
from threading import Thread

symbolListFuture = get_symbol_list("USDT", "Future")
symbolListSpot = get_symbol_list("USDT", "Spot")

def do_work_hype_coin_scanning(market): 
    global symbolListFuture
    global symbolListSpot
    interval = '1m' 
    symbolList = ""
    candleTime = ""
    searchList = {}

    if (market == "Future"):
        symbolList = symbolListFuture  
    elif (market == "Spot"):
        symbolList = symbolListSpot  

    searchList, candleTime  = get_calculated_hype_symbol_list(market, interval, symbolList)

    debugMsg = ""
    debugMsg = warn + " " + market + " Coin Liste Taraması (" + interval + ")\n\n"
    debugMsg += "Hesaplanan Mum Zamanı : " + str(candleTime) + "\n\n"

    counter = 0
    for key, value in searchList.items():
        if(counter == 5):
            break
        debugMsg += str(key) + " : " + str(value) + "\n"       
        counter = counter + 1

    send_message_to_telegram(channelTarama, debugMsg)
    debugMsg = ""

    if(datetime.now().minute == 0):
        if (market == "Future"):
            symbolListFuture = get_symbol_list("USDT", "Future")
        elif (market == "Spot"):
            symbolListSpot = get_symbol_list("USDT", "Spot")   

while (1):
    if (datetime.now().second == 1):
        t = Thread(target=do_work_hype_coin_scanning, args=["Future"])
        t.start()
    sleep(1)        