import cv2
import torch
from ultralytics import YOLO

username = "admin"
password = "autvix123456"
ip_camera = "192.168.1.108"
port = "554"
rtsp_url = f"rtsp://{username}:{password}@{ip_camera}:{port}/cam/realmonitor?channel=1&subtype=0"

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Utilizando dispositivo: {device}")

model = YOLO('modelos/glasses.pt').to(device)

classNames = ['Glasses, no-Glasses']

cap = cv2.VideoCapture(rtsp_url)

cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("Erro ao conectar à câmera. Verifique as configurações.")
    exit()

print("Transmissão ao vivo iniciada com detecção de Oculos. Pressione 'q' para sair.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Não foi possível obter o frame da câmera.")
        break

    results = model(frame)

    for result in results.xyxy[0].cpu().numpy():
        x1, y1, x2, y2, conf, cls = result
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        conf = round(float(conf), 2)
        cls = int(cls)
        currentClass = classNames[cls]

        color = (0, 255, 0) if 'NO-' not in currentClass else (0, 0, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{currentClass} {conf}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow("Transmissão ao Vivo com Detecção de Oculos", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
