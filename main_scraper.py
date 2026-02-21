
import asyncio
import json
import os
import sys
import pandas as pd
import random
from scholar_scraper import get_scholar_authors
from researchgate_scraper import get_researchgate_authors
from social_searcher import analyze_researcher_social, get_sentiment

async def run_analysis():
    # Chargement des institutions
    if os.path.exists("institutions.json"):
        with open("institutions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            # On combine universités et centres de recherche
            targets = data.get("universities", []) + data.get("research_centers", [])
    else:
        targets = [{"name": "Université de l'Assomption au Congo", "researchgate": "https://www.researchgate.net/institution/Universite-de-lAssomption-au-Congo"}]

    print(f"Démarrage de l'extraction pour {len(targets)} institutions.")

    all_data = []

    for item in targets:
        inst_name = item["name"]
        rg_url = item.get("researchgate", inst_name)

        print(f"\n--- Collecte des données pour : {inst_name} ---")

        # Exécution séquentielle pour minimiser les risques de blocage IP
        print(f"Extraction Google Scholar...")
        scholar_results = await get_scholar_authors(inst_name, max_authors=5)
        await asyncio.sleep(random.uniform(5, 10)) # Pause entre les plateformes

        print(f"Extraction ResearchGate...")
        rg_results = await get_researchgate_authors(rg_url, max_authors=10)
        await asyncio.sleep(random.uniform(5, 10)) # Pause entre les institutions

        # Traitement Scholar
        for author in scholar_results:
            full_text = " ".join(author.get("publications", [])) + " " + " ".join(author.get("interests", []))
            sentiment = get_sentiment(full_text)
            social = analyze_researcher_social(author["name"], full_text)

            row = {
                "Nom": author["name"],
                "Institution": author["affiliation"],
                "Plateforme": "Google Scholar",
                "Lien": author["link"],
                "Interets": ", ".join(author["interests"]),
                "Donnees_Extraites": " | ".join(author["publications"]),
                "Sentiment_Analyse": sentiment,
                "Lien_Facebook": social["search_links"]["facebook_search"],
                "Lien_Blog": social["search_links"]["blog_search"]
            }
            all_data.append(row)

        # Traitement ResearchGate
        for author in rg_results:
            full_text = " ".join(author.get("info", []))
            sentiment = get_sentiment(full_text)
            social = analyze_researcher_social(author["name"], full_text)

            row = {
                "Nom": author["name"],
                "Institution": inst_name,
                "Plateforme": "ResearchGate",
                "Lien": author["link"],
                "Interets": "N/A",
                "Donnees_Extraites": " | ".join(author["info"]),
                "Sentiment_Analyse": sentiment,
                "Lien_Facebook": social["search_links"]["facebook_search"],
                "Lien_Blog": social["search_links"]["blog_search"]
            }
            all_data.append(row)

        if scholar_results or rg_results:
            print(f"-> {len(scholar_results) + len(rg_results)} chercheurs trouvés.")

    if not all_data:
        print("\nAucune donnée n'a pu être extraite automatiquement. Utilisez les scripts individuels pour le débogage.")
        return

    # Création du dataset
    df = pd.DataFrame(all_data)
    csv_file = "chercheurs_rdc_dataset.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")

    print(f"\nExtraction terminée. {len(all_data)} chercheurs sauvegardés dans {csv_file}")

if __name__ == "__main__":
    asyncio.run(run_analysis())
