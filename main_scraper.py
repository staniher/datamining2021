
import asyncio
import json
import os
import sys
import pandas as pd
import random
import glob
from scholar_scraper import get_scholar_authors
from researchgate_scraper import get_researchgate_authors
from google_snippet_scraper import get_researchers_from_google
from social_searcher import analyze_researcher_social, get_sentiment
from openalex_extractor import get_drc_works

async def run_analysis(local_files=None, limit=2, use_openalex=True):
    # Chargement des institutions
    if os.path.exists("institutions.json"):
        with open("institutions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            targets = data.get("universities", []) + data.get("research_centers", [])
    else:
        targets = [{"name": "Université de l'Assomption au Congo"}]

    all_data = []

    # --- 1. OPTION OPENALEX (La plus fiable et recommandée) ---
    if use_openalex:
        print("\n=== PHASE 1 : Extraction via OpenAlex (API Officielle) ===")
        oa_works = get_drc_works(max_works=500) # Limite par défaut
        for w in oa_works:
            all_data.append({
                "Nom": w["Auteurs_RDC"],
                "Institution": "RDC (Multi)",
                "Plateforme": "OpenAlex",
                "Lien": w["DOI"],
                "Donnees_Extraites": f"{w['Titre']} - {w['Abstract']}",
                "Sentiment_Analyse": w["Sentiment"]
            })
        print(f"-> {len(oa_works)} publications récupérées via OpenAlex.")

    # --- 2. OPTION LOCALE (Fichiers HTML) ---
    if local_files:
        print("\n=== PHASE 2 : Analyse des fichiers locaux fournis ===")
        for file_path in local_files:
            if "scholar" in file_path.lower():
                results = await get_scholar_authors("Local", local_file=file_path)
                platform = "Google Scholar (Local)"
            else:
                results = await get_researchgate_authors("Local", local_file=file_path)
                platform = "ResearchGate (Local)"

            for author in results:
                text = " ".join(author.get("publications", [])) if "publications" in author else " ".join(author.get("info", []))
                all_data.append({
                    "Nom": author["name"], "Institution": author.get("affiliation", "N/A"),
                    "Plateforme": platform, "Lien": author["link"],
                    "Donnees_Extraites": text, "Sentiment_Analyse": get_sentiment(text)
                })

    # --- 3. OPTION EN LIGNE (Web Scraping - Si demandé explicitement ou si peu de données) ---
    if not local_files and len(all_data) < 10:
        print("\n=== PHASE 3 : Extraction Web (Scholar / ResearchGate) ===")
        for item in targets[:limit]:
            inst_name = item["name"]
            print(f"Extraction pour : {inst_name}...")

            # Essai direct
            scholar_results = await get_scholar_authors(inst_name, max_authors=3)
            rg_results = await get_researchgate_authors(item.get("researchgate", inst_name), max_authors=3)

            # Fallback Snippets
            if not scholar_results:
                snippets = await get_researchers_from_google(inst_name, platform="scholar.google.com")
                for s in snippets:
                    all_data.append({"Nom": s["name"], "Institution": inst_name, "Plateforme": s["source"], "Lien": s["link"], "Donnees_Extraites": s["snippet"], "Sentiment_Analyse": get_sentiment(s["snippet"])})

            if not rg_results:
                snippets = await get_researchers_from_google(inst_name, platform="researchgate.net")
                for s in snippets:
                    all_data.append({"Nom": s["name"], "Institution": inst_name, "Plateforme": s["source"], "Lien": s["link"], "Donnees_Extraites": s["snippet"], "Sentiment_Analyse": get_sentiment(s["snippet"])})

            # Résultats directs
            for author in scholar_results:
                text = " ".join(author.get("publications", [])) + " " + " ".join(author.get("interests", []))
                all_data.append({"Nom": author["name"], "Institution": author["affiliation"], "Plateforme": "Google Scholar", "Lien": author["link"], "Donnees_Extraites": text, "Sentiment_Analyse": get_sentiment(text)})

            for author in rg_results:
                text = " ".join(author.get("info", []))
                all_data.append({"Nom": author["name"], "Institution": inst_name, "Plateforme": "ResearchGate", "Lien": author["link"], "Donnees_Extraites": text, "Sentiment_Analyse": get_sentiment(text)})

    if not all_data:
        print("\nAucune donnée n'a pu être extraite.")
        return

    # Sauvegarde finale
    df = pd.DataFrame(all_data)
    df = df.drop_duplicates(subset=["Nom", "Lien"])

    csv_file = "chercheurs_rdc_dataset_final.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    print(f"\nTerminé ! {len(df)} chercheurs/publications sauvegardés dans '{csv_file}'.")

if __name__ == "__main__":
    args = sys.argv[1:]
    files = [a for a in args if a.endswith(".html") or os.path.isdir(a)]

    html_files = []
    for f in files:
        if os.path.isdir(f):
            html_files.extend(glob.glob(os.path.join(f, "*.html")))
        else:
            html_files.append(f)

    asyncio.run(run_analysis(local_files=html_files))
