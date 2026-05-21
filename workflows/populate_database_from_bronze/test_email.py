import smtplib
from dotenv import load_dotenv
import os 

load_dotenv()
EMAIL = os.getenv("EMAIL_TO")
PASSWORD = os.getenv("EMAIL_PASSWORD")  # Sem espaços

try:
    print("Tentando conectar ao servidor do Google...")
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    print("✅ LOGIN BEM SUCEDIDO! A senha funciona.")
    server.quit()
except Exception as e:
    print(f"❌ FALHA NO LOGIN: {e}")