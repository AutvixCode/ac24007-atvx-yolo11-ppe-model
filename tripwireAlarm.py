import requests
import os
import time
from datetime import datetime
from requests.auth import HTTPDigestAuth

# 🔹 Configurações da Câmera Dahua
USERNAME = "admin"
PASSWORD = "autvix123456"
IP_CAMERA = "192.168.1.108"
PORT = "80"
EVENT_URL = f"http://{IP_CAMERA}:{PORT}/cgi-bin/eventManager.cgi?action=attach&codes=[CrossLineDetection]"
SNAPSHOT_URL = f"http://{IP_CAMERA}:{PORT}/cgi-bin/snapshot.cgi"
FOLDER_PATH = "fotos"

if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)

def capture_snapshot():
    try:
        response = requests.get(SNAPSHOT_URL, auth=HTTPDigestAuth(USERNAME, PASSWORD), stream=True)

        if response.status_code == 200:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_path = os.path.join(FOLDER_PATH, f"tripwire_{timestamp}.jpg")

            with open(file_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            print(f"[📸] Imagem salva: {file_path}")
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

# 🔹 Iniciar o monitoramento
monitor_tripwire()
