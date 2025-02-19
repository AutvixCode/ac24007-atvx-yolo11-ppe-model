import sqlite3
import pandas as pd
import smtplib
from io import BytesIO
from PIL import Image
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# 🔹 Configurações de e-mail (USE VARIÁVEIS DE AMBIENTE PARA SEGURANÇA)
SENDER_EMAIL = "sistema@autvix.com.br"
SENDER_PASSWORD = "rwdgnwbcztxwkwlw"
RECIPIENT_EMAIL = "autvixcode@autvix.com.br"

# 🔹 Conectar ao banco de dados e obter o último alarme
with sqlite3.connect('base.db') as conn:
    df = pd.read_sql_query("SELECT data, hora, imagem FROM detectModel ORDER BY data DESC, hora DESC LIMIT 1", conn)

if df.empty:
    print("❌ Nenhum alarme detectado.")
    exit()

alarm_date, alarm_time, image_blob = df.iloc[0]
image = Image.open(BytesIO(image_blob))
image_filename = "detectModel_alarm.jpg"
image.save(image_filename, format="JPEG")

msg = MIMEMultipart()
msg["From"] = SENDER_EMAIL
msg["To"] = RECIPIENT_EMAIL
msg["Subject"] = f"🚨 Alarme Detectado - {alarm_date} {alarm_time}"

msg.attach(MIMEText(f"""
    <h2>🚨 Alarme Detectado!</h2>
    <p><b>Data:</b> {alarm_date}</p>
    <p><b>Hora:</b> {alarm_time}</p>
    <p>Em anexo, a imagem capturada pelo sistema.</p>
""", "html"))

with open(image_filename, "rb") as img_file:
    msg.attach(MIMEImage(img_file.read(), name=image_filename))

try:
    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print("✅ E-mail enviado com sucesso via Outlook!")
except Exception as e:
    print(f"❌ Erro ao enviar o e-mail: {e}")
