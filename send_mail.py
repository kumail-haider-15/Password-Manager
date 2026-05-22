import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage

# Load environment variables from .env file
load_dotenv()

my_email = os.getenv("MY_EMAIL")
password = os.getenv("PASSWORD")


#   Email sending mechanism

def send_email(final_msg, email):
    msg = EmailMessage()
    msg.set_content(final_msg['message'])  # handles Unicode properly

    msg['Subject'] = final_msg['subject']
    msg["From"] = my_email
    msg["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(my_email, password)
        connection.send_message(msg)