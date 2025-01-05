import smtplib
from _datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from PyQt5.QtCore import QRunnable


class Mail(QRunnable):
    def __init__(self):
        super().__init__()
        self.gmail_user = 'canhbaohoctap@gmail.com'
        self.gmail_password = 'rsvn gqco gqly szzs'
        self.recipient_email = 'huyvuvi123@gmail.com'
        self.infringe_count = None

    def run(self):
        self.send_summary_email(self.infringe_count)

    def set_information(self, infringe_count, email):
        self.infringe_count = infringe_count
        self.recipient_email = email

    def send_summary_email(self, infringe_count):
        today_date = datetime.now().strftime('%Y-%m-%d')
        subject = f"Thông báo lỗi ngày {today_date}"
        total_errors = sum(infringe_count.values())
        body = f"Tổng số lỗi trong trong quá trình học vừa qua ngày {today_date}: {total_errors}\n"
        for error_type, count in infringe_count.items():
            body += f"- {error_type}: {count} lần\n"

        body += "\nBạn hãy điều chỉnh lại tư thế học tốt hơn. Học tốt sẽ giúp bạn ngăn chặn các tình huống như trên."
        self.send_email(subject, body)

    def send_email(self, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.gmail_user
        msg['To'] = self.recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.gmail_user, self.gmail_password)
                server.sendmail(self.gmail_user, self.recipient_email, msg.as_string())
        except Exception as e:
            print(e)