import os
from dotenv import load_dotenv

load_dotenv()

SENDER = {
    "email": os.getenv("sender_email", ""),
    "password": os.getenv("sender_pwd", ""),
}
