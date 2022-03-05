import time 
import telegram_bot
import binance_bot

while True:
    print("System Working...")

    binance_bot.calculate_trade_strategy()
    #telegram_bot.send_message("testMessage")

    time.sleep(5)
