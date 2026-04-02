
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
from openalex_extractor import get_drc_works, search_authors_by_name, get_author_works

async def run_analysis(local_files=None, specific_researchers=None):
    # Chargement des institutions
    if os.path.exists("institutions.json"):
        with open("institutions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            targets = data.get("universities", []) + data.get("research_centers", [])
    else:
        targets = [{"name": "Université de l'Assomption au Congo"}]

    all_data = []

    # 1. RECHERCHE DE CHERCHEURS SPÉCIFIQUES
    if specific_researchers:
        print("\n=== PHASE 0 : Recherche de chercheurs spécifiques ===")
        for name in specific_researchers:
            print(f"\n--- Recherche pour : {name} ---")

            # OpenAlex search
            oa_authors = search_authors_by_name(name)
            for oa_a in oa_authors:
                if oa_a['works_count'] > 0:
                    works = get_author_works(oa_a['works_api_url'])
                    for w in works:
                        all_data.append({
                            "Nom": oa_a['name'], "Institution": oa_a['affiliation'], "Plateforme": "OpenAlex (Profil)",
                            "Lien": w["DOI"], "Donnees_Extraites": f"{w['Titre']} - {w['Abstract']}",
                            "Sentiment_Analyse": w["Sentiment"]
                        })

            # Scholar Search
            scholar_results = await get_scholar_authors(name, max_authors=2)
            for author in scholar_results:
                text = " ".join(author.get("publications", [])) + " " + " ".join(author.get("interests", []))
                all_data.append({
                    "Nom": author["name"], "Institution": author["affiliation"], "Plateforme": "Google Scholar",
                    "Lien": author["link"], "Donnees_Extraites": text, "Sentiment_Analyse": get_sentiment(text)
                })

            # ResearchGate Search
            rg_results = await get_researchgate_authors(name, max_authors=2)
            for author in rg_results:
                text = " ".join(author.get("info", []))
                all_data.append({
                    "Nom": author["name"], "Institution": "N/A", "Plateforme": "ResearchGate",
                    "Lien": author["link"], "Donnees_Extraites": text, "Sentiment_Analyse": get_sentiment(text)
                })

    # 2. EXTRACTION VIA OPENALEX (Générale RDC)
    if not local_files:
        print("\n=== PHASE 1 : Extraction via OpenAlex (API Officielle) ===")
        oa_works = get_drc_works(max_works=300)
        for w in oa_works:
            all_data.append({
                "Nom": w["Auteurs_RDC"], "Institution": "RDC (Multi)", "Plateforme": "OpenAlex",
                "Lien": w["DOI"], "Donnees_Extraites": f"{w['Titre']} - {w['Abstract']}",
                "Sentiment_Analyse": w["Sentiment"]
            })

    # 3. EXTRACTION LOCALE
    if local_files:
        print("\n=== PHASE 2 : Analyse des fichiers locaux fournis ===")
        for file_path in local_files:
            if "scholar" in file_path.lower():
                results = await get_scholar_authors("Local", local_file=file_path)
            else:
                results = await get_researchgate_authors("Local", local_file=file_path)
            for author in results:
                text = " ".join(author.get("publications", [])) if "publications" in author else " ".join(author.get("info", []))
                all_data.append({
                    "Nom": author["name"], "Institution": author.get("affiliation", "N/A"),
                    "Plateforme": "Local File", "Lien": author["link"],
                    "Donnees_Extraites": text, "Sentiment_Analyse": get_sentiment(text)
                })

    if not all_data:
        print("\nAucune donnée n'a pu être extraite.")
        return

    # Sauvegarde finale
    df = pd.DataFrame(all_data)
    df = df.drop_duplicates(subset=["Nom", "Lien"])
    csv_file = "chercheurs_rdc_dataset_final.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    print(f"\nTerminé ! {len(df)} lignes sauvegardées dans '{csv_file}'.")

if __name__ == "__main__":
    # Paramètres par défaut
    researchers = ["Nsenge Mpia Héritier", "Kambale Kasambya Moïse"]

    args = sys.argv[1:]
    html_files = [a for a in args if a.endswith(".html")]

    # On permet de passer des noms de chercheurs comme arguments s'ils ne finissent pas par .html
    arg_researchers = [a for a in args if not a.endswith(".html") and not os.path.isdir(a)]
    if arg_researchers:
        researchers = arg_researchers

    if html_files:
        asyncio.run(run_analysis(local_files=html_files))
    else:
        asyncio.run(run_analysis(specific_researchers=researchers))
