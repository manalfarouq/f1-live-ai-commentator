#!/usr/bin/env python
# coding: utf-8

# In[20]:


import os
import shutil
import glob
import random


# In[21]:

images_raw  = "data/yolo/images/raw"
labels_raw  = "data/yolo/labels/raw"   

train_images = "data/yolo/images/train"
val_images   = "data/yolo/images/val"
train_labels = "data/yolo/labels/train"
val_labels   = "data/yolo/labels/val"

ratio_train = 0.8


# In[22]:


# Création des dossiers

for dossier in [train_images, val_images, train_labels, val_labels]:
    os.makedirs(dossier, exist_ok=True)



# In[23]:


# Chargement des images

images = glob.glob(os.path.join(images_raw, "*.png")) \
       + glob.glob(os.path.join(images_raw, "*.jpg"))

"""
On mélange aléatoirement les images avant de les séparer.
Comme ça, train et val ont une distribution équilibrée des classes.
"""
random.shuffle(images)



# Split train / val

split      = int(len(images) * ratio_train)
train_set  = images[:split]
val_set    = images[split:]



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

print(f"✅ Train : {len(train_set)} images")
print(f"✅ Val   : {len(val_set)} images")

