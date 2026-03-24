import chromadb
from backend.app.services.rag.augment import generer_commentaire 

client = chromadb.PersistentClient(path="data/rag/chroma_db")
collection = client.get_or_create_collection(name="f1_knowledge")

# 2. Base de connaissances F1 XXL (30 documents)
documents = [
    "Leclerc prend l'avantage au virage 3 grâce à un freinage tardif.",
    "Verstappen tente l'undercut au tour 15 pour passer devant Perez.",
    "Alerte météo : la pluie arrive sur le secteur 3, pneus intermédiaires conseillés.",
    "Hamilton économise ses gommes hard pour un long relais final.",
    "DRS activé pour Norris qui revient à moins d'une seconde de Sainz.",
    "Ocon et Gasly sont à la lutte pour la 8ème place, contact évité de justesse.",
    "Red Bull domine le secteur 2 avec une vitesse de pointe impressionnante.",
    "Drapeau jaune : Sargeant est à l'arrêt dans l'échappatoire du virage 10.",
    "Arrêt aux stands record pour Ferrari : 2.1 secondes pour Leclerc.",
    "Alonso se plaint d'une perte de puissance moteur sur la radio.",
    "La voiture de sécurité (Safety Car) entre en piste après le crash de Stroll.",
    "Russell tente un dépassement par l'extérieur au virage 1, ça passe !",
    "Piastri réalise le meilleur tour en course avec les pneus softs neufs.",
    "Stratégie risquée pour Mercedes qui tente un seul arrêt contre deux pour les autres.",
    "Hülkenberg reçoit une pénalité de 5 secondes pour avoir dépassé les limites de piste.",
    "Magnussen défend agressivement sa position face à Albon dans la chicane.",
    "Température de piste en hausse : 45°C, dégradation accélérée des pneus soft.",
    "Vibrations signalées par Ricciardo sur son train avant gauche.",
    "Le 'Plan B' est activé pour Carlos Sainz suite à l'usure précoce des gommes.",
    "Dépassement audacieux de Bearman dans le tunnel, il gagne deux places.",
    "Vent de face violent dans la ligne droite principale, impact sur la vitesse de pointe.",
    "L'aileron arrière de la Haas semble endommagé après un léger contact.",
    "Tsunoda est sous enquête des commissaires pour avoir coupé la ligne de sortie des stands.",
    "Hamilton demande à son ingénieur : 'Is the floor okay?', il craint des dégâts.",
    "Bataille à trois entre Aston Martin, McLaren et Mercedes pour le podium.",
    "Bottas tente l'overcut en restant en piste 5 tours de plus que ses concurrents.",
    "Panne de DRS pour la Williams de Colapinto, il est sans défense en ligne droite.",
    "Ferrari demande à Leclerc de changer de mode moteur pour économiser du carburant.",
    "Drapeau bleu pour Zhou qui doit laisser passer le leader Verstappen.",
    "L'adhérence est très faible hors de la trajectoire idéale à cause des débris."
]

# 3. Ajout propre (on vide d'abord pour éviter les doublons si tu relances le script)
collection.add(
    documents=documents,
    ids=[f"doc_{i}" for i in range(len(documents))]
)

print(f"✅ {collection.count()} documents chargés dans la base de connaissances.")

# 4. Test avec une situation complexe
race_data = {
    "lap": 42, 
    "drivers": ["Leclerc", "Hamilton"], 
    "event": "Pluie fine signalée",
    "tyre_type": "medium"
}

# Si ça affiche encore "Commentaire en attente", c'est dans augment.py qu'il faut regarder !
resultat = generer_commentaire(race_data, persona="journaliste")
print("\nCommentaire généré :\n", resultat.get("commentaire", "Erreur : toujours pas de texte !"))