import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils
from os import environ

print('MAIL SCRIPT IS STARTED...')

mail_content = '''Hello,
This is a simple mail from Norbert's computer. Tell him he is awesome. Thank You!
'''
# The mail addresses and password
sender_address = 'trebronszef@op.pl'
sender_pass = environ.get('PASSWORD')
receiver_address = 'bartoszek.jus@gmail.com'

print('SIGNED IN SUCCESSFULLY...')
# Setup the MIME
counter = 1

# while counter <= 10:

message = MIMEMultipart('alternative')
message['From'] = email.utils.formataddr(('ja', sender_address,))
message['To'] = email.utils.formataddr(('inny_ja', receiver_address))
message['Subject'] = 'Norbert Cie znalazl :)'  # The subject line
# The body and the attachments for the mail
message.attach(MIMEText(mail_content, 'plain'))
context = ssl.create_default_context()
# Create SMTP session for sending the mail
print('CONNECTING TO SMTP...')

try:
    session = smtplib.SMTP_SSL('smtp.poczta.onet.pl', 465, context=context, timeout=120)  # use gmail with port
    print('SUCCESS CONNECTION...')
    print('sdasdasdasda', sender_pass, 'sdasdsdasdds')
    session.ehlo()
    session.login(sender_address, sender_pass)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.close()
    print('Counter: ', counter)
    counter = +1
except Exception as e:
    print("Error: ", e)
else:
    print('Mail Sent.')
finally:
    print('Session closed.')
