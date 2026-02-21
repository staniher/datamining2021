
import asyncio
import json
import os
import sys
import pandas as pd
import random
from scholar_scraper import get_scholar_authors
from researchgate_scraper import get_researchgate_authors
from google_snippet_scraper import get_researchers_from_google
from social_searcher import analyze_researcher_social, get_sentiment

async def run_analysis(local_scholar=None, local_rg=None):
    # Chargement des institutions
    if os.path.exists("institutions.json"):
        with open("institutions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            targets = data.get("universities", []) + data.get("research_centers", [])
    else:
        targets = [{"name": "Université de l'Assomption au Congo"}]

    all_data = []

    # Si des fichiers locaux sont fournis, on les traite en priorité
    if local_scholar or local_rg:
        print("\n=== Traitement des fichiers locaux fournis ===")
        if local_scholar:
            results = await get_scholar_authors("Local", local_file=local_scholar)
            for author in results:
                text = " ".join(author.get("publications", [])) + " " + " ".join(author.get("interests", []))
                all_data.append({"Nom": author["name"], "Institution": author["affiliation"], "Plateforme": "Google Scholar (Local)", "Lien": author["link"], "Donnees_Extraites": text, "Sentiment_Analyse": get_sentiment(text)})

        if local_rg:
            results = await get_researchgate_authors("Local", local_file=local_rg)
            for author in results:
                text = " ".join(author.get("info", []))
                all_data.append({"Nom": author["name"], "Institution": "N/A", "Plateforme": "ResearchGate (Local)", "Lien": author["link"], "Donnees_Extraites": text, "Sentiment_Analyse": get_sentiment(text)})
    else:
        # Sinon, exécution normale
        print(f"Démarrage de l'extraction automatique pour {len(targets)} institutions.")
        for item in targets[:3]:
            inst_name = item["name"]
            rg_url = item.get("researchgate", inst_name)
            print(f"\n--- Collecte pour : {inst_name} ---")

            scholar_results = await get_scholar_authors(inst_name, max_authors=3)
            rg_results = await get_researchgate_authors(rg_url, max_authors=3)

            if not scholar_results:
                snippets = await get_researchers_from_google(inst_name, platform="scholar.google.com")
                for s in snippets:
                    all_data.append({"Nom": s["name"], "Institution": inst_name, "Plateforme": s["source"], "Lien": s["link"], "Donnees_Extraites": s["snippet"], "Sentiment_Analyse": get_sentiment(s["snippet"])})

            if not rg_results:
                snippets = await get_researchers_from_google(inst_name, platform="researchgate.net")
                for s in snippets:
                    all_data.append({"Nom": s["name"], "Institution": inst_name, "Plateforme": s["source"], "Lien": s["link"], "Donnees_Extraites": s["snippet"], "Sentiment_Analyse": get_sentiment(s["snippet"])})

            for author in scholar_results:
                text = " ".join(author.get("publications", [])) + " " + " ".join(author.get("interests", []))
                all_data.append({"Nom": author["name"], "Institution": author["affiliation"], "Plateforme": "Google Scholar", "Lien": author["link"], "Donnees_Extraites": text, "Sentiment_Analyse": get_sentiment(text)})

            for author in rg_results:
                text = " ".join(author.get("info", []))
                all_data.append({"Nom": author["name"], "Institution": inst_name, "Plateforme": "ResearchGate", "Lien": author["link"], "Donnees_Extraites": text, "Sentiment_Analyse": get_sentiment(text)})

    if not all_data:
        print("\nAucune donnée n'a pu être extraite. Veuillez consulter SCRAPER_README.md pour utiliser le mode manuel.")
        return

    df = pd.DataFrame(all_data)
    df.to_csv("chercheurs_rdc_dataset.csv", index=False, encoding="utf-8-sig")
    print(f"\nTerminé. {len(all_data)} lignes sauvegardées dans chercheurs_rdc_dataset.csv.")

if __name__ == "__main__":
    s_file = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".html") else None
    r_file = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].endswith(".html") else None
    asyncio.run(run_analysis(local_scholar=s_file, local_rg=r_file))
