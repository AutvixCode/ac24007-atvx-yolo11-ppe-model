import cv2
import torch
import os
from ultralytics import YOLO

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Utilizando dispositivo: {device}")

models = {
    "gloves": YOLO('modelos/gloves.pt').to(device),
    "glasses": YOLO('modelos/glasses.pt').to(device),
    "ppe": YOLO('modelos/ppe.pt').to(device)
}

class_names = {
    "gloves": ['Gloves', 'No-Gloves'],
    "glasses": ['Glasses', 'No-Glasses'],
    "ppe": ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 'Person', 'Safety Cone',
            'Safety Vest', 'machinery', 'vehicle']
}

ppe_classes_permitidas = {'Safety Vest', 'NO-Safety Vest', 'Hardhat', 'NO-Hardhat', 'NO-Mask', 'Mask'}

image_folder = "imagens/"
if not os.path.exists(image_folder):
    print(f"Erro: A pasta {image_folder} não foi encontrada.")
    exit()

image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
if not image_files:
    print("Nenhuma imagem encontrada na pasta.")
    exit()

print(f"Detectando objetos em {len(image_files)} imagens...\n")

for image_file in image_files:
    image_path = os.path.join(image_folder, image_file)
    image = cv2.imread(image_path)

    if image is None:
        print(f"Erro ao carregar {image_file}, pulando...\n")
        continue

    print(f"📷 Imagem: {image_file}")

    for model_name, model in models.items():
        results = model(image)

        print(f"  🔍 Modelo: {model_name}")
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = round(float(box.conf[0].item()), 2)
                cls = int(box.cls[0].item())

                current_class = class_names[model_name][cls] if cls < len(class_names[model_name]) else f"Class {cls}"

                if model_name == "ppe" and current_class not in ppe_classes_permitidas:
                    continue

                color = (0, 0, 255) if "No-" in current_class or "NO-" in current_class else (0, 255, 0)

                print(f"    ✅ {current_class} | Confiança: {conf} | Caixa: ({x1}, {y1}, {x2}, {y2})")

                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                cv2.putText(image, f"{current_class} {conf}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    print("\n" + "-"*50 + "\n")

    cv2.imshow(f"Detecção - {image_file}", image)

cv2.waitKey(0)
cv2.destroyAllWindows()
