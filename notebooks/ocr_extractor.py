# notebooks/ocr_extractor.py

import cv2
import easyocr
from typing import List

reader = None

def init_reader():
    """Initialise le lecteur OCR une seule fois"""
    global reader
    if reader is None:
        reader = easyocr.Reader(['en'], gpu=False)
    return reader

def extract_text_from_image(image_path: str) -> List:
    """
    Extrait tout le texte d'une image F1
    """
    ocr_reader = init_reader()
    image = cv2.imread(image_path)
    results = ocr_reader.readtext(image, detail=1, paragraph=False)
    return results