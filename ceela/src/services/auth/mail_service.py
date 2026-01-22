import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pydantic import EmailStr

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "sys.soporte.001@gmail.com"
SENDER_PASSWORD = "zqzk dydn vcvi zput"
RECEIVER_EMAIL = ""

def send_email(email: EmailStr, subject: str, body: str):
    RECEIVER_EMAIL = email
    
    message = MIMEMultipart()
    message["From"] = f"CEELA <{SENDER_EMAIL}>"
    message["To"] = RECEIVER_EMAIL
    message["Subject"] = subject
    
    message.attach(MIMEText(body, "plain"))
    
    context = ssl.create_default_context()
    
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())
        return {"message": "Correo enviado exitosamente"}
    except Exception as e:
        return {"Error": str(e)}
