import pandas as pd
import random

# Cette fonction génère un jeu de données synthétique pour les rapports de crise à Butembo
def generate_data():
    # Liste de lieux typiques à Butembo et environs
    locations = ["Vutsundo", "Furu", "Kangitsi", "Kyaghala", "Kavaghendi", "Mususa", "Bulengera", "Kimemi"]
    # Types d'incidents fréquents
    incidents = ["conflit armé", "incursion rebelle", "manifestation", "pillage", "incendie criminel"]
    # Groupes d'acteurs (anonymisés pour le modèle)
    actors = ["groupe armé inconnu", "milice locale", "forces de sécurité", "assaillants"]

    data = []
    # Nous générons 100 rapports pour cet exemple
    for i in range(100):
        loc = random.choice(locations)
        inc = random.choice(incidents)
        act = random.choice(actors)

        # Rapport en Français
        report_fr = f"Un {inc} a été signalé à {loc} impliquant un {act}."
        # Étiquetage NER simplifié (BIO format non utilisé pour simplifier, on cible les entités directement)
        entities_fr = {"LOC": loc, "INC": inc, "ACT": act}

        # Rapport en Swahili (Contexte local de Butembo)
        report_sw = f"Ghasia ya {inc} imeripotiwa {loc} na {act}."
        entities_sw = {"LOC": loc, "INC": inc, "ACT": act}

        data.append({"text": report_fr, "language": "fr", "LOC": loc, "INC": inc, "ACT": act})
        data.append({"text": report_sw, "language": "sw", "LOC": loc, "INC": inc, "ACT": act})

    # Création du DataFrame
    df = pd.DataFrame(data)
    # Sauvegarde en CSV
    df.to_csv("butembo_crisis_data.csv", index=False)
    print("Données générées avec succès dans 'butembo_crisis_data.csv'")

# Point d'entrée du script
if __name__ == "__main__":
    generate_data()
