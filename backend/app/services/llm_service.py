import google.generativeai as genai
import os

# Configurer Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')


def generate_commentary(predictions_list):
    """
    Génère un commentaire sur le Top 3 prédit
    
    Args:
        predictions_list: Liste de dict avec 'driver', 'probability', 'position'
        
    Returns:
        str: Commentaire généré par Gemini
    """
    
    # Créer le prompt
    prompt = f"""Tu es un commentateur de Formule 1 passionné. 

Voici les prédictions du Top 3 pour cette course :

🥇 1er : {predictions_list[0]['driver']} ({predictions_list[0]['probability']:.1f}% de chances)
🥈 2ème : {predictions_list[1]['driver']} ({predictions_list[1]['probability']:.1f}% de chances)
🥉 3ème : {predictions_list[2]['driver']} ({predictions_list[2]['probability']:.1f}% de chances)

Génère un commentaire court (2-3 phrases) et enthousiaste sur ce podium prédit.
Mentionne les pilotes et leurs chances de victoire."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erreur lors de la génération du commentaire : {str(e)}"