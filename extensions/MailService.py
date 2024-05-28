from flask_mail import Mail, Message
from typing import List, Tuple
import logging

class MailService:
    def __init__(self, app):
        MailService.__instance = self
        self.mail = Mail(app)
        self.app = app
        logging.getLogger("StreamLogger").info("Mail Service initialied.")
        logging.getLogger("FileLogger").info("Mail Service initialied.")

    def send_mail(self, subject, recipients, body):
        message = Message(subject=subject, recipients=recipients, body=body)
        with self.app.app_context():
            with self.mail.connect() as connection:
                connection.send(message)

    @staticmethod
    def get_instance():
        if MailService.__instance is not None:
            return MailService.__instance
        else:
            raise Exception("MailService is not initialized")
