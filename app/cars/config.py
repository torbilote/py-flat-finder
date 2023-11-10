import random

RECIPIENTS = [
    "bartoszek.jus@gmail.com",
    "trebronszef1@gmail.com",
]

WEB_URL = "https://www.olx.pl/motoryzacja/samochody/?page=1&search%5Bfilter_enum_car_body%5D%5B0%5D=sedan&search%5Bfilter_enum_car_body%5D%5B1%5D=estate-car&search%5Bfilter_enum_condition%5D%5B0%5D=notdamaged&search%5Bfilter_enum_petrol%5D%5B0%5D=petrol&search%5Bfilter_enum_petrol%5D%5B1%5D=lpg&search%5Bfilter_enum_transmission%5D%5B0%5D=manual&search%5Bfilter_float_price%3Ato%5D=35000&search%5Bfilter_float_year%3Afrom%5D=2013"
WEB_CLASSES = {
    "olx_items": "css-1sw7q4x",
    "olx_item_url": "css-rc5s2u",
    "olx_item_header": "css-16v5mdi",
    "olx_item_price": "css-10b0gli",
    "olx_item_refresh_dt": "css-veheph",
}
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.69",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
]
REQUEST_HEADERS = {
    "User-Agent": random.choice(user_agents),
    "Accept": "application/json",
    "Content-Type": "application/json",
}
FILE_PATH_LOCAL = "data/cars.csv"
FILE_ID_DB = "1snf1v7apGGTAcGgIMuV4Dn9jQfWsSWSX"
