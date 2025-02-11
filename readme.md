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
│── images/            
│── modelos/
│── scriptCams/
│── main.py
│── readme.md           
```

## Clone este repositório

```bash
https://github.com/AutvixCode/ac24007-atvx-yolo11-ppe-model.git
```

## Scripts

### 1. load_models

Esta função carrega os modelos treinados para a detecção de EPIs:

* Retorna um dicionário contendo três modelos YOLO carregados na GPU ou CPU

### 2. get_class_names

Esta função carrega as classes dos modelos

* Retorna um dicionário contendo as classes associadas a cada modelo.

### 3. draw_boxes

Esta função tem como objetivo montar as caixas de detencção con confidencia, classe e detecção

* Desenha as caixas delimitadoras ao redor dos objetos detectados.

### 4. Main

Esta função é a principal do script, com o intuito de capturar o video e realizar a interferencia em tempo real dos objetos detectados nas câmeras.
