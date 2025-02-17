import cv2
import torch
from ultralytics import YOLO

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Utilizando dispositivo: {device}")

def load_models():
    return {
        "gloves": YOLO('modelos/gloves.pt').to(device),
        "glasses": YOLO('modelos/glasses.pt').to(device),
        "ppe": YOLO('modelos/ppe.pt').to(device)
    }

def get_class_names():
    return {
        "gloves": ['Gloves', 'No-Gloves'],
        "glasses": ['Glasses', 'No-Glasses'],
        "ppe": ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 'Person', 'Safety Cone',
                'Safety Vest', 'machinery', 'vehicle']
    }

PPE_ALLOWED_CLASSES = {'Safety Vest', 'NO-Safety Vest', 'Hardhat', 'NO-Hardhat', 'NO-Mask', 'Mask'}

def draw_boxes(frame, boxes, class_names, model_name):
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = round(float(box.conf[0].item()), 2)
        cls = int(box.cls[0].item())
        
        current_class = class_names[model_name][cls] if cls < len(class_names[model_name]) else f"Class {cls}"

        if model_name == "ppe" and current_class not in PPE_ALLOWED_CLASSES:
            continue
        
        color = (0, 0, 255) if "No-" in current_class or "NO-" in current_class else (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{current_class} {conf}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def main():
    models = load_models()
    class_names = get_class_names()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível acessar a webcam.")
        exit()
        
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar frame da webcam.")
            break
        
        for model_name, model in models.items():
            results = model(frame)
            for result in results:
                draw_boxes(frame, result.boxes, class_names, model_name)
        
        cv2.imshow("Detecção de EPI", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()