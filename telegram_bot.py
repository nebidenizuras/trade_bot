from datetime import datetime 
import requests 
from threading import Thread 


        
# api = 5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c  

# Kontrol et aktifse true 
# https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c 

# Aşağıdaki Link Üzerinden Group ID Bul
# https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c/getUpdates

# Bot ID    : 593917120
# Grup ID(TMT #TestNet 0) : -1001630300483
# Grup ID(TMT #TestNet 1) : -1001492284839
# Grup ID(TMT #TestNet 2) : -1001689764244
# Grup ID(TMT Tarama)     : -1001687885923
 
message_url = "https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c/sendMessage"

id_albiz_gocen  = "-1001630300483"   # Grup ID(TMT #TestNet 0)
id_atsiz        = "-1001492284839"   # Grup ID(TMT #TestNet 1)
id_albiz        = "-1001689764244"   # Grup ID(TMT #TestNet 2)
id_tarama       = "-1001687885923"   # Grup ID(TMT Tarama)

channelAlbizGocen   = "channelAlbizGocen"
channelAtsiz        = "channelAltiz"
channelAlbiz        = "channelAlbiz"
channelTarama       = "channelTarama"

def send_message_to_telegram(channelID, message): 
    #print(message)
 
    #iş yükü parçacıgı için 
    def thread1(): 
        # mesajı telegram kanalına yollayalım 
        if(channelID == channelAlbizGocen):
            requests.post(url=message_url ,data={"chat_id":id_albiz_gocen,"text":message}).json()    
        elif(channelID == channelAtsiz):
            requests.post(url=message_url ,data={"chat_id":id_atsiz,"text":message}).json()    
        elif(channelID == channelAlbiz): 
            requests.post(url=message_url ,data={"chat_id":id_albiz,"text":message}).json()    
        elif(channelID == channelTarama):
            requests.post(url=message_url ,data={"chat_id":id_tarama,"text":message}).json()    
                    
    #thread ile fonksiyonu başlatır 
    th = Thread(target=thread1) 
    th.start()

# EMOJI
warn = '\U0000203C'

msg = warn + warn + warn + "\nSakin Ol, Plana Güven...\n" + warn + warn + warn

#send_message_to_telegram(channelAlbizGocen,msg)
#send_message_to_telegram(channelAtsiz,msg)
#send_message_to_telegram(channelAlbiz,msg)
#send_message_to_telegram(channelTarama,msg)
