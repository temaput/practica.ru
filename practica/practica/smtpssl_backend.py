from django.core.mail.utils import DNS_NAME
from django.core.mail.backends.smtp import EmailBackend
import smtplib

class EmailSSLBackend(EmailBackend):
    def open (self):
        """
        We will use the same lib as standart django backend
        but will choose SMTP_SSL instead of just SMTP class
        """
        if self.connection:
            return False  # connection already made
        try:
            self.connection = smtplib.SMTP_SSL(self.host, self.port,
                    local_hostname=DNS_NAME.get_fqdn())
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except:
            if not self.fail_silently:
                raise


