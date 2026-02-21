
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

async def run_analysis(local_files=None, limit=3):
    # Chargement des institutions
    if os.path.exists("institutions.json"):
        with open("institutions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            targets = data.get("universities", []) + data.get("research_centers", [])
    else:
        targets = [{"name": "Université de l'Assomption au Congo"}]

    all_data = []

    # MODE LOCAL : Traitement des fichiers HTML fournis ou présents dans 'imports/'
    if local_files:
        print("\n=== MODE LOCAL : Analyse des fichiers fournis ===")
        for file_path in local_files:
            print(f"Fichier : {file_path}")
            if "scholar" in file_path.lower():
                results = await get_scholar_authors("Local", local_file=file_path)
                platform = "Google Scholar (Local)"
            else:
                results = await get_researchgate_authors("Local", local_file=file_path)
                platform = "ResearchGate (Local)"

            for author in results:
                text = " ".join(author.get("publications", [])) if "publications" in author else " ".join(author.get("info", []))
                sentiment = get_sentiment(text)
                all_data.append({
                    "Nom": author["name"], "Institution": author.get("affiliation", "N/A"),
                    "Plateforme": platform, "Lien": author["link"],
                    "Donnees_Extraites": text, "Sentiment_Analyse": sentiment
                })

    # MODE EN LIGNE : Si aucun fichier local n'est spécifié
    else:
        print(f"\n=== MODE EN LIGNE : Extraction pour {len(targets)} institutions ===")
        # On limite le nombre d'institutions pour éviter les blocages IP massifs
        for item in targets[:limit]:
            inst_name = item["name"]
            rg_url = item.get("researchgate", inst_name)
            print(f"\n--- Travail sur : {inst_name} ---")

            # 1. Tentatives directes (avec délais)
            scholar_results = await get_scholar_authors(inst_name, max_authors=3)
            await asyncio.sleep(random.uniform(2, 5))
            rg_results = await get_researchgate_authors(rg_url, max_authors=3)

            # 2. Fallbacks si bloqué
            if not scholar_results:
                print("   [!] Scholar bloqué ou vide. Utilisation du fallback Google...")
                snippets = await get_researchers_from_google(inst_name, platform="scholar.google.com")
                for s in snippets:
                    all_data.append({
                        "Nom": s["name"], "Institution": inst_name, "Plateforme": s["source"],
                        "Lien": s["link"], "Donnees_Extraites": s["snippet"], "Sentiment_Analyse": get_sentiment(s["snippet"])
                    })

            if not rg_results:
                print("   [!] ResearchGate bloqué ou vide. Utilisation du fallback Google...")
                snippets = await get_researchers_from_google(inst_name, platform="researchgate.net")
                for s in snippets:
                    all_data.append({
                        "Nom": s["name"], "Institution": inst_name, "Plateforme": s["source"],
                        "Lien": s["link"], "Donnees_Extraites": s["snippet"], "Sentiment_Analyse": get_sentiment(s["snippet"])
                    })

            # 3. Ajout des résultats directs réussis
            for author in scholar_results:
                text = " ".join(author.get("publications", [])) + " " + " ".join(author.get("interests", []))
                all_data.append({
                    "Nom": author["name"], "Institution": author["affiliation"], "Plateforme": "Google Scholar",
                    "Lien": author["link"], "Donnees_Extraites": text, "Sentiment_Analyse": get_sentiment(text)
                })

            for author in rg_results:
                text = " ".join(author.get("info", []))
                all_data.append({
                    "Nom": author["name"], "Institution": inst_name, "Plateforme": "ResearchGate",
                    "Lien": author["link"], "Donnees_Extraites": text, "Sentiment_Analyse": get_sentiment(text)
                })

            print(f"   -> {len(all_data)} chercheurs collectés jusqu'à présent.")
            await asyncio.sleep(random.uniform(10, 20)) # Grande pause entre institutions

    if not all_data:
        print("\n[ERREUR] Aucune donnée n'a pu être extraite.")
        print("CONSEIL : Ouvrez ResearchGate dans votre navigateur, résolvez le captcha, enregistrez la page HTML et relancez avec le fichier.")
        return

    # Sauvegarde finale
    df = pd.DataFrame(all_data)
    # Suppression des doublons basés sur le nom et le lien
    df = df.drop_duplicates(subset=["Nom", "Lien"])

    csv_file = "chercheurs_rdc_dataset.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    print(f"\nExtraction terminée ! {len(df)} chercheurs uniques sauvegardés dans '{csv_file}'.")

if __name__ == "__main__":
    # Vérification si des arguments sont des fichiers HTML ou des dossiers
    args = sys.argv[1:]
    files_to_parse = []

    for arg in args:
        if arg.endswith(".html") and os.path.exists(arg):
            files_to_parse.append(arg)
        elif os.path.isdir(arg):
            files_to_parse.extend(glob.glob(os.path.join(arg, "*.html")))

    # Si on trouve des fichiers HTML, on lance en mode local
    if files_to_parse:
        asyncio.run(run_analysis(local_files=files_to_parse))
    else:
        # Sinon mode automatique
        asyncio.run(run_analysis())
