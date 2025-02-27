import numpy as np
import requests
import sqlite3
import time
import threading
import io
import smtplib
import torch
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
from requests.auth import HTTPDigestAuth
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import time

# 🔹 Configurações da Câmera Dahua
class CameraConfig:
    USERNAME = "admin"
    PASSWORD = "autvix123456"
    IP_CAMERA = "192.168.1.108"
    PORT = "80"
    EVENT_URL = f"http://{IP_CAMERA}:{PORT}/cgi-bin/eventManager.cgi?action=attach&codes=[CrossLineDetection]"
    SNAPSHOT_URL = f"http://{IP_CAMERA}:{PORT}/cgi-bin/snapshot.cgi"
    DB_PATH = "database/base.db"

# 🔹 Configurações de E-mail
class EmailConfig:
    SENDER_EMAIL = "sistema@autvix.com.br"
    SENDER_PASSWORD = "rwdgnwbcztxwkwlw"
    RECIPIENT_EMAIL = "alexandre.baiocco@autvix.com.br"
    
# 🔹 Configurações do Modelo YOLO
class YOLOConfig:
    device = "cuda" if torch.cuda.is_available() else "cpu"

    @staticmethod
    def load_models():
        return {
            "gloves": YOLO('modelos/gloves.pt').to(YOLOConfig.device),
            "ppe": YOLO('modelos/ppe.pt').to(YOLOConfig.device)
        }

    @staticmethod
    def get_class_names():
        return {
            "gloves": ['Gloves', 'No-Gloves'],
            "ppe": ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 'Person', 'Safety Cone',
                     'Safety Vest', 'machinery', 'vehicle']
        }

    PPE_ALLOWED_CLASSES = {'Safety Vest', 'NO-Safety Vest', 'Hardhat', 'NO-Hardhat', 'NO-Mask', 'Mask'}

# Monitorar eventos de Tripwire
def monitor_tripwire():
    try:
        response = requests.get(CameraConfig.EVENT_URL, auth=HTTPDigestAuth(CameraConfig.USERNAME, CameraConfig.PASSWORD), stream=True)

        if response.status_code == 200:
            print("[INFO] Conexão estabelecida! Monitorando eventos de Tripwire...\n")
            last_capture_time = 0

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if "Code=CrossLineDetection" in decoded_line:
                        current_time = time.time()
                        if current_time - last_capture_time >= 15:
                            print(f"[ALERTA 🚨] Tripwire ativado!")
                            capture_snapshot()
                            last_capture_time = current_time
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro: {e}")

# Captura um snapshot e salva no banco
def capture_snapshot():
    try:
        response = requests.get(CameraConfig.SNAPSHOT_URL, auth=HTTPDigestAuth(CameraConfig.USERNAME, CameraConfig.PASSWORD), stream=True)

        if response.status_code == 200:
            data = datetime.now().strftime("%Y-%m-%d")
            hora = datetime.now().strftime("%H:%M:%S")
            imagem_blob = response.content
            salvar_no_banco(data, hora, imagem_blob)
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro ao capturar a imagem: {e}")
        
