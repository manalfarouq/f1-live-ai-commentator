# backend/app/routes/f1_data_router.py

from fastapi import APIRouter, UploadFile, File
import shutil

router = APIRouter(prefix="/f1-data", tags=["F1 Data"])


@router.get("/test")
async def test_endpoint():
    return {"status": "F1 Data Router OK 🏎️"}


@router.post("/debug")
async def debug_ocr(file: UploadFile = File(...)):
    """
    Debug : voir tout ce que l'OCR détecte
    """
    import sys
    import os
    
    notebooks_path = '/app/notebooks'
    if notebooks_path not in sys.path:
        sys.path.insert(0, notebooks_path)
    
    try:
        from reconnaissance_dobjets import extract_text_from_image
    except Exception as e:
        return {"error": f"Import failed: {str(e)}"}
    
    os.makedirs("data/images", exist_ok=True)
    temp_path = f"data/images/temp_{file.filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extraire TOUT le texte détecté
        ocr_results = extract_text_from_image(temp_path)
        
        # Formater pour affichage
        debug_data = []
        for (bbox, text, prob) in ocr_results:
            debug_data.append({
                "text": text,
                "confidence": round(prob, 2),
                "y_position": int(bbox[0][1])
            })
        
        # Trier par position Y pour voir l'ordre
        debug_data.sort(key=lambda x: x['y_position'])
        
        return {
            "total_detected": len(debug_data),
            "all_text": debug_data
        }
    
    except Exception as e:
        return {"error": str(e)}
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/extract")
async def extract_f1_data(file: UploadFile = File(...)):
    """
    Upload une image et extrait les données F1
    """
    import sys
    import os
    
    notebooks_path = '/app/notebooks'
    
    if notebooks_path not in sys.path:
        sys.path.insert(0, notebooks_path)
    
    try:
        from reconnaissance_dobjets import get_f1_data, save_data_to_dict
    except Exception as e:
        return {"error": f"Import failed: {str(e)}"}
    
    os.makedirs("data/images", exist_ok=True)
    temp_path = f"data/images/temp_{file.filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        drivers = get_f1_data(temp_path)
        result = save_data_to_dict(drivers)
        
        return result
    
    except Exception as e:
        return {"error": str(e)}
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)