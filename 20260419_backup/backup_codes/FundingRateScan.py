import requests

# Coinglass API anahtarınızı buraya girin
API_KEY = 'API_ANAHTARINIZ'

# API endpoint
url = 'https://open-api-v3.coinglass.com/api/futures/coins-markets'

# HTTP başlıkları
headers = {
    'accept': 'application/json',
    'coinglassSecret': API_KEY
}

# API isteği
response = requests.get(url, headers=headers)

# Yanıtı kontrol et ve işle
if response.status_code == 200:
    data = response.json()
    # Veriyi işleyin
    for coin in data['data']:
        print(f"Coin: {coin['symbol']}, Ortalama Fonlama Oranı: {coin['avgFundingRateByOi']}")
else:
    print(f"API isteği başarısız oldu. Durum kodu: {response.status_code}")
