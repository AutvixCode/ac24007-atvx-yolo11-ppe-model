import requests
import sqlite3
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
DB_PATH = "base.db"
ultimo_registro = 0

# 🔹 Função para salvar a imagem no banco de dados SQLite
def salvar_no_banco(data, hora, imagem_blob):
    try:
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO epi (data, hora, imagem) VALUES (?, ?, ?)
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

# 🔹 Iniciar o monitoramento
monitor_tripwire()
