# YOLO11 PPE Model

Este repositório contém um modelo baseado no **YOLO11** para detecção de Equipamentos de Proteção Individual (EPI), realizando a integração de vários modelos ja treinados. O objetivo é garantir a segurança em ambientes industriais, identificando automaticamente se os trabalhadores estão utilizando os EPIs obrigatórios.

## Características

* Baseado na arquitetura YOLOv11
* Treinado para detectar óculos em imagens
* Suporte para inferência em tempo real
* Código otimizado para GPU

## Estrutura do Repositório

```bash
yolo11_ppe_model/
│── modelos/
│── scriptCams/
│── database/
│── tripwireAlarm.py
│── readme.md           
```

## Clone este repositório

```bash
https://github.com/AutvixCode/ac24007-atvx-yolo11-ppe-model.git
```

## Scripts

* **Monitoramento de Tripwire:** Detecta eventos de cruzamento de linha na câmera Dahua.
* **Captura de Imagens:** Quando um evento de Tripwire ocorre, a imagem é capturada automaticamente.
* **Armazenamento no Banco de Dados:** As imagens capturadas são salvas em um banco de dados SQLite.
* **Processamento com YOLO:** As imagens são analisadas por modelos YOLO para detecção de EPIs.
* **Detecção de Ausência de EPI:** Caso um trabalhador não esteja utilizando EPI adequado, um alerta é gerado.
* **Notificação via E-mail:** Envio automático de e-mails em caso de ausência de EPI.

## Configurações

### Configuração da câmera

```python
class CameraConfig:
    USERNAME = "admin"
    PASSWORD = "sua_senha"
    IP_CAMERA = "192.168.1.108"
    PORT = "80"
```

### Configuração de email para envio

```python
class EmailConfig:
    SENDER_EMAIL = "seu_email@example.com"
    SENDER_PASSWORD = "sua_senha"
    RECIPIENT_EMAIL = "destinatario@example.com"
```

### Configuração de Banco de Dados

```Sql
CREATE TABLE tripwireAlarm (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE,
    hora DATETIME,
    imagem BLOB
);

CREATE TABLE detectModel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE,
    hora DATETIME,
    a_detect BOOLEAN,
    imagem BLOB
);
```
