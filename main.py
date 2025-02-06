import cv2
import torch
import os
import pandas as pd
from ultralytics import YOLO

# Configuração do dispositivo (GPU ou CPU)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Utilizando dispositivo: {device}")

# Carregamento dos modelos
models = {
    "gloves": YOLO('modelos/gloves.pt').to(device),
    "glasses": YOLO('modelos/glasses.pt').to(device),
    "ppe": YOLO('modelos/ppe.pt').to(device)
}

# Classes para cada modelo
class_names = {
    "gloves": ['Gloves', 'No-Gloves'],
    "glasses": ['Glasses', 'No-Glasses'],
    "ppe": ['Helmet', 'Vest', 'mask']
}

# Pasta de imagens
image_folder = "imagens/"
output_csv = "result.csv"
results_list = []

# Verifica se a pasta existe
if not os.path.exists(image_folder):
    print(f"Erro: A pasta {image_folder} não foi encontrada.")
    exit()

# Lista todas as imagens na pasta
image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]

if not image_files:
    print("Nenhuma imagem encontrada na pasta.")
    exit()

print(f"Detectando objetos em {len(image_files)} imagens...")

# Processa cada imagem
for image_file in image_files:
    image_path = os.path.join(image_folder, image_file)
    image = cv2.imread(image_path)

    if image is None:
        print(f"Erro ao carregar {image_file}, pulando...")
        continue

    detections = []

    # Passa a imagem por cada modelo
    for model_name, model in models.items():
        results = model(image)

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = round(float(box.conf[0].item()), 2)
                cls = int(box.cls[0].item())
                current_class = class_names[model_name][cls] if cls < len(class_names[model_name]) else f"Class {cls}"

                # Salva a detecção no CSV
                results_list.append([image_file, model_name, current_class, conf, x1, y1, x2, y2])

                # Define cor (verde se detectado corretamente, vermelho se for "No-")
                color = (0, 255, 0) if 'No-' not in current_class else (0, 0, 255)

                # Desenha a caixa na imagem
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                cv2.putText(image, f"{current_class} {conf}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Exibe a imagem com detecção
    cv2.imshow("Detecção", image)
    cv2.waitKey(500)  # Mostra a imagem por meio segundo antes de ir para a próxima

cv2.destroyAllWindows()

# Salva os resultados no CSV
df = pd.DataFrame(results_list, columns=["Imagem", "Modelo", "Objeto Detectado", "Confiança", "x1", "y1", "x2", "y2"])
df.to_csv(output_csv, index=False)
print(f"Detecções salvas em {output_csv}")


print(df.head)