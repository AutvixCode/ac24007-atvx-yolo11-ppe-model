import requests
import sqlite3
import time
import threading
import io
import cv2
from datetime import datetime
from PIL import Image
from ultralytics import YOLO
from requests.auth import HTTPDigestAuth

# 🔹 Configurações da Câmera Dahua
USERNAME = "admin"
PASSWORD = "autvix123456"
IP_CAMERA = "192.168.1.108"
PORT = "80"
EVENT_URL = f"http://{IP_CAMERA}:{PORT}/cgi-bin/eventManager.cgi?action=attach&codes=[CrossLineDetection]"
SNAPSHOT_URL = f"http://{IP_CAMERA}:{PORT}/cgi-bin/snapshot.cgi"
DB_PATH = "base.db"
ultimo_registro = 0

# 🔹 Função para salvar a imagem no banco de dados SQLite
def salvar_no_banco(data, hora, imagem_blob):
    try:
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO tripwireAlarm (data, hora, imagem) VALUES (?, ?, ?)
        """, (data, hora, imagem_blob))

        conexao.commit()
        conexao.close()
        print("[✅] Imagem salva no banco de dados com sucesso.")

    except Exception as e:
        print(f"[ERRO] Falha ao salvar no banco: {e}")

# 🔹 Função para capturar um snapshot e salvar diretamente no banco
def capture_snapshot():
    global ultimo_registro

    tempo_atual = time.time()
    if tempo_atual - ultimo_registro < 20:
        print(f"[⏳] Aguardando {20} segundos antes de registrar outro evento...")
        return

    try:
        response = requests.get(SNAPSHOT_URL, auth=HTTPDigestAuth(USERNAME, PASSWORD), stream=True)

        if response.status_code == 200:
            data = datetime.now().strftime("%Y-%m-%d")
            hora = datetime.now().strftime("%H:%M:%S")

            imagem_blob = response.content

            salvar_no_banco(data, hora, imagem_blob)
            ultimo_registro = tempo_atual

        else:
            print(f"[ERRO] Falha ao capturar imagem. Código HTTP: {response.status_code}")

    except Exception as e:
        print(f"[ERRO] Ocorreu um erro ao capturar a imagem: {e}")

# 🔹 Função para monitorar alarmes de Tripwire
def monitor_tripwire():
    print("[INFO] Conectando à câmera Dahua para monitorar alarmes de Tripwire...")

    try:
        response = requests.get(EVENT_URL, auth=HTTPDigestAuth(USERNAME, PASSWORD), stream=True)

        if response.status_code == 200:
            print("[INFO] Conexão estabelecida! Monitorando eventos de Tripwire...\n")

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')

                    if "Code=CrossLineDetection" in decoded_line:
                        print(f"[ALERTA 🚨] Tripwire ativado! 📍 {decoded_line}")

                        capture_snapshot()

        else:
            print(f"[ERRO] Falha na conexão com a câmera. Código HTTP: {response.status_code}")

    except Exception as e:
        print(f"[ERRO] Ocorreu um erro: {e}")

# 🔹 Função para monitorar imagens e processar com YOLOv11
def monitorar_e_salvar():
    model = YOLO("modelos/ppe.pt")

    banco = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES, timeout=10)
    cursor = banco.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detectModel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE,
            hora DATETIME,
            imagem BLOB
        )
    """)
    banco.commit()

    cursor.execute("SELECT MAX(id) FROM tripwireAlarm")
    last_id = cursor.fetchone()[0] or 0

    print(f"📡 Monitorando novas imagens... Último ID: {last_id}")

    while True:
        cursor.execute("SELECT id, data, hora, imagem FROM tripwireAlarm WHERE id > ?", (last_id,))
        novas_imagens = cursor.fetchall()

        if novas_imagens:
            for id_imagem, data, hora, imagem_blob in novas_imagens:
                last_id = id_imagem

                image = Image.open(io.BytesIO(imagem_blob)).convert("RGB")
                results = model(image)
                detected_objects = [model.names.get(int(box.cls), f"Classe-{int(box.cls)}") for box in results[0].boxes]

                print(f"📷 Imagem {id_imagem}: Objetos detectados -> {detected_objects}")

                if any(obj.lower().startswith("no-") for obj in detected_objects):
                    print(f"Ausência de objeto detectada na imagem {id_imagem}")

                    result_img = results[0].plot()
                    result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
                    result_pil = Image.fromarray(result_img)

                    img_byte_arr = io.BytesIO()
                    result_pil.save(img_byte_arr, format='JPEG')
                    image_blob = img_byte_arr.getvalue()

                    try:
                        cursor.execute("INSERT INTO detectModel (data, hora, imagem) VALUES (?, ?, ?)", 
                                       (data, hora, sqlite3.Binary(image_blob)))
                        banco.commit()
                        print(f"✅ Imagem {id_imagem} com detecções salva no banco.")
                    except sqlite3.Error as e:
                        print(f"⚠️ Erro ao salvar no banco: {e}")

        time.sleep(5)

# 🔹 Rodar ambas as funções ao mesmo tempo
if __name__ == "__main__":
    thread1 = threading.Thread(target=monitor_tripwire)
    thread2 = threading.Thread(target=monitorar_e_salvar)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
