from datetime import datetime 
import requests 
from threading import Thread 


# api = 5178648263:AAESJwnZBqv-C8IGRwFK4MJ7UgD93Yghe6I  
#https://api.telegram.org/bot5178648263:AAESJwnZBqv-C8IGRwFK4MJ7UgD93Yghe6I/sendMessage 
#-593936905 grup 
#1122622679 ibrahim 

mesaj_url = "https://api.telegram.org/bot5178648263:AAESJwnZBqv-C8IGRwFK4MJ7UgD93Yghe6I/sendMessage" 

def send_message(message): 
    #iş yükü parçacıgı için 
    def thread1(): 
        # mesajı telegrama yollayalım 
        requests.post(url=mesaj_url ,data={"chat_id":"-593936905","text":message}).json()                
 
    #thread ile fonksiyonu başlatır 
    th = Thread(target=thread1) 
    th.start() 
