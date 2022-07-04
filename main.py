from fbchat import Client
from fbchat.models import *
from getpass import getpass

client = Client('norbert.lipinski96@gmail.com', getpass())
client.send(Message(text='Wiadomosc od koteczka wyslana z bota muhaha :*'), thread_id='100004435502825', thread_type=ThreadType.USER)

client.logout()
