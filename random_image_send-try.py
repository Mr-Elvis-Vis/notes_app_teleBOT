import requests
from telegram import Bot

bot = Bot(token='5009373960:AAGL4dW_6BX4wi7JJGIT6QbTQooZoL4Tnvo')

# Адрес API сохраним в константе
URL = 'https://api.thecatapi.com/v1/images/search'
chat_id = 105882124
# Делаем GET-запрос к эндпоинту:
response = requests.get(URL).json()
# Извлекаем из ответа URL картинки:
random_cat_url = response[0].get('url')  

# Передаём chat_id и URL картинки в метод для отправки фото:
bot.send_photo(chat_id, random_cat_url)