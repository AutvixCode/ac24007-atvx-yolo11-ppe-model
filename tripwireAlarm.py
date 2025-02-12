import requests
from requests.auth import HTTPDigestAuth

USERNAME = "admin"
PASSWORD = "autvix123456"
IP_CAMERA = "192.168.1.108"
PORT = "80"

EVENT_URL = f"http://{IP_CAMERA}:{PORT}/cgi-bin/eventManager.cgi?action=attach&codes=[CrossLineDetection]"

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

        else:
            print(f"[ERRO] Falha na conexão com a câmera. Código HTTP: {response.status_code}")

    except Exception as e:
        print(f"[ERRO] Ocorreu um erro: {e}")

monitor_tripwire()
