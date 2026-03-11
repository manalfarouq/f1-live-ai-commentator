import os
from ultralytics import YOLO



# Paramètres


data_yaml   = "data/yolo/data.yaml"
model_base  = "yolov8n.pt"         
epochs      = 50
image_size  = 640
batch_size  = 8
projet      = "data/yolo/runs"
nom_run     = "f1_indicators"



# Chargement du modèle

"""
On part de yolov8n.pt (nano = le plus léger).
Il est déjà dans notebooks/ depuis le projet,
on le copie ici ou on le laisse se télécharger automatiquement.
"""
model = YOLO(model_base)



# Entraînement

results = model.train(
    data      = data_yaml,
    epochs    = epochs,
    imgsz     = image_size,
    batch     = batch_size,
    project   = projet,
    name      = nom_run,
    exist_ok  = True
)



# Résultat

print(f"✅ Entraînement terminé")
print(f"📁 Résultats dans : {projet}/{nom_run}")