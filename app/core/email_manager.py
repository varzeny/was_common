# email_manager.py

## lib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email
import aiosmtplib
from aioimaplib import IMAP4_SSL

from typing import Dict

## module


## definition
class EmailClient:
    def __init__(self, config) -> None:   
        self.smtp_server = config["smtp_server"]
        self.smtp_port = config["smtp_port"]
        self.imap_server = config["imap_server"]
        self.email_address = config["email_address"]
        self.email_password = config["email_password"]


    async def send_email(self, to:str, subject:str, subtype:str, body):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(
                _text = body,
                _subtype = subtype
            )
        )
        try:
            await aiosmtplib.send(
                msg,
                hostname= self.smtp_server,
                port= self.smtp_port,
                start_tls=True,
                username=self.email_address,
                password=self.email_password
            )
            print(f"sent email to {to}")
        except Exception as e:
            print("error form send_mail : ", e)


    async def receive_email(self):
        try:
            # IMAP 서버에 연결 및 로그인
            client = IMAP4_SSL(self.imap_server)
            await client.wait_hello_from_server()
            await client.login(self.email_address, self.password)

            # 받은 편지함 선택
            await client.select('INBOX')

            # 이메일 검색 (모든 이메일)
            search_response = await client.search('ALL')
            email_ids = search_response[1][0].split()
            if not email_ids:
                print("No emails found.")
                return

            latest_email_id = email_ids[-1].decode()
            print(latest_email_id)

            # 이메일 데이터 가져오기
            fetch_response = await client.fetch(latest_email_id, '(RFC822)')


            try:
                # fetch_response에서 이메일 데이터를 올바르게 추출
                raw_email_data = fetch_response.lines[1]
                if isinstance(raw_email_data, bytearray):
                    raw_email = bytes(raw_email_data)
                    print("==========")

                else:
                    print("Error: raw_email_data is not bytearray")
            except Exception as e:
                print("Error accessing fetched data:", e)
                return

            # 이메일 파싱
            msg = email.message_from_bytes(raw_email)
            print("From: ", self.decode_mime_words(msg['From']))
            print("Subject: ", self.decode_mime_words(msg['Subject']))

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload(decode=True).decode()
                        print("Body: ", body)
            else:
                body = msg.get_payload(decode=True).decode()
                print("Body: ", body)

        except Exception as e:
            print(f"Error: {e}")


class EmailManager:
    clients:Dict[str, EmailClient] = {}

    @classmethod
    def add_client( cls, config ):
        cls.clients[ config["name"] ] = EmailClient( config )