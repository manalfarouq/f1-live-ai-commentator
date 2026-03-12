#!/usr/bin/env python
# coding: utf-8

import os
import shutil
import glob
import random


# Paramètres

images_raw  = "data/yolo/images/raw"
labels_raw  = "data/yolo/labels/raw"   

train_images = "data/yolo/images/train"
val_images   = "data/yolo/images/val"
train_labels = "data/yolo/labels/train"
val_labels   = "data/yolo/labels/val"

ratio_train = 0.8


# Nettoyage des dossiers existants

for dossier in [train_images, val_images, train_labels, val_labels]:
    shutil.rmtree(dossier, ignore_errors=True)
    os.makedirs(dossier)


# Chargement des images

images = glob.glob(os.path.join(images_raw, "*.png")) \
       + glob.glob(os.path.join(images_raw, "*.jpg"))


# Séparer annotées et backgrounds

def est_annotee(img):
    chemin = os.path.join(labels_raw, os.path.splitext(os.path.basename(img))[0] + ".txt")
    return os.path.exists(chemin) and os.path.getsize(chemin) > 0

annotees    = [img for img in images if est_annotee(img)]
backgrounds = [img for img in images if not est_annotee(img)]

# Shuffle séparé
random.shuffle(annotees)
random.shuffle(backgrounds)

# Split 80/20 sur chaque groupe séparément
def split_liste(lst):
    s = int(len(lst) * ratio_train)
    return lst[:s], lst[s:]

train_ann, val_ann = split_liste(annotees)
train_bg,  val_bg  = split_liste(backgrounds)

train_set = train_ann + train_bg
val_set   = val_ann   + val_bg


# Copie des fichiers

def copier(liste, dossier_images, dossier_labels):
    for img in liste:
        nom          = os.path.basename(img)
        nom_label    = os.path.splitext(nom)[0] + ".txt"
        chemin_label = os.path.join(labels_raw, nom_label)

        shutil.copy(img, os.path.join(dossier_images, nom))

        if os.path.exists(chemin_label):
            shutil.copy(chemin_label, os.path.join(dossier_labels, nom_label))

copier(train_set, train_images, train_labels)
copier(val_set,   val_images,   val_labels)


# Résultat

print(f"✅ Train : {len(train_set)} images ({len(train_ann)} annotées)")
print(f"✅ Val   : {len(val_set)} images ({len(val_ann)} annotées)")