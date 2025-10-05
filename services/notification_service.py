import smtplib
from email.mime.text import MIMEText

class NotificationService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"  
        self.smtp_port = 587
        self.email = "rohith142003@gmail.com"  
        self.password = "ixnv rhou wtxs mkci"  
    
    def send_notification(self, address, message):
        user_email = "kokoxef203@bllibl.com"  
        
        msg = MIMEText(message)
        msg['Subject'] = 'Mock Wallet Transaction'
        msg['From'] = self.email
        msg['To'] = user_email
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.sendmail(self.email, user_email, msg.as_string())
            server.quit()
            print("Notification sent!")
        except Exception as e:
            print(f"Notification failed: {e}")