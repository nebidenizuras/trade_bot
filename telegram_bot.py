from datetime import datetime 
import requests 
import tkinter 
from tkinter import *
from threading import Thread 


        
# api = 5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c  

# Kontrol et aktifse true 
# https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c 

# Bot ID    : 593917120
# Grup ID   : -1001542109604
 
message_url = "https://api.telegram.org/bot5356826126:AAEjHzEKvwhFDoy4wdnDdtK9dtxTz8vN94c/sendMessage"

def send_message(message): 
    #iş yükü parçacıgı için 
    def thread1(): 
        # mesajı telegrama yollayalım 
        requests.post(url=message_url ,data={"chat_id":"-1001542109604","text":message}).json()                
 
    #thread ile fonksiyonu başlatır 
    th = Thread(target=thread1) 
    th.start()