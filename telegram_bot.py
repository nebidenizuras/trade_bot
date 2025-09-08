from datetime import datetime 
import requests 
from threading import Thread 
        
# api = 5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c  
# Kontrol et aktifse true 
# https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c 

# Aşağıdaki Link Üzerinden Group ID Bul
# https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c/getUpdates

# Bot ID    : 593917120

message_url = "https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c/sendMessage"

id_channel_00 = "-1001687885923"  
id_channel_01 = "-1001492284839"  
id_channel_02 = "-1001630300483"  
id_channel_03 = "-1001689764244"  
id_channel_04 = "-1001509604144"  
id_channel_05 = "-1001625055452"  
id_channel_06 = "-1001628871969"  
id_channel_07 = "-1001692848554"  

channel_00   = "channel_00" #CRYPTO-1D
channel_01   = "channel_01" #CRYPTO-4H
channel_02   = "channel_02" #CRYPTO-1H
channel_03   = "channel_03" #CRYPTO-15m
channel_04   = "channel_04" #BIST-1D
channel_05   = "channel_05" #USSTOCK-1D
channel_06   = "channel_06" #TEST
channel_07   = "channel_07"

def send_message_to_telegram(channelID, message): 
    #iş yükü parçacıgı için 
    def thread1(): 
        # mesajı telegram kanalına yollayalım       
        if(channelID == channel_00):
            requests.post(url=message_url ,data={"chat_id":id_channel_00,"text":message}).json()    
        elif(channelID == channel_01):
            requests.post(url=message_url ,data={"chat_id":id_channel_01,"text":message}).json()  
        elif(channelID == channel_02):
            requests.post(url=message_url ,data={"chat_id":id_channel_02,"text":message}).json()               
        elif(channelID == channel_03):
            requests.post(url=message_url ,data={"chat_id":id_channel_03,"text":message}).json()  
        elif(channelID == channel_04):
            requests.post(url=message_url ,data={"chat_id":id_channel_04,"text":message}).json() 
        elif(channelID == channel_05):
            requests.post(url=message_url ,data={"chat_id":id_channel_05,"text":message}).json() 
        elif(channelID == channel_06):
            requests.post(url=message_url ,data={"chat_id":id_channel_06,"text":message}).json() 
        elif(channelID == channel_07):
            requests.post(url=message_url ,data={"chat_id":id_channel_07,"text":message}).json() 

    #thread ile fonksiyonu başlatır 
    th = Thread(target=thread1) 
    th.start()

# EMOJI
warn = '\U0000203C'

msg = warn + warn + warn + "\nSakin Ol, Plana Güven...\n" + warn + warn + warn

"""
send_message_to_telegram(channel_00,msg)
send_message_to_telegram(channel_01,msg)
send_message_to_telegram(channel_02,msg)
send_message_to_telegram(channel_03,msg)
"""
