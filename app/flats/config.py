import random

RECIPIENTS = [
    # "bartoszek.jus@gmail.com",
    "trebronszef1@gmail.com",
]
WEB_URL = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/wroclaw/?search%5Bfilter_float_m%3Afrom%5D=55&search%5Bfilter_float_price%3Ato%5D=800000&search%5Border%5D=created_at%3Adesc&view=grid"
WEB_CLASSES = {
    "olx_items": "css-1sw7q4x",
    "olx_item_url": "css-z3gu2d",
    "olx_item_header": "css-1dqjq98",
    "olx_item_price": "css-3ahyw4",
    "olx_item_refresh_dt": "css-1mwdrlh",
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
FILE_PATH_LOCAL = "app/data/flats.csv"
FILE_ID_DB = "1YvybUmPJqL3nYg1-qKUxEKwq3Rqb0j2Y"

SEND_NOTIFICATION = True