# Função para salvar a imagem no banco de dados SQLite
def salvar_no_banco(data, hora, imagem_blob):
    try:
        with sqlite3.connect(CameraConfig.DB_PATH, timeout=10) as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO tripwireAlarm (data, hora, imagem) VALUES (?, ?, ?)
            """, (data, hora, sqlite3.Binary(imagem_blob)))
            conexao.commit()
        print("[✅] Imagem salva no banco de dados com sucesso.")
    except sqlite3.Error as e:
        print(f"[ERRO] Falha ao salvar no banco: {e}")
        
# Função para desenhar as detecções
def desenhar_boxes(image_np, detections):
    image = Image.fromarray(image_np)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except IOError:
        font = ImageFont.load_default()

    for model_name, results in detections.items():
        for result in results:
            for box, cls_id in zip(result.boxes.xyxy, result.boxes.cls):
                class_name = YOLOConfig.get_class_names()[model_name][int(cls_id)]
                color = "red" if class_name in YOLOConfig.PPE_ALLOWED_CLASSES else "green"

                x1, y1, x2, y2 = map(int, box)
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

                text_size = draw.textbbox((0, 0), class_name, font=font)
                text_width = text_size[2] - text_size[0]
                text_height = text_size[3] - text_size[1]

                text_x = x1
                text_y = max(y1 - text_height, 0)

                draw.rectangle([text_x, text_y, text_x + text_width, text_y + text_height], fill=color)
                draw.text((text_x, text_y), class_name, fill="white", font=font)

    return image

# Função para obter o último ID já existente no banco
def obter_ultimo_id_tripwireAlarm():
    with sqlite3.connect(CameraConfig.DB_PATH, timeout=10) as banco:
        cursor = banco.cursor()
        cursor.execute("SELECT MAX(id) FROM tripwireAlarm")
        last_id = cursor.fetchone()[0] or 0
    return last_id

# Monitoramento da tabela tripwireAlarm para rodar o modelo em cima das imagens
def monitorar_e_salvar():
    last_id = obter_ultimo_id_tripwireAlarm()  
    models = YOLOConfig.load_models()
    class_names = YOLOConfig.get_class_names()
    print(f"📡 Iniciando monitoramento a partir do ID {last_id}...")

    while True:
        try:
            with sqlite3.connect(CameraConfig.DB_PATH, timeout=10) as banco:
                cursor = banco.cursor()

                cursor.execute("SELECT MAX(id) FROM tripwireAlarm")
                max_detect_id = cursor.fetchone()[0] or 0

                if max_detect_id > last_id:
                    cursor.execute("SELECT id, data, hora, imagem FROM tripwireAlarm WHERE id > ? ORDER BY id ASC", (last_id,))
                    novos_registros = cursor.fetchall()

                    for novo_registro in novos_registros:
                        id_imagem, data, hora, imagem_blob = novo_registro
                        last_id = id_imagem

                        print(f"📡 Novo evento de Tripwire! ID {id_imagem} - {data} {hora}")

                        image = Image.open(io.BytesIO(imagem_blob))
                        image_np = np.array(image)

                        detections = {}
                        ausencia_detectada = False

                        for model_name, model in models.items():
                            results = model(image_np)

                            detected_classes = [
                                class_names[model_name][int(cls)]
                                for cls in results[0].boxes.cls.cpu().numpy()
                            ]

                            if any(cls.startswith("NO-") for cls in detected_classes):
                                ausencia_detectada = True

                            detections[model_name] = results
                            
                        processed_image = desenhar_boxes(image_np, detections)
                        img_io = io.BytesIO()
                        processed_image.save(img_io, format="JPEG")
                        img_blob = img_io.getvalue()

                        cursor.execute("""
                            INSERT INTO detectModel (data, hora, a_detect, imagem) 
                            VALUES (?, ?, ?, ?)
                        """, (data, hora, ausencia_detectada, img_blob))

                        banco.commit()
                        print(f"✅ Imagem processada e salva no banco (a_detect={ausencia_detectada}).")

        except sqlite3.Error as e:
            print(f"❌ Erro ao acessar o banco de dados: {e}")

        time.sleep(5)
        
# Função para obter o último ID já existente no banco
def obter_ultimo_id_detectModel():
    with sqlite3.connect(CameraConfig.DB_PATH, timeout=10) as banco:
        cursor = banco.cursor()
        cursor.execute("SELECT MAX(id) FROM detectModel")
        last_id = cursor.fetchone()[0] or 0
    return last_id

# Função para monitorar o ultimo alerta
def monitorar_alertas():
    last_id = obter_ultimo_id_detectModel()
    while True:
        try:
            with sqlite3.connect(CameraConfig.DB_PATH, timeout=10) as banco:
                cursor = banco.cursor()
                cursor.execute("SELECT MAX(id) FROM detectModel")
                max_detect_id = cursor.fetchone()[0] or 0

                if max_detect_id > last_id:
                    cursor.execute("SELECT id, data, hora, a_detect, imagem FROM detectModel WHERE id > ? AND a_detect = 1 ORDER BY id ASC", (last_id,))
                    novos_registros = cursor.fetchall()

                    for registro in novos_registros:
                        id_imagem, data, hora, a_detect, imagem_blob = registro
                        last_id = id_imagem

                        print(f"🚨 Alerta de EPI detectado! ID {id_imagem} - {data} {hora}")
                        enviar_alerta_email(data, hora, imagem_blob)

        except sqlite3.Error as e:
            print(f"❌ Erro ao acessar o banco de dados: {e}")

        time.sleep(5)

# Função para enviar e-mail de alerta
def enviar_alerta_email(data, hora, imagem_blob):
    try:
        image = Image.open(io.BytesIO(imagem_blob))
        image_filename = "detectModel_alarm.jpg"
        image.save(image_filename, format="JPEG")

        msg = MIMEMultipart()
        msg["From"] = EmailConfig.SENDER_EMAIL
        msg["To"] = EmailConfig.RECIPIENT_EMAIL
        msg["Subject"] = f"🚨 Alarme de EPI Detectado - {data} {hora}"

        msg.attach(MIMEText(f"""
            <h2>🚨 Alerta de Falta de EPI!</h2>
            <p><b>Data:</b> {data}</p>
            <p><b>Hora:</b> {hora}</p>
            <p>Foi detectada a ausência de um ou mais EPIs.</p>
            <p>Em anexo, a imagem processada com a detecção.</p>
        """, "html"))

        with open(image_filename, "rb") as img_file:
            msg.attach(MIMEImage(img_file.read(), name=image_filename))

        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(EmailConfig.SENDER_EMAIL, EmailConfig.SENDER_PASSWORD)
            server.sendmail(EmailConfig.SENDER_EMAIL, EmailConfig.RECIPIENT_EMAIL, msg.as_string())

        print(f"✅ E-mail de alerta enviado com sucesso! ({data} {hora})")

    except Exception as e:
        print(f"❌ Erro ao enviar o e-mail: {e}")

if __name__ == "__main__":
    threading.Thread(target=monitor_tripwire).start()
    threading.Thread(target=monitorar_e_salvar).start()
    threading.Thread(target=monitorar_alertas).start()