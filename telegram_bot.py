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

def send_message_TMT_TestNet0(message): 
    #print(message)
    #'''   
    #iş yükü parçacıgı için 
    def thread1(): 
        # mesajı telegrama yollayalım 
        requests.post(url=message_url ,data={"chat_id":"-1001630300483","text":message}).json()                
 
    #thread ile fonksiyonu başlatır 
    th = Thread(target=thread1) 
    th.start()
    #'''

def send_message_TMT_TestNet1(message): 
    #print(message)
    #'''   
    #iş yükü parçacıgı için 
    def thread1(): 
        # mesajı telegrama yollayalım 
        requests.post(url=message_url ,data={"chat_id":"-1001492284839","text":message}).json()                
 
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
        requests.post(url=message_url ,data={"chat_id":"-1001689764244","text":message}).json()                
 
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
        requests.post(url=message_url ,data={"chat_id":"-1001687885923","text":message}).json()                
 
    #thread ile fonksiyonu başlatır 
    th = Thread(target=thread1) 
    th.start()
    #'''

# EMOJI
warn = '\U0000203C'

msg = warn + warn + warn + "\nSakin Ol, Plana Güven...\n" + warn + warn + warn

#send_message_TMT_TestNet0(msg)
#send_message_TMT_TestNet1(msg)
#send_message_TMT_TestNet2(msg)
#send_message_tarama(msg)