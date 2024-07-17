# email_manager.py

## lib
import smtplib, imaplib, email

## module


## definition
class EmailClient:
    def __init__(self, config) -> None:   
        self.smtp_server = config["smtp_server"]
        self.smtp_port = config["smtp_port"]
        self.imap_server = config["imap_server"]
        self.email_address = config["email_address"]
        self.email_password = config["email_password"]




class EmailManager:
    servers = {}

    @classmethod
    def add_server( cls, config ):
        cls.servers[ config["name"] ] = EmailClient( config )