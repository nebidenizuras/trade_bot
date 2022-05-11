from datetime import datetime 
import requests 
from threading import Thread 


        
# api = 5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c  

# Kontrol et aktifse true 
# https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c 

# Aşağıdaki Link Üzerinden Group ID Bul
# https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c/getUpdates

# Bot ID    : 593917120
# Grup ID(TMT Channel_00) : -1001687885923
# Grup ID(TMT Channel_01) : -1001492284839  
# Grup ID(TMT Channel_02) : -1001689764244
# Grup ID(TMT Channel_03) : -1001630300483


message_url = "https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c/sendMessage"

id_channel_00   = "-1001687885923"   # Grup ID(TMT Channel_00)
id_channel_01   = "-1001492284839"   # Grup ID(TMT Channel_01)
id_channel_02   = "-1001630300483"   # Grup ID(TMT Channel_02)
id_channel_03   = "-1001689764244"   # Grup ID(TMT Channel_03)

channel_00   = "channel_00"
channel_01   = "channel_01"
channel_02   = "channel_02"
channel_03   = "channel_03"


def send_message_to_telegram(channelID, message): 
    #print(message)
    #'''
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

    #thread ile fonksiyonu başlatır 
    th = Thread(target=thread1) 
    th.start()
    #'''

# EMOJI
warn = '\U0000203C'

msg = warn + warn + warn + "\nSakin Ol, Plana Güven...\n" + warn + warn + warn

"""
send_message_to_telegram(channel_00,msg)
send_message_to_telegram(channel_01,msg)
send_message_to_telegram(channel_02,msg)
send_message_to_telegram(channel_03,msg)
"""
