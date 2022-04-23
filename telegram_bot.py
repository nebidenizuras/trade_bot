from datetime import datetime 
import requests 
from threading import Thread 


        
# api = 5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c  

# Kontrol et aktifse true 
# https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c 

# Aşağıdaki Link Üzerinden Group ID Bul
# https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c/getUpdates

# Bot ID    : 593917120
# Grup ID(TMT TestNet)   : -1001542109604
# Grup ID(TMT TestNet 2) : -1001736136361
# Grup ID(TMT Tarama)    : -1001356226519
 
message_url = "https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c/sendMessage"

def send_message(message): 
    #print(message)
    #'''   
    #iş yükü parçacıgı için 
    def thread1(): 
        # mesajı telegrama yollayalım 
        requests.post(url=message_url ,data={"chat_id":"-1001542109604","text":message}).json()                
 
    #thread ile fonksiyonu başlatır 
    th = Thread(target=thread1) 
    th.start()
    #'''

def send_message_TMT_TestNet2(message): 
    #print(message)
    #'''   
    #iş yükü parçacıgı için 
    def thread1(): 
        # mesajı telegrama yollayalım 
        requests.post(url=message_url ,data={"chat_id":"-1001736136361","text":message}).json()                
 
    #thread ile fonksiyonu başlatır 
    th = Thread(target=thread1) 
    th.start()
    #'''

def send_message_tarama(message): 
    #print(message)
    #'''   
    #iş yükü parçacıgı için 
    def thread1(): 
        # mesajı telegrama yollayalım 
        requests.post(url=message_url ,data={"chat_id":"-1001356226519","text":message}).json()                
 
    #thread ile fonksiyonu başlatır 
    th = Thread(target=thread1) 
    th.start()
    #'''


# EMOJI
warn = '\U0000203C'

msg = warn + warn + warn + "\n\n\nSakin Ol, Plana Güven...\n\n\n" + warn + warn + warn
#send_message(msg)
#send_message_TMT_TestNet2(msg)
#send_message_tarama(msg)