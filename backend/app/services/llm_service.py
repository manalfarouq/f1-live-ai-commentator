# backend/app/services/llm_service.py

import google.generativeai as genai
import os

# Configurer Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')  


def generate_commentary(predictions_list):
    prompt = f"""Tu es un commentateur de Formule 1 passionné. 

Voici les prédictions du Top 3 pour cette course :

🥇 1er : {predictions_list[0]['driver']} ({predictions_list[0]['probability']:.1f}% de chances)
🥈 2ème : {predictions_list[1]['driver']} ({predictions_list[1]['probability']:.1f}% de chances)
🥉 3ème : {predictions_list[2]['driver']} ({predictions_list[2]['probability']:.1f}% de chances)

Génère un commentaire court (2-3 phrases) et enthousiaste sur ce podium prédit."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erreur lors de la génération du commentaire : {str(e)}"