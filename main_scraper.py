
import asyncio
import json
import os
import sys
from scholar_scraper import get_scholar_authors
from researchgate_scraper import get_researchgate_authors
from social_searcher import analyze_researcher_social, get_sentiment

async def run_analysis():
    # Load institutions
    if os.path.exists("institutions.json"):
        with open("institutions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            institutions = [inst["name"] for inst in data.get("universities", [])]
    else:
        institutions = ["Université de Kinshasa"]

    print(f"Démarrage de l'analyse pour {len(institutions)} institutions.")

    all_results = []

    # Pour la démo, on limite aux 2 premières institutions
    for inst in institutions[:2]:
        print(f"\n--- Analyse de : {inst} ---")

        # Scraping asynchrone
        scholar_task = get_scholar_authors(inst, max_authors=3)
        rg_task = get_researchgate_authors(inst, max_authors=3)

        scholar_results, rg_results = await asyncio.gather(scholar_task, rg_task)

        # Traitement et Analyse de Sentiment
        for author in scholar_results:
            # Analyse sur les publications (plus de contenu)
            full_text = " ".join(author.get("publications", [])) + " " + " ".join(author.get("interests", []))
            author["sentiment"] = get_sentiment(full_text)
            author.update(analyze_researcher_social(author["name"], full_text))
            all_results.append(author)

        for author in rg_results:
            full_text = " ".join(author.get("info", []))
            author["sentiment"] = get_sentiment(full_text)
            author.update(analyze_researcher_social(author["name"], full_text))
            all_results.append(author)

    # Exportation
    output_file = "rapport_final_chercheurs.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nAnalyse terminée. {len(all_results)} chercheurs exportés dans {output_file}")

if __name__ == "__main__":
    asyncio.run(run_analysis())
