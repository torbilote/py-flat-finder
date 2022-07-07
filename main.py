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
from typing import Dict
import time
import pandas

load_dotenv()

URL = 'https://www.olx.pl/nieruchomosci/mieszkania/wynajem/wroclaw/?search%5Bfilter_float_price%3Ato%5D=3000&search%5Bfilter_enum_rooms%5D%5B0%5D=two&search%5Bprivate_business%5D=private&search%5Border%5D=created_at%3Adesc&view=galleryWide'
SENDER_EMAIL = getenv('SENDER')
SENDER_NAME = getenv('SENDER_NAME')
PASSWORD = getenv('PASSWORD')
RECIPIENTS_EMAILS = [getenv('REC1'), getenv('REC2')]
INTERVAL = 1 * 60 * 10  # 10 minutes
INTERVAL_DEV = 1 * 20 * 1  # 20 seconds


class Requestor():
    def __init__(self, url: str, sender_email: str, sender_name: str, recipients_emails: list[str], password: str) -> None:
        self.url = url
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.recipients_emails = recipients_emails
        self.password = password
        self.fetched_data = []
        self.enriched_data = {}
        self.flat_repository = {}

    def fetch_raw_data(self) -> None:
        self.fetched_data = []

        response_part1 = requests.get(self.url)
        response_part2 = BeautifulSoup(response_part1.content, 'html.parser')
        response_part3 = response_part2.find(id='innerLayout').find(id='listContainer').find(id='body-container').find(id='gallerywide').find_all('li', {'class': 'wrap'})

        self.fetched_data = response_part3

    def enrich_data(self) -> None:
        self.enriched_data = {}

        for fetched_item in self.fetched_data:
            flat_id = fetched_item.get('data-id')
            flat_title = fetched_item.find('div', {'class': 'tcenter'}).a['title']
            flat_url = fetched_item.find('div', {'class': 'tcenter'}).a['href']
            flat_fetch_date = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

            flat_price = fetched_item.find('div', {'class': 'price'})
            flat_price_class = flat_price.get('class')

            if len(flat_price_class) == 1:
                flat_price = str(flat_price.string).strip().split(' ')
                flat_price = f'{flat_price[0]}{flat_price[1]}'
            else:
                flat_price = flat_price.get_text().strip().split(' ')
                flat_price = f'{flat_price[0]}{flat_price[1]}'

            record = {flat_id: [flat_title, flat_url, flat_fetch_date, flat_price]}

            self.enriched_data.update(record)

    def send_email(self, new_flats: Dict) -> None:

        email_header1 = f'Witam serdecznie!\n\n'
        email_header2 = f'Liczba nowych mieszkań na OLX dla Twoich filtrów to {len(new_flats)}. Oto one:\n\n'
        email_header = email_header1 + email_header2

        new_flats_array = [flat for flat in new_flats.values()]

        email_main = ''

        for new_flat in new_flats_array:
            email_main = f'{email_main}\n{new_flat[1]} -- {new_flat[3]}zl -- {new_flat[0]} -- {new_flat[2]}'

        email_content = email_header + email_main

        message = MIMEMultipart('alternative')
        message['From'] = email.utils.formataddr((self.sender_name, self.sender_email))
        message['Subject'] = 'New fetched_item offer!'

        context = ssl.create_default_context()

        try:
            session = smtplib.SMTP_SSL('smtp.poczta.onet.pl', 465, context=context, timeout=120)
            session.ehlo()
            session.login(self.sender_email, self.password)

            for recipient_email in self.recipients_emails:
                message['To'] = email.utils.formataddr(('Subscriber', recipient_email))
                message.attach(MIMEText(email_content, 'plain'))
                text = message.as_string()
                session.sendmail(self.sender_email, recipient_email, text)

            session.close()

        except Exception as e:
            print("Error: ", e)
        else:
            print(f'Mail Sent. Number of flats: {len(new_flats)}')

    def load_repository(self) -> None:
        self.flat_repository = {}

        try:
            dataframe = pandas.read_csv(filepath_or_buffer='./repository.csv', index_col=0)

            for index, row in dataframe.iterrows():
                flat = {str(index): [row[0], row[1], row[2], row[3]]}
                self.flat_repository.update(flat)

        except FileNotFoundError:
            print(FileNotFoundError)
        else:
            pass

    def save_repository(self) -> None:
        dataframe = pandas.DataFrame.from_dict(data=self.flat_repository, orient='index', columns=['title', 'url', 'fetch_date', 'price'])
        dataframe.to_csv(path_or_buf='./repository.csv', index=True, index_label='id' )

def execute_requestor_job(requestor: Requestor):
    requestor.load_repository()
    requestor.fetch_raw_data()
    requestor.enrich_data()

    new_flats = {}

    # print('before:\n')
    # print('enriched:\n', list(requestor.enriched_data.keys())[:5])
    # print('repo:\n', list(requestor.flat_repository.keys())[:5])
    # print('nwe flats:\n', list(new_flats.keys())[:5])

    for potential_new_flat_id in requestor.enriched_data.keys():
            if not potential_new_flat_id in requestor.flat_repository.keys():
                new_flat = {potential_new_flat_id: requestor.enriched_data[potential_new_flat_id]}
                new_flats.update(new_flat)
                requestor.flat_repository.update(new_flat)

    # print('after:\n')
    # print('enriched:\n', list(requestor.enriched_data.keys())[:5])
    # print('repo:\n', list(requestor.flat_repository.keys())[:5])
    # print('nwe flats:\n', list(new_flats.keys())[:5])

    if len(new_flats) > 0:
        requestor.send_email(new_flats)

    requestor.save_repository()



if __name__ == '__main__':

    requestor = Requestor(URL, SENDER_EMAIL, SENDER_NAME, RECIPIENTS_EMAILS, PASSWORD)

    while True:

        print(f'--{datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")} -- Start of iteration. ')

        timer_start = time.perf_counter()

        execute_requestor_job(requestor)

        timer_stop = time.perf_counter()
        timer_result = timer_stop - timer_start

        print(f'--{datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")} -- End of iteration. Loop time: {timer_result} sec. ')

        time.sleep(INTERVAL)
