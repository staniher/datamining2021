from sentence_transformers import SentenceTransformer
import torch
import numpy as np

# Cette classe définit notre engin de NER Zero-Shot basé sur SBERT
class ButemboNEREngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # Initialisation du modèle de sentences-transformers
        self.model = SentenceTransformer(model_name)
        # Définition des types d'entités (LOC=Lieu, INC=Incident, ACT=Acteur)
        self.entity_types = ["lieu", "conflit", "acteur armé"]
        # Descriptions pour l'approche zero-shot (similaire à OpenBioNER-v2)
        self.type_descriptions = {
            "lieu": "un emplacement géographique, quartier ou village dans Butembo",
            "conflit": "un événement violent, une incursion ou une manifestation",
            "acteur armé": "un groupe, une milice ou des forces de sécurité impliquées"
        }

    # Méthode pour extraire les entités en utilisant la similarité cosinus
    def extract_entities(self, text):
        # Encodage du texte d'entrée
        text_embedding = self.model.encode([text])
        # Encodage des descriptions de types pour le zero-shot
        type_embeddings = self.model.encode(list(self.type_descriptions.values()))

        # Calcul de la similarité cosinus (score de confiance)
        similarities = np.dot(text_embedding, type_embeddings.T) / (
            np.linalg.norm(text_embedding) * np.linalg.norm(type_embeddings, axis=1)
        )

        # On retourne le type avec le score maximum
        max_idx = np.argmax(similarities)
        return list(self.type_descriptions.keys())[max_idx], similarities[0][max_idx]

# Exemple d'utilisation rapide
if __name__ == "__main__":
    engine = ButemboNEREngine()
    ent, score = engine.extract_entities("Un conflit armé a été signalé à Kangitsi.")
    print(f"Entité prédite: {ent} (Score: {score:.4f})")
