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

channel00   = "channel00"
channel01   = "channel01"
channel02   = "channel02"
channel03   = "channel03"


def send_message_to_telegram(channelID, message): 
    #print(message)
    #'''
    #iş yükü parçacıgı için 
    def thread1(): 
        # mesajı telegram kanalına yollayalım       
        if(channelID == channel00):
            requests.post(url=message_url ,data={"chat_id":id_channel_00,"text":message}).json()    
        elif(channelID == channel01):
            requests.post(url=message_url ,data={"chat_id":id_channel_01,"text":message}).json()  
        elif(channelID == channel02):
            requests.post(url=message_url ,data={"chat_id":id_channel_02,"text":message}).json()               
        elif(channelID == channel03):
            requests.post(url=message_url ,data={"chat_id":id_channel_03,"text":message}).json()  

    #thread ile fonksiyonu başlatır 
    th = Thread(target=thread1) 
    th.start()
    #'''

# EMOJI
warn = '\U0000203C'

msg = warn + warn + warn + "\nSakin Ol, Plana Güven...\n" + warn + warn + warn

"""
send_message_to_telegram(channel00,msg)
send_message_to_telegram(channel01,msg)
send_message_to_telegram(channel02,msg)
send_message_to_telegram(channel03,msg)
"""
