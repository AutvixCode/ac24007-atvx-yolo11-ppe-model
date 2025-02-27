import cv2
import torch
from ultralytics import YOLO

# Configuração da câmera IP
username = "admin"
password = "autvix123456"
ip_camera = "192.168.1.108"
port = "554"
rtsp_url = f"rtsp://{username}:{password}@{ip_camera}:{port}/cam/realmonitor?channel=1&subtype=0"

# Configuração do dispositivo (CPU ou GPU)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Utilizando dispositivo: {device}")

# Carregar modelo treinado
model = YOLO('modelos/best.pt').to(device)

# Classes do modelo
classNames = ['Gloves', 'no-gloves']

# Abrir conexão com a câmera
cap = cv2.VideoCapture(rtsp_url)

# Definir propriedades da câmera
cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Verificar se a conexão foi bem-sucedida
if not cap.isOpened():
    print("Erro ao conectar à câmera. Verifique as configurações.")
    exit()

print("Transmissão ao vivo iniciada com detecção de Luvas. Pressione 'q' para sair.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Não foi possível obter o frame da câmera.")
        break

    # Realizar a inferência com o modelo YOLO
    results = model(frame)  # Retorna uma lista de objetos `Results`

    for result in results:  # Iterar sobre a lista de resultados
        for box in result.boxes:  # Acessar cada caixa detectada
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # Coordenadas da bounding box
            conf = round(float(box.conf[0].item()), 2)  # Confiança da predição
            cls = int(box.cls[0].item())  # Índice da classe predita
            currentClass = classNames[cls]  # Nome da classe

            # Definir cor com base na classe detectada
            color = (0, 255, 0) if 'no-' not in currentClass.lower() else (0, 0, 255)

            # Desenhar bounding box e label no frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{currentClass} {conf}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Exibir o vídeo com as detecções
    cv2.imshow("Transmissão ao Vivo com Detecção de Luvas", frame)

    # Pressione 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos da câmera e fechar janelas
cap.release()
cv2.destroyAllWindows()
