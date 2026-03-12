import os
from ultralytics import YOLO



# Paramètres


data_yaml   = "data/yolo/data.yaml"
model_base  = "yolov8s.pt"
epochs      = 100
image_size  = 480                   # 640 → 480 (moins de mémoire)
batch_size  = 4                     # 8 → 4 (moins de RAM)
projet      = "data/yolo/runs"
nom_run     = "f1_indicators"



# Chargement du modèle

model = YOLO(model_base)



# Entraînement

results = model.train(
    data      = data_yaml,
    epochs    = epochs,
    imgsz     = image_size,
    batch     = batch_size,
    project   = projet,
    name      = nom_run,
    exist_ok  = True,
    workers   = 2                   # limite les threads dataloader
)



# Résultat

print(f"✅ Entraînement terminé")
print(f"📁 Résultats dans : {projet}/{nom_run}")