import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils
from os import getenv
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import datetime
from typing import Dict, List
import time


class Requestor():
    def __init__(self, url: str, sender_email: str, receivers_email: List[str]) -> None:
        self.url = url
        self.sender_email = sender_email
        self.receivers_email = receivers_email
        self.raw_data = []
        self.flat_data = {}
        self.flat_repository = {}

    def get_raw_data(self) -> None:
        response_part1 = requests.get(self.url)
        response_part2 = BeautifulSoup(response_part1.content, 'html.parser')
        response_part3 = response_part2.find(id='innerLayout').find(id='listContainer').find(id='body-container').find(id='gallerywide').find_all('li', {'class': 'wrap'})
        self.raw_data = response_part3

    def retrieve_flat_data(self) -> None:
        self.flat_data = {}

        for flat in self.raw_data:
            flat_id = flat.get('data-id')
            flat_title = flat.find('div', {'class': 'tcenter'}).a['title']
            flat_url = flat.find('div', {'class': 'tcenter'}).a['href']
            flat_fetch_date = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

            flat_price = flat.find('div', {'class': 'price'})
            flat_price_class = flat_price.get('class')

            if len(flat_price_class) == 1:
                flat_price = str(flat_price.string).strip().split(' ')
                flat_price = f'{flat_price[0]}{flat_price[1]}'
            else:
                flat_price = flat_price.get_text().strip().split(' ')
                flat_price = f'{flat_price[0]}{flat_price[1]}'

            record = {flat_id: [flat_title, flat_url, flat_fetch_date, flat_price]}
            self.flat_data.update(record)

    def add_to_repository(self, new_flat: Dict) -> None:
        self.flat_repository.update(new_flat)

    def send_email(self, flats_to_send: Dict) -> None:
        email_content = f'''
        Hello,
        Number of new flats: {len(flats_to_send)}


        '''
        # {[flats_to_send[flat_id] for flat_id in flats_to_send.keys()]} \n

        sender_pass = getenv('PASSWORD')
        message = MIMEMultipart('alternative')
        message['From'] = email.utils.formataddr(('Norbert', self.sender_email))
        message['Subject'] = 'New flat offer!'

        context = ssl.create_default_context()

        try:
            session = smtplib.SMTP_SSL('smtp.poczta.onet.pl', 465, context=context, timeout=120)
            session.ehlo()
            session.login(self.sender_email, sender_pass)

            for receiver in self.receivers_email:
                message['To'] = email.utils.formataddr(('Subscriber', receiver))
                message.attach(MIMEText(email_content, 'plain'))
                text = message.as_string()
                session.sendmail(self.sender_email, receiver, text)

            session.close()

        except Exception as e:
            print("Error: ", e)
        else:
            print(f'Mail Sent. Number of flats: {len(flats_to_send)}')


if __name__ == '__main__':
    load_dotenv()
    url = 'https://www.olx.pl/nieruchomosci/mieszkania/wynajem/wroclaw/?search%5Bfilter_float_price%3Ato%5D=3000&search%5Bfilter_enum_rooms%5D%5B0%5D=two&search%5Bprivate_business%5D=private&search%5Border%5D=created_at%3Adesc&view=galleryWide'
    sender_email = 'trebronszef@op.pl'
    receivers_email = ['trebronszef1@gmail.com']
    # interval = 1 * 60 * 10  # 10 minutes
    interval1 = 1 * 10
    requestor = Requestor(url, sender_email, receivers_email)
    print('Requester created.')

    iterator = 1

    while True:
        time_start = time.time()

        requestor.get_raw_data()
        print('Raw data fetched.')

        requestor.retrieve_flat_data()
        print('Flat data retrieved.')

        potential_new_flats = {}

        for new_flat_id in requestor.flat_data.keys():
            if not new_flat_id in requestor.flat_repository.keys():
                d = {new_flat_id: requestor.flat_data[new_flat_id]}
                requestor.add_to_repository(d)
                potential_new_flats.update(d)
        print('Comparing loop ended.')

        if len(potential_new_flats) > 0 and iterator > 1:
            pass
            # requestor.send_email(potential_new_flats)

        print('---FLAT DATA:---\n', set(requestor.flat_data))
        print('---POT DATA:---\n', set(potential_new_flats))
        print('---REP DATA:---\n', set(requestor.flat_repository))

        potential_new_flats.clear()
        print(f'End of iteration. Loop time: {(time.time()-time_start)} sec ')
        iterator += 1
        time.sleep(interval1)
