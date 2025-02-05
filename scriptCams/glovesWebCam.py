import cv2
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Utilizando dispositivo: {device}")

model = torch.hub.load('ultralytics/yolov5', 'custom', path='modelos\gloves.pt').to(device)

classNames = ['Gloves', 'no-gloves']

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("Erro ao acessar a webcam. Verifique se está conectada.")
    exit()

print("Transmissão ao vivo iniciada com detecção de Óculos. Pressione 'q' para sair.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Não foi possível obter o frame da webcam.")
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

    cv2.imshow("Transmissão ao Vivo com Detecção de Óculos", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
