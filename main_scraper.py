
import asyncio
import json
import os
import sys
import pandas as pd
from scholar_scraper import get_scholar_authors
from researchgate_scraper import get_researchgate_authors
from social_searcher import analyze_researcher_social, get_sentiment

async def run_analysis():
    # Chargement des institutions depuis le fichier JSON
    if os.path.exists("institutions.json"):
        with open("institutions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            # On récupère les noms des universités
            institutions = [inst["name"] for inst in data.get("universities", [])]
    else:
        # Valeur par défaut si le fichier est absent
        institutions = ["Université de Kinshasa"]

    print(f"Démarrage de l'extraction pour {len(institutions)} institutions.")

    all_data = []

    # Limitation pour la démonstration (2 premières institutions)
    for inst in institutions[:2]:
        print(f"\n--- Collecte des données pour : {inst} ---")

        # Lancement des scrapers en parallèle
        scholar_task = get_scholar_authors(inst, max_authors=5)
        rg_task = get_researchgate_authors(inst, max_authors=5)

        scholar_results, rg_results = await asyncio.gather(scholar_task, rg_task)

        # Traitement des résultats de Google Scholar
        for author in scholar_results:
            # On combine les publications et intérêts pour l'analyse de sentiment
            full_text = " ".join(author.get("publications", [])) + " " + " ".join(author.get("interests", []))
            sentiment = get_sentiment(full_text)

            # Préparation de la ligne pour le dataset
            row = {
                "Nom": author["name"],
                "Institution": author["affiliation"],
                "Plateforme": "Google Scholar",
                "Lien": author["link"],
                "Interets": ", ".join(author["interests"]),
                "Publications_Extraits": " | ".join(author["publications"]),
                "Sentiment_Analyse": sentiment
            }
            all_data.append(row)

        # Traitement des résultats de ResearchGate
        for author in rg_results:
            full_text = " ".join(author.get("info", []))
            sentiment = get_sentiment(full_text)

            row = {
                "Nom": author["name"],
                "Institution": inst,
                "Plateforme": "ResearchGate",
                "Lien": author["link"],
                "Interets": "N/A",
                "Publications_Extraits": " | ".join(author["info"]),
                "Sentiment_Analyse": sentiment
            }
            all_data.append(row)

    # Création du dataset avec Pandas
    df = pd.DataFrame(all_data)

    # Exportation en CSV et JSON
    csv_file = "chercheurs_rdc_dataset.csv"
    json_file = "chercheurs_rdc_dataset.json"

    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    df.to_json(json_file, orient="records", indent=2, force_ascii=False)

    print(f"\nExtraction terminée. {len(all_data)} chercheurs sauvegardés.")
    print(f"Dataset CSV : {csv_file}")
    print(f"Dataset JSON : {json_file}")

if __name__ == "__main__":
    asyncio.run(run_analysis())
