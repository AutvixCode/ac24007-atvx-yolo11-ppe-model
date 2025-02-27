import cv2
import torch
from ultralytics import YOLO

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Utilizando dispositivo: {device}")

model = YOLO('modelos/best copy.pt')

classNames = ['Gloves', 'no-gloves']

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("Erro ao acessar a webcam. Verifique se está conectada.")
    exit()

print("Transmissão ao vivo iniciada com detecção de Luvas. Pressione 'q' para sair.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Não foi possível obter o frame da webcam.")
        break

    results = model(frame)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = round(float(box.conf[0].item()), 2)
            cls = int(box.cls[0].item())
            currentClass = classNames[cls]

            color = (0, 255, 0) if 'no-' not in currentClass.lower() else (0, 0, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{currentClass} {conf}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow("Transmissão ao Vivo com Detecção de Luvas", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
